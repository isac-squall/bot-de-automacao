import os
import sys
from pathlib import Path

# Garante suporte a UTF-8 (emojis e caracteres especiais) no terminal Windows
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ==============================================================================
# DIRETÓRIOS BASE DO PROJETO
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"

# Garante que os diretórios existem
for directory in [DATA_DIR, TEMPLATES_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Caminhos de arquivos padrão
DEMO_FORM_PATH = TEMPLATES_DIR / "demo_form.html"
CONTATOS_CSV = DATA_DIR / "contatos_exemplo.csv"
CADASTROS_CSV = DATA_DIR / "cadastros_exemplo.csv"

# ==============================================================================
# CONFIGURAÇÕES DE NAVEGADOR & SELENIUM
# ==============================================================================
SELENIUM_CONFIG = {
    "headless": False,             # False para você acompanhar visualmente o bot trabalhando
    "timeout": 15,                 # Tempo máximo de espera explícita por elementos (segundos)
    "browser": "chrome",           # "chrome" ou "edge"
    "user_data_dir": str(BASE_DIR / ".chrome_profile"), # Salva sessão (ex: login WhatsApp)
}

# ==============================================================================
# CONFIGURAÇÕES DO PYAUTOGUI (AUTOMAÇÃO DESKTOP)
# ==============================================================================
PYAUTOGUI_CONFIG = {
    "failsafe": True,              # SEGURANÇA: Mover o mouse para o canto superior esquerdo para o bot
    "pause": 0.5,                  # Intervalo padrão entre cada ação do mouse/teclado (segundos)
    "typing_interval": 0.05,       # Velocidade de digitação por tecla
}

# ==============================================================================
# CONFIGURAÇÕES DE ENVIO DE MENSAGENS (WHATSAPP WEB)
# ==============================================================================
WHATSAPP_CONFIG = {
    "login_wait_seconds": 30,      # Tempo para o usuário escanear o QR Code no primeiro uso
    "delay_between_messages": 8,   # Delay humanizado entre disparos para segurança
    "confirm_before_send": True,   # Pedir confirmação antes de disparar lista
}
