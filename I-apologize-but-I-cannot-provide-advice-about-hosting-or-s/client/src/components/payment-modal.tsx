import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/api';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  planType: 'basic' | 'premium' | 'pro';
  planPrice: string;
}

const planNames = {
  basic: 'Básico',
  premium: 'Premium',
  pro: 'Profissional'
};

export function PaymentModal({ isOpen, onClose, planType, planPrice }: PaymentModalProps) {
  const [paymentMethod, setPaymentMethod] = useState<'pix' | 'card' | 'boleto'>('pix');
  const [isLoading, setIsLoading] = useState(false);
  const [paymentData, setPaymentData] = useState<any>(null);
  const { toast } = useToast();

  const createPayment = async () => {
    setIsLoading(true);
    try {
      const response = await apiRequest('POST', '/api/payments/create', {
        planType,
        paymentMethod
      });
      
      const data = await response.json();
      setPaymentData(data);
      
      toast({
        title: "Pagamento criado",
        description: "Use o código PIX para finalizar o pagamento",
      });
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.message || "Erro ao criar pagamento",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const simulatePayment = async () => {
    if (!paymentData) return;
    
    setIsLoading(true);
    try {
      await apiRequest('POST', `/api/payments/${paymentData.paymentId}/complete`);
      
      toast({
        title: "Pagamento confirmado!",
        description: "Sua licença foi ativada com sucesso!",
      });
      
      onClose();
      // Refresh the page to update subscription status
      window.location.reload();
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error.message || "Erro ao confirmar pagamento",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyPixCode = () => {
    if (paymentData?.pixCode) {
      navigator.clipboard.writeText(paymentData.pixCode);
      toast({
        title: "Copiado!",
        description: "Código PIX copiado para a área de transferência",
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg bg-slate-800 border-slate-700">
        <DialogHeader>
          <DialogTitle className="text-center text-white">
            <div className="flex flex-col items-center mb-4">
              <div className="bg-blue-500 p-3 rounded-lg mb-4">
                <i className="fas fa-credit-card text-white text-2xl"></i>
              </div>
              Finalizar Pagamento
            </div>
            <div className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-lg inline-block">
              <span className="font-semibold">Plano {planNames[planType]} - R$ {planPrice}/mês</span>
            </div>
          </DialogTitle>
        </DialogHeader>

        {!paymentData ? (
          <div className="space-y-6">
            {/* Payment Methods */}
            <div className="grid grid-cols-3 gap-4">
              <Button
                variant={paymentMethod === 'pix' ? 'default' : 'outline'}
                onClick={() => setPaymentMethod('pix')}
                className={`py-6 flex flex-col space-y-2 ${
                  paymentMethod === 'pix' 
                    ? 'bg-green-500 hover:bg-green-600 text-white' 
                    : 'bg-slate-700 hover:bg-slate-600 text-gray-300'
                }`}
              >
                <i className="fas fa-qrcode text-xl"></i>
                <div className="text-sm font-medium">PIX</div>
              </Button>
              <Button
                variant={paymentMethod === 'card' ? 'default' : 'outline'}
                onClick={() => setPaymentMethod('card')}
                className={`py-6 flex flex-col space-y-2 ${
                  paymentMethod === 'card' 
                    ? 'bg-blue-500 hover:bg-blue-600 text-white' 
                    : 'bg-slate-700 hover:bg-slate-600 text-gray-300'
                }`}
              >
                <i className="fas fa-credit-card text-xl"></i>
                <div className="text-sm font-medium">Cartão</div>
              </Button>
              <Button
                variant={paymentMethod === 'boleto' ? 'default' : 'outline'}
                onClick={() => setPaymentMethod('boleto')}
                className={`py-6 flex flex-col space-y-2 ${
                  paymentMethod === 'boleto' 
                    ? 'bg-yellow-500 hover:bg-yellow-600 text-white' 
                    : 'bg-slate-700 hover:bg-slate-600 text-gray-300'
                }`}
              >
                <i className="fas fa-barcode text-xl"></i>
                <div className="text-sm font-medium">Boleto</div>
              </Button>
            </div>

            {/* Order Summary */}
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-300">Plano {planNames[planType]} (1 mês)</span>
                <span className="text-white">R$ {planPrice}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-300">Desconto primeiro mês</span>
                <span className="text-green-400">-R$ 20,00</span>
              </div>
              <div className="border-t border-slate-600 pt-2">
                <div className="flex justify-between items-center">
                  <span className="text-white font-semibold">Total</span>
                  <span className="text-green-400 font-bold text-xl">R$ {(parseFloat(planPrice) - 20).toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="text-center text-sm text-gray-400 mb-4">
              ✅ Ativação imediata após confirmação do pagamento<br/>
              📧 Instruções enviadas por email automaticamente
            </div>

            <Button 
              onClick={createPayment} 
              className="w-full bg-green-500 hover:bg-green-600" 
              disabled={isLoading}
            >
              {isLoading ? 'Criando pagamento...' : 'Criar Pagamento PIX'}
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* PIX Payment Display */}
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-6">
              <div className="text-center">
                <div className="bg-white p-4 rounded-lg inline-block mb-4">
                  <div className="w-32 h-32 bg-gray-800 rounded flex items-center justify-center">
                    <i className="fas fa-qrcode text-4xl text-gray-600"></i>
                  </div>
                </div>
                <p className="text-green-400 font-medium mb-2">Escaneie o QR Code com seu banco</p>
                <p className="text-sm text-gray-300 mb-4">Ou copie o código PIX abaixo:</p>
                <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-3 text-sm font-mono text-gray-300 break-all">
                  {paymentData.pixCode}
                </div>
                <Button
                  onClick={copyPixCode}
                  className="mt-3 bg-green-500/20 hover:bg-green-500/30 text-green-400"
                >
                  <i className="fas fa-copy mr-2"></i>
                  Copiar Código PIX
                </Button>
              </div>
            </div>

            {/* Simulate payment button for demo */}
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
              <p className="text-yellow-400 text-sm mb-3">
                <i className="fas fa-info-circle mr-2"></i>
                Demo: Clique abaixo para simular o pagamento
              </p>
              <Button
                onClick={simulatePayment}
                className="w-full bg-yellow-500 hover:bg-yellow-600 text-black"
                disabled={isLoading}
              >
                {isLoading ? 'Processando...' : 'Simular Pagamento Confirmado'}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
