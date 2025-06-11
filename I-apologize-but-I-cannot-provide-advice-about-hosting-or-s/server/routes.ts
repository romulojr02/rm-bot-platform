import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertUserSchema, loginSchema, insertPaymentSchema } from "@shared/schema";
import session from "express-session";
import ConnectPgSimple from "connect-pg-simple";
import { neon } from "@neondatabase/serverless";

declare module "express-session" {
  interface SessionData {
    userId?: number;
    isAdmin?: boolean;
  }
}

const PgSession = ConnectPgSimple(session);

export async function registerRoutes(app: Express): Promise<Server> {
  // Session configuration
  app.use(session({
    store: new PgSession({
      conString: process.env.DATABASE_URL,
      createTableIfMissing: true,
    }),
    secret: process.env.SESSION_SECRET || 'your-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production',
      httpOnly: true,
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
    },
  }));

  // Middleware to check authentication
  const requireAuth = (req: any, res: any, next: any) => {
    if (!req.session.userId) {
      return res.status(401).json({ message: 'Authentication required' });
    }
    next();
  };

  const requireAdmin = (req: any, res: any, next: any) => {
    if (!req.session.userId || !req.session.isAdmin) {
      return res.status(403).json({ message: 'Admin access required' });
    }
    next();
  };

  // Auth routes
  app.post('/api/auth/register', async (req, res) => {
    try {
      const userData = insertUserSchema.parse(req.body);
      
      // Check if user already exists
      const existingUser = await storage.getUserByUsername(userData.username);
      if (existingUser) {
        return res.status(400).json({ message: 'Username already exists' });
      }

      const existingEmail = await storage.getUserByEmail(userData.email);
      if (existingEmail) {
        return res.status(400).json({ message: 'Email already exists' });
      }

      const user = await storage.createUser(userData);
      
      req.session.userId = user.id;
      req.session.isAdmin = user.isAdmin || false;

      res.json({ 
        id: user.id, 
        username: user.username, 
        email: user.email,
        fullName: user.fullName,
        isAdmin: user.isAdmin 
      });
    } catch (error: any) {
      res.status(400).json({ message: error.message });
    }
  });

  app.post('/api/auth/login', async (req, res) => {
    try {
      const { username, password } = loginSchema.parse(req.body);

      const user = await storage.authenticateUser(username, password);
      if (!user) {
        return res.status(401).json({ message: 'Invalid credentials' });
      }

      req.session.userId = user.id;
      req.session.isAdmin = user.isAdmin || false;

      res.json({ 
        id: user.id, 
        username: user.username, 
        email: user.email,
        fullName: user.fullName,
        isAdmin: user.isAdmin 
      });
    } catch (error: any) {
      res.status(400).json({ message: error.message });
    }
  });

  app.post('/api/auth/logout', (req, res) => {
    req.session.destroy((err) => {
      if (err) {
        return res.status(500).json({ message: 'Could not log out' });
      }
      res.json({ message: 'Logged out successfully' });
    });
  });

  app.get('/api/auth/me', async (req, res) => {
    if (!req.session.userId) {
      return res.status(401).json({ message: 'Not authenticated' });
    }

    try {
      const user = await storage.getUser(req.session.userId);
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }

      res.json({ 
        id: user.id, 
        username: user.username, 
        email: user.email,
        fullName: user.fullName,
        isAdmin: user.isAdmin 
      });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  // User routes
  app.get('/api/user/subscription', requireAuth, async (req, res) => {
    try {
      const subscription = await storage.getActiveSubscription(req.session.userId!);
      res.json(subscription);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.get('/api/user/sessions', requireAuth, async (req, res) => {
    try {
      const sessions = await storage.getUserSessions(req.session.userId!);
      res.json(sessions);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.get('/api/user/payments', requireAuth, async (req, res) => {
    try {
      const payments = await storage.getUserPayments(req.session.userId!);
      res.json(payments);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  // Payment routes
  app.post('/api/payments/create', requireAuth, async (req, res) => {
    try {
      const { planType, paymentMethod } = req.body;
      
      const planPrices = {
        basic: '19.90',
        premium: '39.90',
        pro: '69.90'
      };

      const amount = planPrices[planType as keyof typeof planPrices];
      if (!amount) {
        return res.status(400).json({ message: 'Invalid plan type' });
      }

      const payment = await storage.createPayment({
        userId: req.session.userId!,
        amount,
        paymentMethod,
        externalId: `pix_${Date.now()}_${req.session.userId}`,
      });

      // In a real implementation, you would integrate with a payment gateway here
      // For now, we'll simulate a PIX payment
      const pixCode = `00020126330015BR.PIX.${payment.id.toString().padStart(10, '0')}`;

      res.json({
        paymentId: payment.id,
        amount: payment.amount,
        pixCode,
        qrCodeData: pixCode,
        status: payment.status
      });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.post('/api/payments/:id/complete', requireAuth, async (req, res) => {
    try {
      const paymentId = parseInt(req.params.id);
      const payment = await storage.getPayment(paymentId);
      
      if (!payment || payment.userId !== req.session.userId) {
        return res.status(404).json({ message: 'Payment not found' });
      }

      await storage.updatePaymentStatus(paymentId, 'completed');

      // Create or extend subscription
      const planDays = {
        basic: 30,
        premium: 30,
        pro: 30
      };

      // Determine plan type based on amount (simplified)
      let planType = 'basic';
      if (payment.amount === '39.90') planType = 'premium';
      if (payment.amount === '69.90') planType = 'pro';

      const days = planDays[planType as keyof typeof planDays];
      await storage.extendSubscription(payment.userId, days);

      res.json({ message: 'Payment completed and subscription activated' });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  // Bot routes
  app.get('/api/bot/download', requireAuth, async (req, res) => {
    try {
      const subscription = await storage.getActiveSubscription(req.session.userId!);
      if (!subscription) {
        return res.status(403).json({ message: 'Active subscription required' });
      }

      // In production, serve the actual bot file
      // For now, create a placeholder file
      const botContent = `
# RM Bot Launcher - Conecte com sua licença online
# Arquivo de exemplo - substitua pelo bot real

import requests
import sys

def validate_license(license_key):
    try:
        response = requests.post('${process.env.NODE_ENV === 'production' ? 'https://your-domain.com' : 'http://localhost:5000'}/api/bot/validate-license', {
            'license_key': license_key
        })
        return response.status_code == 200
    except:
        return False

if __name__ == '__main__':
    license_key = input("Digite sua chave de licença: ")
    if validate_license(license_key):
        print("Licença válida! Iniciando RM Bot...")
        # Aqui você adicionaria o código do seu bot real
    else:
        print("Licença inválida ou expirada!")
        sys.exit(1)
`;

      res.setHeader('Content-Type', 'application/octet-stream');
      res.setHeader('Content-Disposition', 'attachment; filename="RM_Bot_v2.0.py"');
      res.send(botContent);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.post('/api/bot/validate-license', async (req, res) => {
    try {
      const { license_key } = req.body;
      
      // Find subscription by license key
      const subscription = await storage.getUserSubscriptionByLicense(license_key);
      
      if (!subscription) {
        return res.status(401).json({ message: 'Invalid license key' });
      }

      if (new Date(subscription.expiresAt) < new Date()) {
        return res.status(401).json({ message: 'License expired' });
      }

      res.json({ 
        valid: true, 
        planType: subscription.planType,
        expiresAt: subscription.expiresAt 
      });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.post('/api/bot/session/start', requireAuth, async (req, res) => {
    try {
      const subscription = await storage.getActiveSubscription(req.session.userId!);
      if (!subscription) {
        return res.status(403).json({ message: 'Active subscription required' });
      }

      const session = await storage.createBotSession(req.session.userId!);
      res.json(session);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.put('/api/bot/session/:id', requireAuth, async (req, res) => {
    try {
      const sessionId = parseInt(req.params.id);
      const { fishCaught, skillsUsed } = req.body;

      await storage.updateBotSession(sessionId, fishCaught, skillsUsed);
      res.json({ message: 'Session updated' });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.post('/api/bot/session/:id/end', requireAuth, async (req, res) => {
    try {
      const sessionId = parseInt(req.params.id);
      await storage.endBotSession(sessionId);
      res.json({ message: 'Session ended' });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  // Admin routes
  app.get('/api/admin/stats', requireAdmin, async (req, res) => {
    try {
      const stats = await storage.getSystemStats();
      res.json(stats);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.get('/api/admin/users', requireAdmin, async (req, res) => {
    try {
      const users = await storage.getAllUsers();
      res.json(users);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.post('/api/admin/users/:id/extend', requireAdmin, async (req, res) => {
    try {
      const userId = parseInt(req.params.id);
      const { days } = req.body;

      await storage.extendSubscription(userId, days);
      res.json({ message: 'Subscription extended' });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.delete('/api/admin/users/:id', requireAdmin, async (req, res) => {
    try {
      const userId = parseInt(req.params.id);
      await storage.deleteUser(userId);
      res.json({ message: 'User deleted' });
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  app.get('/api/admin/expiring-subscriptions', requireAdmin, async (req, res) => {
    try {
      const days = parseInt(req.query.days as string) || 7;
      const subscriptions = await storage.getExpiringSubscriptions(days);
      res.json(subscriptions);
    } catch (error: any) {
      res.status(500).json({ message: error.message });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
