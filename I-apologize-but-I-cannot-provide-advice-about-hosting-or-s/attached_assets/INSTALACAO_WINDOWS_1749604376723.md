# RM Bot - Instalação no Windows

## Requisitos do Sistema
- Windows 10/11
- Python 3.8 ou superior
- Jogo Poke Old instalado

## Passo 1: Instalar Python

1. Baixe Python em: https://python.org/downloads/
2. Durante a instalação, marque "Add Python to PATH"
3. Termine a instalação

## Passo 2: Baixar o RM Bot

1. Baixe o arquivo `rm_bot_standalone.py` deste projeto
2. Crie uma pasta para o bot (ex: `C:\RM_Bot`)
3. Coloque o arquivo na pasta criada

## Passo 3: Instalar Dependências

Abra o Prompt de Comando (CMD) e execute:

```cmd
pip install customtkinter
pip install bcrypt
pip install pyautogui
pip install opencv-python
pip install psutil
pip install pywin32
```

Ou instale todas de uma vez usando o arquivo de requisitos:

```cmd
pip install -r requirements_windows.txt
```

## Passo 4: Executar o Bot

1. Navegue até a pasta do bot no CMD:
```cmd
cd C:\RM_Bot
```

2. Execute o bot:
```cmd
python rm_bot_standalone.py
```

## Como Usar

### 🔐 Sistema de Login
O RM Bot possui três tipos de interface:

#### 1. **Interface de Administrador**
- **Login:** `admin` / `admin123`
- Acesso completo ao sistema
- Pode gerenciar usuários e licenças
- Pode usar todas as funcionalidades do bot

#### 2. **Interface de Usuário VIP**
- Para usuários com licença ativa
- Acesso às funcionalidades de automação
- Interface simplificada e focada

#### 3. **Interface Bloqueada**
- Para usuários sem licença ou expirada
- Mostra informações sobre como ativar licença
- Sem acesso às funcionalidades do bot

### 📝 Cadastro de Novos Usuários
1. Na tela de login, clique em "Cadastrar"
2. Preencha os dados (usuário e senha)
3. **IMPORTANTE:** Novos usuários começam com 0 dias de licença
4. Apenas administradores podem ativar licenças

### 👑 Funcionalidades do Administrador

#### Gerenciar Usuários
- Criar novos usuários com ou sem licença
- Visualizar todos os usuários cadastrados
- Ver status de licenças em tempo real
- Deletar usuários inativos

#### Gerenciar Licenças
- Estender licença de usuários específicos
- Estender todas as licenças de uma vez
- Ver estatísticas gerais do sistema
- Limpar usuários com licenças expiradas

#### Opções de Tempo de Licença
- 7 dias, 30 dias, 90 dias, 365 dias
- Ou definir tempo personalizado
- Licenças se acumulam (não sobrescrevem)

### 🎮 Funcionalidades de Automação

#### 🎮 Seleção do Jogo
1. Abra o Poke Old e vá para uma área com água
2. No bot, clique em "Selecionar Jogo"
3. Escolha o processo do jogo na lista
4. O bot detectará automaticamente as áreas de água azul
5. Use "Re-detectar Água" se mudar de local

#### 🎣 Pesca Automática MELHORADA
1. **Primeiro selecione o processo do jogo**
2. Configure a velocidade (padrão: 1000ms)
3. Clique em "Iniciar Pesca"
4. **NOVO:** O bot segura a tecla ESPAÇO automaticamente
5. **NOVO:** Clica em pontos aleatórios nas áreas de água detectadas
6. **NOVO:** Variação humana nos cliques e tempos
7. **NOVO:** Re-detecção automática de água a cada 10 pescas

#### ⚔️ Skills Automáticas  
1. Selecione as skills F1-F12 que deseja usar
2. Configure o intervalo para cada skill
3. Clique em "Iniciar Skills"
4. Skills funcionam junto com a pesca

#### 📊 Estatísticas
- Veja quantos peixes foram pescados
- Acompanhe o tempo de uso
- Monitore skills utilizadas
- Status da licença em tempo real
- Áreas de água detectadas

## Configuração do Jogo

### Para Pesca:
1. Abra o Poke Old
2. Vá para uma área de pesca
3. Posicione o cursor sobre a água
4. Inicie a pesca no bot

### Para Skills:
1. Configure suas skills nas teclas F1-F12 no jogo
2. Skills de cura são recomendadas em F1-F4
3. Configure o bot para usar as skills desejadas

## Dicas de Uso

### Segurança:
- Use intervalos realistas (mínimo 500ms)
- Varie os tempos para parecer mais humano
- Não deixe o bot rodando por muito tempo seguido

### Performance:
- Feche outros programas pesados
- Mantenha o jogo em primeiro plano
- Use resolução menor para melhor performance

## Solução de Problemas

### "Automação indisponível"
Execute no CMD:
```cmd
pip install --upgrade pyautogui opencv-python psutil
```

### Bot não clica no local correto
1. Certifique-se que o jogo está em primeiro plano
2. Ajuste a resolução do jogo
3. Posicione a janela corretamente

### Skills não funcionam
1. Verifique se as teclas F1-F12 estão configuradas no jogo
2. Certifique-se que o jogo aceita as teclas
3. Teste manualmente primeiro

### Erro de banco de dados
- Delete o arquivo `rm_bot.db` e execute novamente
- O bot criará um novo banco automaticamente

## Recursos Avançados

### Sistema de Assinatura
- Login de admin tem acesso total
- Pode criar novos usuários no futuro
- Sistema preparado para expansão

### Logs e Monitoramento
- Todas as ações são registradas
- Estatísticas em tempo real
- Controle total sobre automações

## Aviso Legal

Este bot é para uso educacional e pessoal. Use com responsabilidade:

- Respeite os termos de serviço do jogo
- Use apenas em servidores que permitem automação
- Não venda ou distribua sem autorização
- Use por sua conta e risco

## Suporte

Para problemas ou dúvidas:
1. Verifique se todas as dependências estão instaladas
2. Certifique-se que o Python está na versão correta
3. Execute como administrador se necessário
4. Desative antivírus temporariamente se bloquear

---

**RM Bot v2.0 - Sistema de Automação para Poke Old**