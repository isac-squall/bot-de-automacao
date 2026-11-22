# 🤖 Bot de Automação Inteligente (Selenium & PyAutoGUI)

Um sistema completo, modular e profissional em Python desenvolvido para:
- 📨 **Enviar mensagens automaticamente** (com personalização e suporte a WhatsApp Web);
- 📝 **Preencher formulários web** automaticamente a partir de planilhas Excel/CSV;
- 🖥️ **Automatizar tarefas repetitivas no computador** (cliques, digitação rápida, macros e atalhos com PyAutoGUI);
- 🎨 **Interface Gráfica Moderna (GUI)** e **Menu Interativo via Terminal (CLI)**.

---

## 📁 Estrutura do Projeto

```
Bot de Automação/
│
├── config.py                     # Configurações globais (navegador, delays, failsafe)
├── requirements.txt              # Bibliotecas necessárias
├── main.py                       # Menu interativo no terminal (CLI)
├── gui.py                        # Painel gráfico moderno (CustomTkinter)
│
├── modules/                      # Núcleo modular do robô
│   ├── web_automator.py          # Preenchimento de formulários e navegação (Selenium)
│   ├── message_sender.py         # Envio de mensagens em massa (WhatsApp Web e Desktop)
│   └── desktop_automator.py      # Automação de mouse, teclado e macros (PyAutoGUI)
│
├── templates/
│   └── demo_form.html            # Formulário web moderno para testes locais imediatos
│
├── data/
│   ├── contatos_exemplo.csv      # Exemplo de contatos para envio de mensagens
│   └── cadastros_exemplo.csv     # Exemplo de clientes para preenchimento de formulários
│
├── screenshots/                  # Pasta onde são salvas as capturas de tela do bot
└── logs/                         # Histórico de execuções
```

---

## 🚀 Como Executar

### Opção 1: Abrir o Painel Gráfico (Recomendado)
Para uma experiência visual com botões, seletores de arquivos e barras de progresso:
```bash
python gui.py
```

### Opção 2: Executar pelo Terminal Interativo
Para navegar por um menu interativo colorido no console:
```bash
python main.py
```

---

## 🎯 As 3 Funcionalidades Principais

### 1. 📝 Preenchimento Automático de Formulários (Selenium)
- **Como funciona:** O robô lê uma planilha (CSV ou Excel) linha por linha e preenche todos os campos correspondentes no navegador (Nome, E-mail, Telefone, Dropdowns, Opções Radio e Caixas de Seleção).
- **Teste imediato sem internet:** O projeto inclui o arquivo [`templates/demo_form.html`](templates/demo_form.html). Você pode ver o bot preenchendo os dados e inserindo registros em tempo real!
- **Como usar no seu próprio formulário:**
  Abra [`modules/web_automator.py`](modules/web_automator.py) e use os métodos prontos:
  ```python
  from modules.web_automator import WebAutomator
  from selenium.webdriver.common.by import By

  bot = WebAutomator(headless=False)
  bot.abrir_pagina("https://seusite.com/formulario")
  bot.preencher_campo(By.NAME, "usuario", "meu_login")
  bot.preencher_campo(By.NAME, "senha", "minha_senha")
  bot.clicar_botao(By.ID, "btnEntrar")
  ```

---

### 2. 📨 Envio de Mensagens Automáticas (WhatsApp Web)
- **Como funciona:** Lê a lista [`data/contatos_exemplo.csv`](data/contatos_exemplo.csv) e gera mensagens personalizadas com variáveis (`{nome}`, `{pedido}`, `{status}`). Os registros incluídos são fictícios e não contêm destinatários reais.
- **Segurança e Humanização:** O bot possui delays configuráveis entre disparos para respeitar os limites de uso.
- **Sessão Salva:** Na primeira vez que usar, escaneie o QR Code no navegador. O perfil é salvo na pasta do projeto para não precisar escanear a cada disparo.
- **Modo Simulação / Prévia:** Permite visualizar exatamente o que seria enviado para cada cliente antes de iniciar qualquer disparo real.

---

### 3. 🖥️ Automação de Tarefas Repetitivas no Desktop (PyAutoGUI)
- **Controle de Mouse e Teclado:** Move o cursor, clica em posições específicas, digita textos e dispara atalhos do Windows (`Ctrl+C`, `Ctrl+V`, `Win+R`, `Alt+Tab`).
- **Demonstração Prática:** Inclui uma rotina que abre o Bloco de Notas (`Notepad`), digita um relatório de testes ao vivo e salva uma captura de tela na pasta `screenshots/`.
- **Localização de Elementos por Imagem:** O bot pode buscar botões ou ícones específicos na tela usando [`localizar_e_clicar_imagem()`](modules/desktop_automator.py).

> [!TIP]
> **Mecanismo de Parada de Emergência (Fail-Safe):**
> O PyAutoGUI possui um sistema de segurança ativo: se você quiser cancelar a automação a qualquer instante, **basta arrastar o cursor do mouse para o canto superior esquerdo da tela**. O robô interrompe a execução na hora.

---

## ⚙️ Configurações Customizáveis

Você pode ajustar parâmetros em [`config.py`](config.py):
- `headless`: `True` para rodar o navegador em segundo plano (invisível) ou `False` para acompanhar a tela.
- `delay_between_messages`: Tempo de espera entre cada mensagem enviada (padrão: 8 segundos).
- `pause`: Intervalo entre ações do mouse/teclado.
- `browser`: Escolha entre `"chrome"` ou `"edge"`.
