import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'login' | 'register';
  onPaymentSuccess?: () => void;
}

export function AuthModal({ isOpen, onClose, initialMode = 'login', onPaymentSuccess }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();
  const { toast } = useToast();

  const [loginData, setLoginData] = useState({
    username: '',
    password: '',
  });

  const [registerData, setRegisterData] = useState({
    fullName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginData.username || !loginData.password) {
      toast({
        title: "Erro",
        description: "Preencha todos os campos",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await login(loginData.username, loginData.password);
      toast({
        title: "Sucesso",
        description: "Login realizado com sucesso!",
      });
      onClose();
    } catch (error: any) {
      toast({
        title: "Erro no login",
        description: error.message || "Credenciais inválidas",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!registerData.fullName || !registerData.email || !registerData.username || !registerData.password) {
      toast({
        title: "Erro",
        description: "Preencha todos os campos",
        variant: "destructive",
      });
      return;
    }

    if (registerData.password !== registerData.confirmPassword) {
      toast({
        title: "Erro",
        description: "As senhas não coincidem",
        variant: "destructive",
      });
      return;
    }

    if (!registerData.agreeToTerms) {
      toast({
        title: "Erro",
        description: "Você deve concordar com os termos de serviço",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await register({
        fullName: registerData.fullName,
        email: registerData.email,
        username: registerData.username,
        password: registerData.password,
      });
      toast({
        title: "Sucesso",
        description: "Conta criada com sucesso!",
      });
      onClose();
      onPaymentSuccess?.();
    } catch (error: any) {
      toast({
        title: "Erro no cadastro",
        description: error.message || "Erro ao criar conta",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const adminLogin = async () => {
    setIsLoading(true);
    try {
      await login('admin', 'admin123');
      toast({
        title: "Sucesso",
        description: "Login administrativo realizado!",
      });
      onClose();
    } catch (error: any) {
      toast({
        title: "Erro",
        description: "Credenciais administrativas inválidas",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-slate-800 border-slate-700">
        <DialogHeader>
          <DialogTitle className="text-center text-white">
            <div className="flex flex-col items-center mb-4">
              <div className="bg-blue-500 p-3 rounded-lg mb-4">
                <i className={`fas ${mode === 'login' ? 'fa-robot' : 'fa-user-plus'} text-white text-2xl`}></i>
              </div>
              {mode === 'login' ? 'Entrar no RM Bot' : 'Criar Conta'}
            </div>
          </DialogTitle>
        </DialogHeader>

        {mode === 'login' ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <Label className="text-gray-300">Email ou Usuário</Label>
              <Input
                type="text"
                value={loginData.username}
                onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                placeholder="Digite seu email..."
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-gray-300">Senha</Label>
              <Input
                type="password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                placeholder="Digite sua senha..."
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Checkbox id="remember" />
                <Label htmlFor="remember" className="text-sm text-gray-300">Lembrar-me</Label>
              </div>
              <a href="#" className="text-sm text-blue-400 hover:text-blue-300">Esqueci a senha</a>
            </div>

            <Button type="submit" className="w-full bg-blue-500 hover:bg-blue-600" disabled={isLoading}>
              {isLoading ? 'Entrando...' : 'Entrar'}
            </Button>

            <div className="text-center">
              <span className="text-gray-400">Não tem conta? </span>
              <button type="button" onClick={() => setMode('register')} className="text-blue-400 hover:text-blue-300">
                Cadastre-se
              </button>
            </div>

            <div className="mt-6 pt-6 border-t border-slate-600">
              <Button
                type="button"
                onClick={adminLogin}
                className="w-full bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/50"
                disabled={isLoading}
              >
                <i className="fas fa-crown mr-2"></i>
                Login Administrativo
              </Button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <Label className="text-gray-300">Nome Completo</Label>
              <Input
                type="text"
                value={registerData.fullName}
                onChange={(e) => setRegisterData({ ...registerData, fullName: e.target.value })}
                placeholder="Seu nome completo..."
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-gray-300">Email</Label>
              <Input
                type="email"
                value={registerData.email}
                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                placeholder="seu@email.com"
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-gray-300">Usuário</Label>
              <Input
                type="text"
                value={registerData.username}
                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                placeholder="Nome de usuário..."
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-gray-300">Senha</Label>
              <Input
                type="password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                placeholder="Mínimo 8 caracteres..."
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div>
              <Label className="text-gray-300">Confirmar Senha</Label>
              <Input
                type="password"
                value={registerData.confirmPassword}
                onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                placeholder="Repita sua senha..."
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>

            <div className="flex items-start space-x-2">
              <Checkbox
                checked={registerData.agreeToTerms}
                onCheckedChange={(checked) => setRegisterData({ ...registerData, agreeToTerms: !!checked })}
              />
              <Label className="text-sm text-gray-300 leading-relaxed">
                Concordo com os <a href="#" className="text-blue-400 hover:text-blue-300">Termos de Serviço</a> e 
                <a href="#" className="text-blue-400 hover:text-blue-300"> Política de Privacidade</a>
              </Label>
            </div>

            <Button type="submit" className="w-full bg-green-500 hover:bg-green-600" disabled={isLoading}>
              {isLoading ? 'Criando conta...' : 'Criar Conta Gratuita'}
            </Button>

            <div className="text-center">
              <span className="text-gray-400">Já tem conta? </span>
              <button type="button" onClick={() => setMode('login')} className="text-blue-400 hover:text-blue-300">
                Fazer login
              </button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
