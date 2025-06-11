import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/use-auth';
import { useQuery } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

export function BotDownload() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [downloading, setDownloading] = useState(false);

  const { data: subscription } = useQuery({
    queryKey: ['/api/user/subscription'],
  });

  const isActive = subscription && new Date(subscription.expiresAt) > new Date();

  const downloadBot = async () => {
    if (!isActive) {
      toast({
        title: "Licença necessária",
        description: "Você precisa de uma licença ativa para baixar o bot",
        variant: "destructive",
      });
      return;
    }

    setDownloading(true);
    try {
      const response = await fetch('/api/bot/download', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'RM_Bot_v2.0.exe';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        toast({
          title: "Download iniciado",
          description: "O RM Bot está sendo baixado...",
        });
      }
    } catch (error) {
      toast({
        title: "Erro no download",
        description: "Tente novamente em alguns momentos",
        variant: "destructive",
      });
    } finally {
      setDownloading(false);
    }
  };

  const generateLicenseKey = () => {
    return subscription?.licenseKey || 'XXXXX-XXXXX-XXXXX-XXXXX';
  };

  return (
    <div className="min-h-screen bg-slate-700 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Download do RM Bot</h1>
          <p className="text-gray-400">Baixe e configure seu bot de automação</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Download Section */}
          <Card className="bg-slate-600/30 border-slate-600">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <i className="fas fa-download mr-3 text-blue-500"></i>
                Download do Bot
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-800/50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-white font-semibold">RM Bot v2.0</h3>
                    <p className="text-gray-400 text-sm">Versão mais recente</p>
                  </div>
                  <div className="text-right">
                    <div className="text-green-400 font-semibold">15.2 MB</div>
                    <div className="text-gray-400 text-sm">Windows 10/11</div>
                  </div>
                </div>
                
                <Button
                  onClick={downloadBot}
                  disabled={!isActive || downloading}
                  className={`w-full ${isActive ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-600 cursor-not-allowed'}`}
                >
                  {downloading ? (
                    <>
                      <i className="fas fa-spinner fa-spin mr-2"></i>
                      Baixando...
                    </>
                  ) : isActive ? (
                    <>
                      <i className="fas fa-download mr-2"></i>
                      Baixar RM Bot
                    </>
                  ) : (
                    <>
                      <i className="fas fa-lock mr-2"></i>
                      Licença Necessária
                    </>
                  )}
                </Button>
              </div>

              {isActive && (
                <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-lg">
                  <h4 className="text-green-400 font-semibold mb-2">Sua Chave de Licença:</h4>
                  <div className="bg-slate-800/50 p-3 rounded font-mono text-sm text-white break-all">
                    {generateLicenseKey()}
                  </div>
                  <p className="text-green-400 text-sm mt-2">
                    <i className="fas fa-info-circle mr-1"></i>
                    Use esta chave para ativar o bot
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Instructions */}
          <Card className="bg-slate-600/30 border-slate-600">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <i className="fas fa-book mr-3 text-green-500"></i>
                Como Instalar
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold">1</div>
                  <div>
                    <p className="text-white font-medium">Baixe o arquivo</p>
                    <p className="text-gray-400 text-sm">Clique no botão de download acima</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold">2</div>
                  <div>
                    <p className="text-white font-medium">Execute como administrador</p>
                    <p className="text-gray-400 text-sm">Clique com botão direito → "Executar como administrador"</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold">3</div>
                  <div>
                    <p className="text-white font-medium">Insira sua chave de licença</p>
                    <p className="text-gray-400 text-sm">Cole a chave mostrada acima na primeira execução</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold">4</div>
                  <div>
                    <p className="text-white font-medium">Configure e use</p>
                    <p className="text-gray-400 text-sm">Abra o Poke Old e configure as automações</p>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-lg mt-6">
                <h4 className="text-yellow-400 font-semibold mb-2">
                  <i className="fas fa-exclamation-triangle mr-2"></i>
                  Requisitos do Sistema
                </h4>
                <ul className="text-yellow-400 text-sm space-y-1">
                  <li>• Windows 10 ou superior</li>
                  <li>• Python 3.8+ (instalado automaticamente)</li>
                  <li>• Conexão com internet para validação</li>
                  <li>• Poke Old instalado</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Version History */}
        <Card className="bg-slate-600/30 border-slate-600 mt-6">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <i className="fas fa-history mr-3 text-purple-500"></i>
              Histórico de Versões
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-white font-semibold">v2.0 - Atual</h4>
                  <span className="text-gray-400 text-sm">11/06/2025</span>
                </div>
                <ul className="text-gray-300 text-sm mt-2 space-y-1">
                  <li>• Nova interface com abas organizadas</li>
                  <li>• Sistema de detecção visual melhorado</li>
                  <li>• Anti-detecção aprimorado</li>
                  <li>• Verificação de licença online</li>
                </ul>
              </div>

              <div className="border-l-4 border-gray-500 pl-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-gray-400 font-semibold">v1.5</h4>
                  <span className="text-gray-400 text-sm">28/05/2025</span>
                </div>
                <ul className="text-gray-400 text-sm mt-2 space-y-1">
                  <li>• Correções de bugs na pesca automática</li>
                  <li>• Melhorias na calibração de cores</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}