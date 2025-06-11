import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useLocation } from "wouter";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { StatsCard } from "@/components/ui/stats-card";
import { 
  Bot, 
  Download, 
  BarChart3, 
  Settings, 
  LifeBuoy, 
  LogOut,
  Clock,
  Fish,
  Wand2,
  TrendingUp,
  Activity,
  Calendar,
  Shield
} from "lucide-react";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [, navigate] = useLocation();

  // Redirect if not logged in
  useEffect(() => {
    if (!user) {
      navigate("/");
    } else if (user.isAdmin) {
      navigate("/admin");
    }
  }, [user, navigate]);

  const { data: subscription } = useQuery({
    queryKey: ['/api/user/subscription'],
    enabled: !!user,
  });

  const { data: payments } = useQuery({
    queryKey: ['/api/user/payments'],
    enabled: !!user,
  });

  if (!user) return null;

  const getDaysRemaining = () => {
    if (!subscription?.expiresAt) return 0;
    const expires = new Date(subscription.expiresAt);
    const now = new Date();
    return Math.max(0, Math.ceil((expires.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));
  };

  const getProgressPercentage = () => {
    const days = getDaysRemaining();
    return Math.min(100, (days / 30) * 100);
  };

  const sidebarItems = [
    { icon: BarChart3, label: "Dashboard", active: true },
    { icon: Download, label: "Download Bot" },
    { icon: Activity, label: "Estatísticas" },
    { icon: Settings, label: "Configurações" },
    { icon: LifeBuoy, label: "Suporte" },
  ];

  const stats = [
    {
      title: "Tempo Online Hoje",
      value: "4h 32m",
      icon: Clock,
      color: "primary"
    },
    {
      title: "Peixes Capturados",
      value: "1,247",
      icon: Fish,
      color: "accent"
    },
    {
      title: "Skills Utilizadas",
      value: "892",
      icon: Wand2,
      color: "warning"
    },
    {
      title: "Eficiência",
      value: "94%",
      icon: TrendingUp,
      color: "destructive"
    }
  ];

  const botStatus = [
    { name: "Pesca Automática", status: "active", label: "Ativo" },
    { name: "Skills Automáticas", status: "warning", label: "Pausado" },
    { name: "Anti-AFK", status: "active", label: "Ativo" }
  ];

  const recentActivity = [
    {
      icon: Fish,
      title: "Sessão de pesca iniciada",
      description: "Área: Cerulean City - Zona Norte",
      time: "há 2 min",
      color: "accent"
    },
    {
      icon: Download,
      title: "Bot atualizado para v2.1",
      description: "Novas funcionalidades disponíveis",
      time: "há 1 hora",
      color: "primary"
    },
    {
      icon: Wand2,
      title: "Skills configuradas",
      description: "F1-F6 ativadas para cura automática",
      time: "há 3 horas",
      color: "warning"
    }
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border">
        <div className="p-6 border-b border-border">
          <div className="flex items-center space-x-3">
            <div className="bg-primary p-2 rounded-lg">
              <Bot className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <div className="font-semibold text-foreground">RM Bot</div>
              <div className="text-sm text-muted-foreground">Dashboard</div>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          {sidebarItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <button
                key={index}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  item.active 
                    ? 'bg-primary/20 text-primary' 
                    : 'text-muted-foreground hover:bg-muted'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
          <button
            onClick={logout}
            className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-muted-foreground hover:bg-muted transition-colors"
          >
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </button>
        </nav>

        {/* License Status */}
        <div className="absolute bottom-4 left-4 right-4">
          <Card className="bg-surface/50">
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground mb-2">
                Licença {subscription?.planType || 'Premium'}
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className={subscription && getDaysRemaining() > 0 ? "text-accent" : "text-destructive"}>
                  {subscription && getDaysRemaining() > 0 ? 'Ativa' : 'Expirada'}
                </span>
                <span className="text-foreground">
                  {getDaysRemaining()} dias
                </span>
              </div>
              <Progress value={getProgressPercentage()} className="h-2" />
            </CardContent>
          </Card>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="backdrop-blur-surface border-b border-border p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Bem-vindo, {user.fullName || user.username}!
              </h1>
              <p className="text-muted-foreground">
                Monitore suas atividades e estatísticas
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className="status-active">
                <Activity className="h-3 w-3 mr-1" />
                Online
              </Badge>
              <Button className="btn-primary">
                <Download className="mr-2 h-4 w-4" />
                Baixar Bot
              </Button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-6 space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <StatsCard key={index} {...stat} />
            ))}
          </div>

          {/* Main Dashboard Widgets */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Bot Status */}
            <Card className="lg:col-span-2 backdrop-blur-surface">
              <CardHeader>
                <CardTitle className="text-foreground">Status do Bot</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {botStatus.map((status, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-card/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        status.status === 'active' ? 'bg-accent' : 'bg-warning'
                      }`} />
                      <span className="text-foreground">{status.name}</span>
                    </div>
                    <Badge className={status.status === 'active' ? 'status-active' : 'status-warning'}>
                      {status.label}
                    </Badge>
                  </div>
                ))}

                <div className="mt-6 pt-6 border-t border-border">
                  <div className="flex justify-between items-center">
                    <span className="text-foreground">Última Sincronização</span>
                    <span className="text-muted-foreground">há 30 segundos</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* License Info */}
            <Card className="backdrop-blur-surface">
              <CardHeader>
                <CardTitle className="text-foreground">Informações da Licença</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-muted-foreground">Plano Atual</span>
                    <Badge variant="outline" className="text-primary border-primary">
                      {subscription?.planType || 'Premium'}
                    </Badge>
                  </div>
                </div>

                {subscription && (
                  <>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Próxima Cobrança</span>
                        <span className="text-foreground">
                          {new Date(subscription.expiresAt).toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Dias Restantes</span>
                        <span className={getDaysRemaining() > 7 ? "text-accent" : "text-warning"}>
                          {getDaysRemaining()} dias
                        </span>
                      </div>
                      <Progress value={getProgressPercentage()} className="h-2" />
                    </div>
                  </>
                )}

                <Button className="w-full btn-primary mt-4">
                  <Shield className="mr-2 h-4 w-4" />
                  Gerenciar Assinatura
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="backdrop-blur-surface">
            <CardHeader>
              <CardTitle className="text-foreground">Atividade Recente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentActivity.map((activity, index) => {
                const Icon = activity.icon;
                return (
                  <div key={index} className="flex items-center justify-between p-4 bg-card/30 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${
                        activity.color === 'accent' ? 'bg-accent/20' :
                        activity.color === 'primary' ? 'bg-primary/20' :
                        'bg-warning/20'
                      }`}>
                        <Icon className={`h-4 w-4 ${
                          activity.color === 'accent' ? 'text-accent' :
                          activity.color === 'primary' ? 'text-primary' :
                          'text-warning'
                        }`} />
                      </div>
                      <div>
                        <p className="text-foreground text-sm">{activity.title}</p>
                        <p className="text-muted-foreground text-xs">{activity.description}</p>
                      </div>
                    </div>
                    <span className="text-muted-foreground text-sm">{activity.time}</span>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
