import { 
  users, 
  subscriptions, 
  payments, 
  botSessions,
  type User, 
  type InsertUser, 
  type Subscription, 
  type InsertSubscription,
  type Payment,
  type InsertPayment,
  type BotSession
} from "@shared/schema";
import { eq, and, desc, gte } from "drizzle-orm";
import { drizzle } from "drizzle-orm/neon-serverless";
import { neon } from "@neondatabase/serverless";
import bcrypt from "bcryptjs";
import crypto from "crypto";

const sql = neon(process.env.DATABASE_URL!);
const db = drizzle(sql);

export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  authenticateUser(username: string, password: string): Promise<User | null>;
  updateUserLastLogin(id: number): Promise<void>;
  getAllUsers(): Promise<(User & { subscription?: Subscription })[]>;
  deleteUser(id: number): Promise<void>;

  // Subscription methods
  createSubscription(subscription: InsertSubscription): Promise<Subscription>;
  getUserSubscription(userId: number): Promise<Subscription | undefined>;
  getActiveSubscription(userId: number): Promise<Subscription | undefined>;
  getUserSubscriptionByLicense(licenseKey: string): Promise<Subscription | undefined>;
  extendSubscription(userId: number, days: number): Promise<void>;
  updateSubscriptionStatus(id: number, status: string): Promise<void>;
  getExpiringSubscriptions(days: number): Promise<Subscription[]>;

  // Payment methods
  createPayment(payment: InsertPayment): Promise<Payment>;
  getPayment(id: number): Promise<Payment | undefined>;
  updatePaymentStatus(id: number, status: string): Promise<void>;
  getUserPayments(userId: number): Promise<Payment[]>;

  // Bot session methods
  createBotSession(userId: number): Promise<BotSession>;
  updateBotSession(id: number, fishCaught: number, skillsUsed: number): Promise<void>;
  endBotSession(id: number): Promise<void>;
  getUserSessions(userId: number): Promise<BotSession[]>;

  // Admin methods
  getSystemStats(): Promise<{
    totalUsers: number;
    activeSubscriptions: number;
    monthlyRevenue: number;
    newUsersThisMonth: number;
  }>;
}

function generateLicenseKey(): string {
  return crypto.randomBytes(16).toString('hex').toUpperCase().match(/.{1,4}/g)!.join('-');
}

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.id, id)).limit(1);
    return result[0];
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.username, username)).limit(1);
    return result[0];
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.email, email)).limit(1);
    return result[0];
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const hashedPassword = await bcrypt.hash(insertUser.password, 10);
    const result = await db.insert(users).values({
      ...insertUser,
      password: hashedPassword,
    }).returning();
    return result[0];
  }

  async authenticateUser(username: string, password: string): Promise<User | null> {
    const user = await this.getUserByUsername(username) || await this.getUserByEmail(username);
    if (!user) return null;

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) return null;

    await this.updateUserLastLogin(user.id);
    return user;
  }

  async updateUserLastLogin(id: number): Promise<void> {
    await db.update(users).set({ lastLogin: new Date() }).where(eq(users.id, id));
  }

  async getAllUsers(): Promise<(User & { subscription?: Subscription })[]> {
    const result = await db
      .select()
      .from(users)
      .leftJoin(subscriptions, and(
        eq(subscriptions.userId, users.id),
        eq(subscriptions.status, 'active')
      ))
      .orderBy(desc(users.createdAt));

    return result.map(row => ({
      ...row.users,
      subscription: row.subscriptions || undefined
    }));
  }

  async deleteUser(id: number): Promise<void> {
    // Delete related records first
    await db.delete(botSessions).where(eq(botSessions.userId, id));
    await db.delete(payments).where(eq(payments.userId, id));
    await db.delete(subscriptions).where(eq(subscriptions.userId, id));
    await db.delete(users).where(eq(users.id, id));
  }

  async createSubscription(subscription: InsertSubscription): Promise<Subscription> {
    const result = await db.insert(subscriptions).values({
      ...subscription,
      status: 'active',
      licenseKey: generateLicenseKey(),
    }).returning();
    return result[0];
  }

  async getUserSubscription(userId: number): Promise<Subscription | undefined> {
    const result = await db
      .select()
      .from(subscriptions)
      .where(eq(subscriptions.userId, userId))
      .orderBy(desc(subscriptions.createdAt))
      .limit(1);
    return result[0];
  }

  async getActiveSubscription(userId: number): Promise<Subscription | undefined> {
    const result = await db
      .select()
      .from(subscriptions)
      .where(and(
        eq(subscriptions.userId, userId),
        eq(subscriptions.status, 'active'),
        gte(subscriptions.expiresAt, new Date())
      ))
      .limit(1);
    return result[0];
  }

  async getUserSubscriptionByLicense(licenseKey: string): Promise<Subscription | undefined> {
    const result = await db
      .select()
      .from(subscriptions)
      .where(eq(subscriptions.licenseKey, licenseKey))
      .limit(1);
    return result[0];
  }

  async extendSubscription(userId: number, days: number): Promise<void> {
    const subscription = await this.getUserSubscription(userId);
    if (subscription) {
      const newExpiry = new Date(Math.max(subscription.expiresAt.getTime(), Date.now()) + days * 24 * 60 * 60 * 1000);
      await db.update(subscriptions)
        .set({ 
          expiresAt: newExpiry,
          status: 'active'
        })
        .where(eq(subscriptions.id, subscription.id));
    }
  }

  async updateSubscriptionStatus(id: number, status: string): Promise<void> {
    await db.update(subscriptions).set({ status }).where(eq(subscriptions.id, id));
  }

  async getExpiringSubscriptions(days: number): Promise<Subscription[]> {
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + days);
    
    return await db
      .select()
      .from(subscriptions)
      .where(and(
        eq(subscriptions.status, 'active'),
        gte(subscriptions.expiresAt, new Date())
      ));
  }

  async createPayment(payment: InsertPayment): Promise<Payment> {
    const result = await db.insert(payments).values({
      ...payment,
      status: 'pending',
    }).returning();
    return result[0];
  }

  async getPayment(id: number): Promise<Payment | undefined> {
    const result = await db.select().from(payments).where(eq(payments.id, id)).limit(1);
    return result[0];
  }

  async updatePaymentStatus(id: number, status: string): Promise<void> {
    const updateData: any = { status };
    if (status === 'completed') {
      updateData.completedAt = new Date();
    }
    await db.update(payments).set(updateData).where(eq(payments.id, id));
  }

  async getUserPayments(userId: number): Promise<Payment[]> {
    return await db
      .select()
      .from(payments)
      .where(eq(payments.userId, userId))
      .orderBy(desc(payments.createdAt));
  }

  async createBotSession(userId: number): Promise<BotSession> {
    const result = await db.insert(botSessions).values({
      userId,
    }).returning();
    return result[0];
  }

  async updateBotSession(id: number, fishCaught: number, skillsUsed: number): Promise<void> {
    await db.update(botSessions)
      .set({ fishCaught, skillsUsed })
      .where(eq(botSessions.id, id));
  }

  async endBotSession(id: number): Promise<void> {
    await db.update(botSessions)
      .set({ 
        sessionEnd: new Date(),
        status: 'ended'
      })
      .where(eq(botSessions.id, id));
  }

  async getUserSessions(userId: number): Promise<BotSession[]> {
    return await db
      .select()
      .from(botSessions)
      .where(eq(botSessions.userId, userId))
      .orderBy(desc(botSessions.sessionStart));
  }

  async getSystemStats(): Promise<{
    totalUsers: number;
    activeSubscriptions: number;
    monthlyRevenue: number;
    newUsersThisMonth: number;
  }> {
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    // Get total users
    const totalUsersResult = await db.select().from(users);
    const totalUsers = totalUsersResult.length;

    // Get active subscriptions
    const activeSubsResult = await db
      .select()
      .from(subscriptions)
      .where(and(
        eq(subscriptions.status, 'active'),
        gte(subscriptions.expiresAt, now)
      ));
    const activeSubscriptions = activeSubsResult.length;

    // Get monthly revenue
    const monthlyPaymentsResult = await db
      .select()
      .from(payments)
      .where(and(
        eq(payments.status, 'completed'),
        gte(payments.completedAt, monthStart)
      ));
    const monthlyRevenue = monthlyPaymentsResult.reduce((sum, payment) => 
      sum + parseFloat(payment.amount), 0);

    // Get new users this month
    const newUsersResult = await db
      .select()
      .from(users)
      .where(gte(users.createdAt, monthStart));
    const newUsersThisMonth = newUsersResult.length;

    return {
      totalUsers,
      activeSubscriptions,
      monthlyRevenue,
      newUsersThisMonth,
    };
  }
}

export const storage = new DatabaseStorage();
