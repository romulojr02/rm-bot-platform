import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/use-auth';
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '@/lib/api';
import { Subscription, BotSession } from '@shared/schema';

export function UserDashboard() {
  const { user, logout } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const { data: subscription } = useQuery<Subscription>({
    queryKey: ['/api/user/subscription'],
  });

  const { data: sessions } = useQuery<BotSession[]>({
    queryKey: ['/api/user/sessions'],
  });

  const { data: payments } = useQuery({
    queryKey: ['/api/user/payments'],
  });

  const todaySessions = sessions?.filter(session => {
    const sessionDate = new Date(session.sessionStart);
    const today = new Date();
    return sessionDate.toDateString() === today.toDateString();
  }) || [];

  const todayStats = todaySessions.reduce(
    (acc, session) => ({
      timeOnline: acc.timeOnline + (session.sessionEnd 
        ? new Date(session.sessionEnd).getTime() - new Date(session.sessionStart).getTime()
        : Date.now() - new Date(session.sessionStart).getTime()),
      fishCaught: acc.fishCaught + (session.fishCaught || 0),
      skillsUsed: acc.skillsUsed + (session.skillsUsed || 0),
    }),
    { timeOnline: 0, fishCaught: 0, skillsUsed: 0 }
  );

  const formatTime = (ms: number) => {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const getDaysRemaining = () => {
    if (!subscription) return 0;
    const expiresAt = new Date(subscription.expiresAt);
    const now = new Date();
    const diffTime = expiresAt.getTime() - now.getTime();
    return Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
  };

  const isActive = subscription && new Date(subscription.expiresAt) > new Date();

  return (
    <div className="flex h-screen bg-slate-700">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-800 border-r border-slate-600">
        <div className="p-6 border-b border-slate-600">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-500 p-2 rounded-lg">
              <i className="fas fa-robot text-white"></i>
            </div>
            <div>
              <div className="font-semibold text-white">RM Bot</div>
              <div className="text-sm text-gray-400">Dashboard</div>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-blue-500/20 text-blue-400">
            <i className="fas fa-tachometer-alt"></i>
            <span>Dashboard</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-download"></i>
            <span>Download Bot</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-chart-bar"></i>
            <span>Estatísticas</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-cog"></i>
            <span>Configurações</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-life-ring"></i>
            <span>Suporte</span>
          </a>
          <Button
            variant="ghost"
            onClick={logout}
            className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50 w-full justify-start"
          >
            <i className="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </Button>
        </nav>

        {subscription && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-slate-600/50 p-4 rounded-lg">
              <div className="text-sm text-gray-400 mb-2">Licença {subscription.planType}</div>
              <div className="flex justify-between text-sm">
                <span className={isActive ? "text-green-400" : "text-red-400"}>
                  {isActive ? "Ativa" : "Expirada"}
                </span>
                <span className="text-gray-300">{getDaysRemaining()} dias</span>
              </div>
              <div className="w-full bg-slate-600 rounded-full h-2 mt-2">
                <div 
                  className="bg-green-400 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, (getDaysRemaining() / 30) * 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-600 p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-white">Bem-vindo, {user?.fullName}!</h1>
              <p className="text-gray-400">Monitore suas atividades e estatísticas</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                isActive 
                  ? 'bg-green-500/20 text-green-400' 
                  : 'bg-red-500/20 text-red-400'
              }`}>
                <i className="fas fa-circle text-xs mr-2"></i>
                {isActive ? 'Online' : 'Offline'}
              </div>
              <Button className="bg-blue-500 hover:bg-blue-600">
                <i className="fas fa-download mr-2"></i>
                Baixar Bot
              </Button>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-6 space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Tempo Online Hoje</p>
                    <p className="text-2xl font-bold text-white">{formatTime(todayStats.timeOnline)}</p>
                  </div>
                  <div className="bg-blue-500/20 p-3 rounded-lg">
                    <i className="fas fa-clock text-blue-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Peixes Capturados</p>
                    <p className="text-2xl font-bold text-white">{todayStats.fishCaught.toLocaleString()}</p>
                  </div>
                  <div className="bg-green-500/20 p-3 rounded-lg">
                    <i className="fas fa-fish text-green-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Skills Utilizadas</p>
                    <p className="text-2xl font-bold text-white">{todayStats.skillsUsed.toLocaleString()}</p>
                  </div>
                  <div className="bg-yellow-500/20 p-3 rounded-lg">
                    <i className="fas fa-magic text-yellow-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Eficiência</p>
                    <p className="text-2xl font-bold text-white">
                      {todayStats.fishCaught > 0 ? Math.min(100, Math.round((todayStats.fishCaught / (todayStats.timeOnline / (1000 * 60))) * 10)) : 0}%
                    </p>
                  </div>
                  <div className="bg-red-500/20 p-3 rounded-lg">
                    <i className="fas fa-chart-line text-red-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Dashboard Widgets */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Bot Status */}
            <div className="lg:col-span-2">
              <Card className="bg-slate-600/30 border-slate-600">
                <CardHeader>
                  <CardTitle className="text-white">Status do Bot</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                      <span className="text-white">Pesca Automática</span>
                    </div>
                    <span className="text-green-400 font-medium">Ativo</span>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span className="text-white">Skills Automáticas</span>
                    </div>
                    <span className="text-yellow-500 font-medium">Pausado</span>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                      <span className="text-white">Anti-AFK</span>
                    </div>
                    <span className="text-green-400 font-medium">Ativo</span>
                  </div>

                  <div className="pt-6 border-t border-slate-600">
                    <div className="flex justify-between items-center">
                      <span className="text-white">Última Sincronização</span>
                      <span className="text-gray-400">há 30 segundos</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* License Info */}
            <Card className="bg-slate-600/30 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white">Informações da Licença</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {subscription ? (
                  <>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Plano Atual</span>
                        <span className="text-blue-500 font-medium capitalize">{subscription.planType}</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Próxima Cobrança</span>
                        <span className="text-white">{new Date(subscription.expiresAt).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Dias Restantes</span>
                        <span className="text-green-400 font-medium">{getDaysRemaining()} dias</span>
                      </div>
                      <div className="w-full bg-slate-600 rounded-full h-2">
                        <div 
                          className="bg-green-400 h-2 rounded-full" 
                          style={{ width: `${Math.min(100, (getDaysRemaining() / 30) * 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    <Button className="w-full bg-blue-500 hover:bg-blue-600 mt-4">
                      Gerenciar Assinatura
                    </Button>
                  </>
                ) : (
                  <div className="text-center">
                    <p className="text-gray-400 mb-4">Nenhuma licença ativa</p>
                    <Button className="w-full bg-green-500 hover:bg-green-600">
                      Adquirir Licença
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="bg-slate-600/30 border-slate-600">
            <CardHeader>
              <CardTitle className="text-white">Atividade Recente</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-green-500/20 p-2 rounded-lg">
                    <i className="fas fa-fish text-green-500 text-sm"></i>
                  </div>
                  <div>
                    <p className="text-white text-sm">Sessão de pesca iniciada</p>
                    <p className="text-gray-400 text-xs">Área: Cerulean City - Zona Norte</p>
                  </div>
                </div>
                <span className="text-gray-400 text-sm">há 2 min</span>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-blue-500/20 p-2 rounded-lg">
                    <i className="fas fa-download text-blue-500 text-sm"></i>
                  </div>
                  <div>
                    <p className="text-white text-sm">Bot atualizado para v2.1</p>
                    <p className="text-gray-400 text-xs">Novas funcionalidades disponíveis</p>
                  </div>
                </div>
                <span className="text-gray-400 text-sm">há 1 hora</span>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-yellow-500/20 p-2 rounded-lg">
                    <i className="fas fa-magic text-yellow-500 text-sm"></i>
                  </div>
                  <div>
                    <p className="text-white text-sm">Skills configuradas</p>
                    <p className="text-gray-400 text-xs">F1-F6 ativadas para cura automática</p>
                  </div>
                </div>
                <span className="text-gray-400 text-sm">há 3 horas</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
