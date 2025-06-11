# RM Bot - Plataforma de Comercialização

Plataforma web completa para venda de licenças do RM Bot para Poke Old.

## 🚀 Deploy no Vercel (GRATUITO)

### 1. Preparar o Repositório
```bash
# Baixe este projeto do Replit
# Crie um repositório no GitHub
# Faça upload dos arquivos
```

### 2. Configurar Banco de Dados (Neon - GRATUITO)
1. Acesse [neon.tech](https://neon.tech)
2. Crie uma conta gratuita
3. Crie um novo projeto
4. Copie a URL de conexão

### 3. Deploy no Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Conecte com GitHub
3. Importe seu repositório
4. Configure as variáveis de ambiente:
   - `DATABASE_URL`: sua URL do Neon
   - `SESSION_SECRET`: uma senha forte qualquer
   - `NODE_ENV`: production

### 4. Primeira Execução
Após o deploy, acesse seu site e:
1. Faça login como admin: `admin` / `admin123`
2. O banco será criado automaticamente
3. Personalize preços e configurações

## 🔧 Estrutura do Projeto

```
├── client/          # Frontend React
├── server/          # Backend Express
├── shared/          # Schemas compartilhados
├── vercel.json      # Configuração Vercel
└── README.md        # Este arquivo
```

## 💾 Banco de Dados

O sistema usa PostgreSQL com as seguintes tabelas:
- `users` - Usuários da plataforma
- `subscriptions` - Licenças ativas
- `payments` - Histórico de pagamentos
- `bot_sessions` - Sessões de uso do bot

## 🔑 Administração

**Login Admin:** admin / admin123

**Funcionalidades:**
- Gerenciar usuários
- Estender licenças
- Ver estatísticas
- Controlar pagamentos

## 💳 Pagamentos

Por padrão usa simulação PIX. Para pagamento real:
1. Configure Mercado Pago
2. Adicione `MERCADOPAGO_ACCESS_TOKEN`
3. Edite `server/routes.ts` linha 168

## 🤖 Integração com Bot

O bot Python deve validar licenças:
```python
import requests

def validate_license(key):
    response = requests.post('https://seu-site.vercel.app/api/bot/validate-license', {
        'license_key': key
    })
    return response.status_code == 200
```

## 📱 Personalização

**Preços:** `client/src/pages/landing.tsx`
**Cores:** `client/src/index.css`
**Textos:** Arquivos em `client/src/pages/`

## 🔄 Atualizações

1. Edite os arquivos
2. Commit no GitHub
3. Vercel faz deploy automático

## 📞 Suporte

- Discord: Configurar link real
- WhatsApp: Editar número em `client/index.html`
- Email: Adicionar formulário de contato