import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { AuthModal } from '@/components/auth-modal';
import { PaymentModal } from '@/components/payment-modal';

export function Landing() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [selectedPlan, setSelectedPlan] = useState<{
    type: 'basic' | 'premium' | 'pro';
    price: string;
  }>({ type: 'premium', price: '39.90' });

  const openLogin = () => {
    setAuthMode('login');
    setShowAuthModal(true);
  };

  const openRegister = () => {
    setAuthMode('register');
    setShowAuthModal(true);
  };

  const openPayment = (planType: 'basic' | 'premium' | 'pro', price: string) => {
    setSelectedPlan({ type: planType, price });
    setShowPaymentModal(true);
  };

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-700 text-gray-100">
      {/* Navigation */}
      <nav className="bg-slate-800/95 backdrop-blur-sm border-b border-slate-600 fixed w-full top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-500 p-2 rounded-lg">
                <i className="fas fa-robot text-white text-xl"></i>
              </div>
              <span className="text-xl font-bold text-white">RM Bot</span>
              <span className="text-sm bg-green-500/20 text-green-400 px-2 py-1 rounded-full">v2.0</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button onClick={() => scrollToSection('features')} className="text-gray-300 hover:text-white transition">
                Recursos
              </button>
              <button onClick={() => scrollToSection('pricing')} className="text-gray-300 hover:text-white transition">
                Preços
              </button>
              <button onClick={() => scrollToSection('contact')} className="text-gray-300 hover:text-white transition">
                Suporte
              </button>
              <Button variant="ghost" onClick={openLogin} className="text-gray-300 hover:text-white">
                Login
              </Button>
              <Button onClick={openRegister} className="bg-blue-500 hover:bg-blue-600">
                Começar Agora
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="pt-24 pb-16 bg-gradient-to-br from-slate-800 via-slate-700 to-slate-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            Automação Premium<br/>para Poke Old
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            O bot mais avançado para Poke Old. Pesca automática, skills inteligentes, detecção visual e muito mais. 
            Usado por +5.000 jogadores em todo Brasil.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button 
              onClick={() => openPayment('premium', '39.90')}
              className="bg-blue-500 hover:bg-blue-600 px-8 py-4 text-lg font-semibold"
              size="lg"
            >
              <i className="fas fa-download mr-2"></i>
              Começar Agora - R$ 19,90/mês
            </Button>
            <Button 
              variant="outline"
              onClick={() => scrollToSection('features')}
              className="border-slate-600 hover:border-blue-500 px-8 py-4 text-lg font-semibold"
              size="lg"
            >
              <i className="fas fa-play mr-2"></i>
              Ver Demonstração
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">5.000+</div>
              <div className="text-sm text-gray-400">Usuários Ativos</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">99.9%</div>
              <div className="text-sm text-gray-400">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">24/7</div>
              <div className="text-sm text-gray-400">Suporte</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">100%</div>
              <div className="text-sm text-gray-400">Seguro</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section id="features" className="py-20 bg-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Recursos Avançados</h2>
            <p className="text-xl text-gray-300">Tecnologia de ponta para máxima eficiência</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-slate-600/50 backdrop-blur-sm p-6 rounded-xl hover:bg-slate-600/70 transition">
              <div className="bg-blue-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-fish text-blue-500 text-xl"></i>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Pesca Inteligente</h3>
              <p className="text-gray-300">Detecção visual avançada de áreas de água. Cliques humanizados e anti-detecção.</p>
            </div>

            <div className="bg-slate-600/50 backdrop-blur-sm p-6 rounded-xl hover:bg-slate-600/70 transition">
              <div className="bg-green-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-magic text-green-500 text-xl"></i>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Skills Automáticas</h3>
              <p className="text-gray-300">Configure F1-F12 com intervalos personalizados. Rotação inteligente de habilidades.</p>
            </div>

            <div className="bg-slate-600/50 backdrop-blur-sm p-6 rounded-xl hover:bg-slate-600/70 transition">
              <div className="bg-yellow-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-eye text-yellow-500 text-xl"></i>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Detecção Visual</h3>
              <p className="text-gray-300">OpenCV para reconhecimento de padrões. Adapta-se automaticamente ao ambiente.</p>
            </div>

            <div className="bg-slate-600/50 backdrop-blur-sm p-6 rounded-xl hover:bg-slate-600/70 transition">
              <div className="bg-red-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-shield-alt text-red-500 text-xl"></i>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Anti-Detecção</h3>
              <p className="text-gray-300">Padrões humanos de movimento. Variação nos tempos e coordenadas.</p>
            </div>

            <div className="bg-slate-600/50 backdrop-blur-sm p-6 rounded-xl hover:bg-slate-600/70 transition">
              <div className="bg-blue-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-chart-line text-blue-500 text-xl"></i>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Estatísticas Detalhadas</h3>
              <p className="text-gray-300">Acompanhe seus ganhos, tempo de uso e eficiência em tempo real.</p>
            </div>

            <div className="bg-slate-600/50 backdrop-blur-sm p-6 rounded-xl hover:bg-slate-600/70 transition">
              <div className="bg-green-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-headset text-green-500 text-xl"></i>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Suporte 24/7</h3>
              <p className="text-gray-300">Discord ativo com comunidade. Atualizações constantes e suporte premium.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Planos Flexíveis</h2>
            <p className="text-xl text-gray-300">Escolha o plano ideal para suas necessidades</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Basic Plan */}
            <div className="bg-slate-600/30 backdrop-blur-sm p-8 rounded-xl border border-slate-600 hover:border-blue-500/50 transition">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">Básico</h3>
                <div className="text-4xl font-bold text-blue-500 mb-2">R$ 19,90</div>
                <div className="text-gray-400">por mês</div>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Pesca automática
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Skills F1-F6
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Suporte por Discord
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  1 conta simultânea
                </li>
              </ul>
              <Button 
                onClick={() => openPayment('basic', '19.90')}
                className="w-full bg-blue-500 hover:bg-blue-600"
              >
                Escolher Básico
              </Button>
            </div>

            {/* Premium Plan */}
            <div className="bg-slate-600/50 backdrop-blur-sm p-8 rounded-xl border-2 border-blue-500 relative hover:border-blue-400 transition">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 px-4 py-1 rounded-full text-sm font-semibold">
                Mais Popular
              </div>
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">Premium</h3>
                <div className="text-4xl font-bold text-blue-500 mb-2">R$ 39,90</div>
                <div className="text-gray-400">por mês</div>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Todos os recursos básicos
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Skills F1-F12 completas
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Detecção visual avançada
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  3 contas simultâneas
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Suporte prioritário
                </li>
              </ul>
              <Button 
                onClick={() => openPayment('premium', '39.90')}
                className="w-full bg-blue-500 hover:bg-blue-600"
              >
                Escolher Premium
              </Button>
            </div>

            {/* Pro Plan */}
            <div className="bg-slate-600/30 backdrop-blur-sm p-8 rounded-xl border border-slate-600 hover:border-green-500/50 transition">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">Profissional</h3>
                <div className="text-4xl font-bold text-green-500 mb-2">R$ 69,90</div>
                <div className="text-gray-400">por mês</div>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Todos os recursos premium
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Contas ilimitadas
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  API personalizada
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Scripts customizados
                </li>
                <li className="flex items-center text-gray-300">
                  <i className="fas fa-check text-green-500 mr-3"></i>
                  Suporte VIP 24/7
                </li>
              </ul>
              <Button 
                onClick={() => openPayment('pro', '69.90')}
                className="w-full bg-green-500 hover:bg-green-600"
              >
                Escolher Pro
              </Button>
            </div>
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-400 mb-4">💳 Pagamento via PIX, Cartão ou Boleto</p>
            <p className="text-gray-400">✅ Garantia de 7 dias ou seu dinheiro de volta</p>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-slate-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Suporte 24/7</h2>
          <p className="text-xl text-gray-300 mb-8">
            Nossa equipe está sempre disponível para ajudar você
          </p>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-600/30 p-6 rounded-xl">
              <div className="bg-blue-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <i className="fab fa-discord text-blue-500 text-xl"></i>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Discord</h3>
              <p className="text-gray-300 mb-4">Comunidade ativa com +2.000 membros</p>
              <Button variant="outline" className="border-blue-500 text-blue-400 hover:bg-blue-500 hover:text-white">
                Entrar no Discord
              </Button>
            </div>
            
            <div className="bg-slate-600/30 p-6 rounded-xl">
              <div className="bg-green-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <i className="fab fa-whatsapp text-green-500 text-xl"></i>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">WhatsApp</h3>
              <p className="text-gray-300 mb-4">Suporte direto via WhatsApp</p>
              <Button variant="outline" className="border-green-500 text-green-400 hover:bg-green-500 hover:text-white">
                Chamar no WhatsApp
              </Button>
            </div>
            
            <div className="bg-slate-600/30 p-6 rounded-xl">
              <div className="bg-purple-500/20 w-12 h-12 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <i className="fas fa-envelope text-purple-500 text-xl"></i>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Email</h3>
              <p className="text-gray-300 mb-4">suporte@rmbot.com.br</p>
              <Button variant="outline" className="border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-white">
                Enviar Email
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Modals */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
        onPaymentSuccess={() => setShowPaymentModal(true)}
      />
      
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        planType={selectedPlan.type}
        planPrice={selectedPlan.price}
      />
    </div>
  );
}
