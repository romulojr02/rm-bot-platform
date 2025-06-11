# 🎯 Guia de Calibração - RM Bot

## Métodos de Detecção de Água

### 1. MÉTODO SIMPLES (Recomendado)
**Mais fácil e funcional**

1. Abra o Poke Old em área de pesca
2. Selecione o processo do jogo no bot
3. Clique em "Calibrar Áreas de Pesca"
4. Escolha opção "2" - Detecção automática por cor
5. Posicione o mouse sobre um quadrado de água azul
6. Pressione ENTER
7. Aguarde 3 segundos - sistema captura automaticamente
8. Pronto! O bot detecta todas as áreas similares

### 2. MARCAÇÃO MANUAL
**Para controle total**

1. Escolha opção "1" no menu de calibração
2. Tenha o jogo visível em área de pesca
3. Pressione ENTER quando pronto
4. Clique em 3-8 pontos diferentes onde quer pescar
5. Sistema salva os pontos exatos

### 3. CARREGAR CONFIGURAÇÃO
**Para reusar configurações anteriores**

1. Escolha opção "3" no menu
2. Selecione qual configuração carregar
3. Sistema restaura automaticamente

## Dicas Importantes

- Use áreas de água bem visíveis (azul claro)
- Evite bordas ou transições de cor
- Para melhor resultado, use água em mar aberto
- Configurações são salvas automaticamente
- Pode alternar entre diferentes configurações

## Arquivos Gerados

- `simple_fishing.json` - Configuração do método simples
- `fishing_points.json` - Pontos marcados manualmente  
- `water_reference.json` - Configuração OpenCV avançada

## Solução de Problemas

**Não detecta água:**
- Tente capturar cor em área mais clara
- Use método manual para pontos específicos
- Verifique se o jogo está em primeiro plano

**Pesca em local errado:**
- Recalibre usando método simples
- Marque pontos manualmente para precisão total
- Certifique-se que a janela do jogo não mudou de tamanho