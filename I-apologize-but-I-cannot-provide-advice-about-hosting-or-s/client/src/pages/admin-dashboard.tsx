import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/hooks/use-auth';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/api';

export function AdminDashboard() {
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [extendDays, setExtendDays] = useState('30');
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [showExtendModal, setShowExtendModal] = useState(false);

  const { data: stats } = useQuery({
    queryKey: ['/api/admin/stats'],
  });

  const { data: users } = useQuery({
    queryKey: ['/api/admin/users'],
  });

  const extendMutation = useMutation({
    mutationFn: async ({ userId, days }: { userId: number; days: number }) => {
      await apiRequest('POST', `/api/admin/users/${userId}/extend`, { days });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/admin/users'] });
      toast({
        title: "Sucesso",
        description: "Licença estendida com sucesso!",
      });
      setShowExtendModal(false);
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (userId: number) => {
      await apiRequest('DELETE', `/api/admin/users/${userId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/admin/users'] });
      toast({
        title: "Sucesso",
        description: "Usuário deletado com sucesso!",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleExtendUser = (userId: number) => {
    setSelectedUserId(userId);
    setShowExtendModal(true);
  };

  const confirmExtend = () => {
    if (selectedUserId && extendDays) {
      extendMutation.mutate({ userId: selectedUserId, days: parseInt(extendDays) });
    }
  };

  const handleDeleteUser = (userId: number) => {
    if (confirm('Tem certeza que deseja deletar este usuário?')) {
      deleteMutation.mutate(userId);
    }
  };

  const getStatusBadge = (subscription: any) => {
    if (!subscription) {
      return <Badge variant="destructive">Sem Licença</Badge>;
    }
    
    const isExpired = new Date(subscription.expiresAt) < new Date();
    if (isExpired) {
      return <Badge variant="destructive">Expirado</Badge>;
    }
    
    return <Badge variant="default" className="bg-green-500">Ativo</Badge>;
  };

  const getPlanBadge = (planType: string) => {
    const colors = {
      basic: 'bg-gray-500',
      premium: 'bg-blue-500',
      pro: 'bg-green-500'
    };
    
    return (
      <Badge className={colors[planType as keyof typeof colors] || 'bg-gray-500'}>
        {planType?.charAt(0).toUpperCase() + planType?.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="flex h-screen bg-slate-700">
      {/* Admin Sidebar */}
      <aside className="w-64 bg-slate-800 border-r border-slate-600">
        <div className="p-6 border-b border-slate-600">
          <div className="flex items-center space-x-3">
            <div className="bg-red-500 p-2 rounded-lg">
              <i className="fas fa-crown text-white"></i>
            </div>
            <div>
              <div className="font-semibold text-white">Admin Panel</div>
              <div className="text-sm text-gray-400">Controle Total</div>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-blue-500/20 text-blue-400">
            <i className="fas fa-chart-pie"></i>
            <span>Visão Geral</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-users"></i>
            <span>Usuários</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-credit-card"></i>
            <span>Pagamentos</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-key"></i>
            <span>Licenças</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-ticket-alt"></i>
            <span>Suporte</span>
          </a>
          <a href="#" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-slate-600/50">
            <i className="fas fa-cogs"></i>
            <span>Sistema</span>
          </a>
        </nav>
      </aside>

      {/* Admin Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Admin Header */}
        <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-600 p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-white">Painel Administrativo</h1>
              <p className="text-gray-400">Gerencie usuários, licenças e pagamentos</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm font-medium">
                <i className="fas fa-shield-alt text-xs mr-2"></i>
                Admin
              </div>
              <Button onClick={logout} className="bg-red-500 hover:bg-red-600">
                <i className="fas fa-sign-out-alt mr-2"></i>
                Logout
              </Button>
            </div>
          </div>
        </header>

        {/* Admin Dashboard Content */}
        <div className="p-6 space-y-6">
          {/* Admin Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Usuários Ativos</p>
                    <p className="text-2xl font-bold text-white">{stats?.totalUsers || 0}</p>
                    <p className="text-green-400 text-sm">+{stats?.newUsersThisMonth || 0} este mês</p>
                  </div>
                  <div className="bg-green-500/20 p-3 rounded-lg">
                    <i className="fas fa-users text-green-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Receita Mensal</p>
                    <p className="text-2xl font-bold text-white">R$ {stats?.monthlyRevenue?.toFixed(2) || '0.00'}</p>
                    <p className="text-green-400 text-sm">Este mês</p>
                  </div>
                  <div className="bg-blue-500/20 p-3 rounded-lg">
                    <i className="fas fa-dollar-sign text-blue-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Assinaturas Ativas</p>
                    <p className="text-2xl font-bold text-white">{stats?.activeSubscriptions || 0}</p>
                    <p className="text-yellow-500 text-sm">Licenças válidas</p>
                  </div>
                  <div className="bg-yellow-500/20 p-3 rounded-lg">
                    <i className="fas fa-user-plus text-yellow-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Novos Usuários</p>
                    <p className="text-2xl font-bold text-white">{stats?.newUsersThisMonth || 0}</p>
                    <p className="text-blue-400 text-sm">Este mês</p>
                  </div>
                  <div className="bg-purple-500/20 p-3 rounded-lg">
                    <i className="fas fa-chart-line text-purple-500"></i>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* User Management Table */}
          <Card className="bg-slate-600/30 border-slate-600">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-white">Gerenciar Usuários</CardTitle>
                <Button className="bg-blue-500 hover:bg-blue-600">
                  <i className="fas fa-user-plus mr-2"></i>
                  Novo Usuário
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Usuário
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Plano
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Vencimento
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-600">
                    {users?.map((user: any) => (
                      <tr key={user.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="bg-blue-500 p-2 rounded-full text-white text-sm font-semibold mr-3">
                              {user.fullName?.charAt(0) || user.username?.charAt(0)}
                            </div>
                            <div>
                              <div className="text-sm font-medium text-white">{user.fullName || user.username}</div>
                              <div className="text-sm text-gray-400">{user.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {user.subscription ? getPlanBadge(user.subscription.planType) : <span className="text-gray-400">-</span>}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(user.subscription)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-300">
                          {user.subscription 
                            ? new Date(user.subscription.expiresAt).toLocaleDateString()
                            : '-'
                          }
                        </td>
                        <td className="px-6 py-4 text-sm font-medium space-x-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleExtendUser(user.id)}
                            className="text-blue-400 hover:text-blue-300"
                          >
                            <i className="fas fa-key"></i>
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDeleteUser(user.id)}
                            className="text-red-400 hover:text-red-300"
                          >
                            <i className="fas fa-trash"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Quick Admin Actions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="bg-slate-600/30 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white text-lg">Licenças Rápidas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-blue-500/20 hover:bg-blue-500/30 text-blue-400">
                  Estender 7 dias - Todos
                </Button>
                <Button className="w-full bg-green-500/20 hover:bg-green-500/30 text-green-400">
                  Estender 30 dias - Premium
                </Button>
                <Button className="w-full bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400">
                  Limpar Expirados
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white text-lg">Sistema</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full bg-blue-500/20 hover:bg-blue-500/30 text-blue-400">
                  Backup Database
                </Button>
                <Button className="w-full bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400">
                  Atualizar Bot v2.1
                </Button>
                <Button className="w-full bg-red-500/20 hover:bg-red-500/30 text-red-400">
                  Manutenção
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-slate-600/30 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white text-lg">Notificações</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm">
                  <div className="text-white">3 novos pagamentos</div>
                  <div className="text-gray-400">há 15 min</div>
                </div>
                <div className="text-sm">
                  <div className="text-white">12 licenças expiram em 7 dias</div>
                  <div className="text-gray-400">Hoje</div>
                </div>
                <div className="text-sm">
                  <div className="text-white">5 tickets pendentes</div>
                  <div className="text-gray-400">Ontem</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Extend License Modal */}
      <Dialog open={showExtendModal} onOpenChange={setShowExtendModal}>
        <DialogContent className="bg-slate-800 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">Estender Licença</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Dias para estender
              </label>
              <Input
                type="number"
                value={extendDays}
                onChange={(e) => setExtendDays(e.target.value)}
                className="bg-slate-700 border-slate-600 text-white"
                placeholder="30"
              />
            </div>
            <div className="flex gap-3 pt-4">
              <Button
                onClick={confirmExtend}
                className="flex-1 bg-green-500 hover:bg-green-600"
                disabled={extendMutation.isPending}
              >
                {extendMutation.isPending ? 'Estendendo...' : 'Confirmar'}
              </Button>
              <Button
                onClick={() => setShowExtendModal(false)}
                variant="outline"
                className="flex-1 border-slate-600"
              >
                Cancelar
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
