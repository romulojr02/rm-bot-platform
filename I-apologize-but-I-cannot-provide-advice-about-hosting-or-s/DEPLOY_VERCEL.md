# 🚀 Deploy RM Bot no Vercel - PASSO A PASSO

## ✅ PASSO 1: Baixar o Projeto

1. **No Replit atual:** Clique nos 3 pontos (...) → "Download as ZIP"
2. **Extraia** os arquivos em uma pasta no seu computador
3. **Delete** a pasta `node_modules` se existir

## ✅ PASSO 2: Criar Repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique em "New repository"
3. Nome: `rm-bot-platform`
4. Marque "Public" (gratuito)
5. Clique "Create repository"

6. **Subir arquivos:**
   - Clique "uploading an existing file"
   - Arraste TODOS os arquivos do projeto
   - Commit: "Initial commit"

## ✅ PASSO 3: Banco de Dados Gratuito (Neon)

1. Acesse [neon.tech](https://neon.tech)
2. Clique "Sign Up" → Conecte com GitHub
3. "Create your first project"
4. Nome: `rm-bot-db`
5. Região: escolha mais próxima
6. **COPIE** a Connection String que aparece

## ✅ PASSO 4: Deploy no Vercel

1. Acesse [vercel.com](https://vercel.com)
2. "Continue with GitHub"
3. "Import" seu repositório `rm-bot-platform`
4. **Framework:** Detect automatically
5. **Root Directory:** deixe vazio

### Configurar Variáveis de Ambiente:
```
DATABASE_URL = sua_connection_string_do_neon
SESSION_SECRET = MinhaChaveSecreta123!@#
NODE_ENV = production
```

6. Clique "Deploy"

## ✅ PASSO 5: Primeiro Acesso

1. Aguarde 2-3 minutos (deploy automático)
2. Clique no link gerado (ex: `rm-bot-platform.vercel.app`)
3. **Login admin:** `admin` / `admin123`
4. Sistema criará tabelas automaticamente

## 🎯 CONFIGURAÇÕES PÓS-DEPLOY

### Personalizar Domínio (Opcional):
1. No Vercel: "Settings" → "Domains"
2. Adicione seu domínio próprio
3. Configure DNS conforme instruído

### Testar Pagamentos:
1. Crie uma conta de teste
2. Simule compra de licença
3. Verifique no painel admin

### Configurar WhatsApp:
- Edite `client/index.html` linha 126
- Troque pelo seu número

## 🔧 COMANDOS ÚTEIS

**Atualizar projeto:**
1. Edite arquivos no GitHub
2. Vercel faz deploy automático

**Ver logs:**
- Vercel → seu projeto → "Functions"

**Backup banco:**
- Neon → Database → "Backup"

## 💰 CUSTOS

- **Vercel:** Gratuito (até 100GB bandwidth)
- **Neon:** Gratuito (até 3GB storage)
- **GitHub:** Gratuito (repositório público)
- **Total:** R$ 0,00/mês

## 🆘 PROBLEMAS COMUNS

**Build Error:**
- Verifique se todos arquivos foram enviados
- Certifique que DATABASE_URL está configurada

**Banco não conecta:**
- Confirme CONNECTION_STRING do Neon
- Teste conexão no painel Neon

**Login admin não funciona:**
- Aguarde 5 minutos após primeiro deploy
- Limpe cache do navegador

## 🎉 PRONTO!

Seu RM Bot está online em: `https://seu-projeto.vercel.app`

**Próximos passos:**
1. Personalizar preços e textos
2. Configurar pagamento real (Mercado Pago)
3. Subir seu bot Python com validação online
4. Divulgar e vender licenças!

**URLs importantes:**
- Site: https://seu-projeto.vercel.app
- Admin: https://seu-projeto.vercel.app (login: admin/admin123)
- Banco: https://console.neon.tech