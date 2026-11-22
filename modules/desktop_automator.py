import time
import os
from datetime import datetime
from pathlib import Path
import config

class DesktopAutomator:
    """
    Classe para automação de tarefas repetitivas no computador (Desktop)
    utilizando PyAutoGUI (controle de mouse, teclado, atalhos e reconhecimento de tela).
    """

    def __init__(self):
        self._inicializar_pyautogui()

    def _inicializar_pyautogui(self):
        """Configurações de segurança e delays do PyAutoGUI."""
        try:
            import pyautogui
            self.pyautogui = pyautogui
            # Failsafe: Arrastar o mouse para o canto superior esquerdo para a execução imediatamente
            self.pyautogui.FAILSAFE = config.PYAUTOGUI_CONFIG.get("failsafe", True)
            self.pyautogui.PAUSE = config.PYAUTOGUI_CONFIG.get("pause", 0.5)
            self.disponivel = True
        except ImportError:
            self.pyautogui = None
            self.disponivel = False
            print("⚠️ A biblioteca PyAutoGUI ainda não está disponível ou está sendo instalada.")

    def verificar_disponibilidade(self):
        if not self.pyautogui:
            self._inicializar_pyautogui()
        if not self.disponivel:
            raise RuntimeError("PyAutoGUI não está instalado. Execute: pip install pyautogui")

    def obter_resolucao(self):
        """Retorna a largura e altura da tela atual."""
        self.verificar_disponibilidade()
        tamanho = self.pyautogui.size()
        return tamanho.width, tamanho.height

    def obter_posicao_atual(self):
        """Retorna as coordenadas (x, y) atuais do mouse."""
        self.verificar_disponibilidade()
        pos = self.pyautogui.position()
        return pos.x, pos.y

    def mover_mouse(self, x, y, duracao=0.5):
        """Move o cursor do mouse suavemente até a coordenada (x, y)."""
        self.verificar_disponibilidade()
        print(f"🖱️ Movendo mouse para ({x}, {y}) em {duracao}s...")
        self.pyautogui.moveTo(x, y, duration=duracao)

    def clicar(self, x=None, y=None, cliques=1, botao="left"):
        """Executa clique do mouse em uma posição específica ou na posição atual."""
        self.verificar_disponibilidade()
        if x is not None and y is not None:
            self.pyautogui.click(x=x, y=y, clicks=cliques, button=botao)
        else:
            self.pyautogui.click(clicks=cliques, button=botao)
        print(f"🖱️ Clique ({botao}, {cliques}x) executado.")

    def digitar_texto(self, texto, intervalo=None):
        """Digita um texto caractere por caractere simulando digitação humana."""
        self.verificar_disponibilidade()
        vel = intervalo or config.PYAUTOGUI_CONFIG.get("typing_interval", 0.05)
        print(f"⌨️ Digitando: '{texto[:30]}...' (vel: {vel}s)")
        self.pyautogui.write(texto, interval=vel)

    def pressionar_tecla(self, tecla):
        """Pressiona uma tecla específica (ex: 'enter', 'tab', 'esc', 'backspace')."""
        self.verificar_disponibilidade()
        self.pyautogui.press(tecla)

    def pressionar_atalho(self, *teclas):
        """Pressiona uma combinação de teclas (ex: 'ctrl', 'c' ou 'win', 'r')."""
        self.verificar_disponibilidade()
        print(f"⌨️ Atalho: {' + '.join(teclas)}")
        self.pyautogui.hotkey(*teclas)

    def tirar_screenshot(self, nome_arquivo=None):
        """Captura a tela atual e salva na pasta de screenshots."""
        self.verificar_disponibilidade()
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"screenshot_{timestamp}.png"

        caminho = config.SCREENSHOTS_DIR / nome_arquivo
        try:
            img = self.pyautogui.screenshot()
            img.save(str(caminho))
            print(f"📸 Screenshot salva em: {caminho}")
            return str(caminho)
        except OSError as e:
            print(f"⚠️ Não foi possível capturar a tela (sessão gráfica em espera/bloqueada): {e}")
            return None

    def localizar_e_clicar_imagem(self, caminho_imagem, confianca=0.8, timeout=5):
        """
        Localiza um botão/ícone na tela a partir de uma imagem de referência e clica nele.
        Requer 'opencv-python' para suporte ao parâmetro de confiança.
        """
        self.verificar_disponibilidade()
        print(f"🔍 Procurando imagem '{Path(caminho_imagem).name}' na tela...")
        inicio = time.time()
        while time.time() - inicio < timeout:
            try:
                pos = self.pyautogui.locateCenterOnScreen(str(caminho_imagem), confidence=confianca)
                if pos:
                    print(f"🎯 Imagem encontrada em ({pos.x}, {pos.y})! Clicando...")
                    self.pyautogui.click(pos.x, pos.y)
                    return True
            except Exception:
                pass
            time.sleep(0.5)

        print(f"❌ Imagem não encontrada na tela após {timeout}s.")
        return False

    def executar_demonstracao_bloco_de_notas(self, callback_progresso=None):
        """
        Executa uma demonstração prática e segura de automação desktop:
        1. Abre o Executar (Win + R)
        2. Abre o Bloco de Notas (notepad)
        3. Digita automaticamente um relatório de teste gerado pelo robô
        4. Demonstra atalhos, quebra de linha e digitação contínua.
        """
        self.verificar_disponibilidade()

        passos = [
            ("Pressionando Win + R para abrir o 'Executar'...", lambda: self.pressionar_atalho("win", "r")),
            ("Digitando 'notepad' e abrindo o Bloco de Notas...", lambda: (time.sleep(0.6), self.digitar_texto("notepad", 0.05), self.pressionar_tecla("enter"))),
            ("Aguardando janela do Bloco de Notas abrir...", lambda: time.sleep(1.2)),
            ("Digitando cabeçalho da automação...", lambda: self.digitar_texto("=== RELATORIO DE TESTE DO ROBO DE AUTOMACAO ===\n\n", 0.03)),
            ("Escrevendo dados e estatisticas...", lambda: self.digitar_texto(
                f"Data e Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Resolucao de Tela: {self.obter_resolucao()[0]}x{self.obter_resolucao()[1]}\n"
                "Status: Bot de Automacao Operacional com Sucesso!\n"
                "Bibliotecas ativas: Selenium, PyAutoGUI, Pandas.\n"
                "--------------------------------------------------\n"
                "Automatizando tarefas repetitivas sem esforco!\n\n", 0.02
            )),
            ("Capturando tela da automação finalizada...", lambda: self.tirar_screenshot("demonstracao_desktop.png")),
        ]

        total = len(passos)
        for i, (descricao, acao) in enumerate(passos, 1):
            print(f"[{i}/{total}] {descricao}")
            if callback_progresso:
                callback_progresso(i, total, descricao)
            acao()
            time.sleep(0.6)

        msg_final = "✅ Demonstração de automação Desktop concluída com sucesso!"
        print(msg_final)
        if callback_progresso:
            callback_progresso(total, total, msg_final)
        return True
