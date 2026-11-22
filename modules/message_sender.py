import time
import urllib.parse
from pathlib import Path
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config
from modules.web_automator import WebAutomator

class MessageSender:
    """
    Classe para envio automatizado de mensagens em massa e personalizadas.
    Suporta envio via WhatsApp Web (Selenium) e disparo desktop (PyAutoGUI).
    """

    def __init__(self, web_automator=None):
        self.web = web_automator or WebAutomator(headless=False)
        self.delay = config.WHATSAPP_CONFIG.get("delay_between_messages", 8)

    def sanitizar_telefone(self, telefone):
        """Remove caracteres especiais e garante o formato internacional (ex: 5511999999999)."""
        tel_limpo = "".join(filter(str.isdigit, str(telefone)))
        if len(tel_limpo) in [10, 11]:
            # Adiciona DDI do Brasil (55) se não estiver presente
            tel_limpo = "55" + tel_limpo
        return tel_limpo

    def formatar_mensagem(self, template, dados_linha):
        """Substitui variáveis como {nome}, {pedido}, {status} na mensagem."""
        try:
            return template.format(**dados_linha)
        except KeyError as e:
            # Se faltar alguma chave, tenta substituição tolerante
            msg = template
            for col, val in dados_linha.items():
                msg = msg.replace(f"{{{col}}}", str(val))
            return msg

    def previsualizar_envios(self, caminho_csv=None, template=None):
        """Gera uma prévia das mensagens que seriam enviadas a partir da planilha."""
        caminho_csv = caminho_csv or config.CONTATOS_CSV
        template = template or "Olá {nome}! Seu pedido {pedido} está com status: *{status}*."

        df = pd.read_csv(caminho_csv)
        previa = []
        for _, row in df.iterrows():
            tel = self.sanitizar_telefone(row.get("telefone", ""))
            msg = self.formatar_mensagem(template, row.to_dict())
            previa.append({"nome": row.get("nome"), "telefone": tel, "mensagem": msg})
        return previa

    def enviar_whatsapp_web(self, telefone, mensagem, aguardar_login=False):
        """
        Envia uma mensagem individual via WhatsApp Web utilizando Selenium.
        """
        driver = self.web.iniciar_navegador()
        tel_limpo = self.sanitizar_telefone(telefone)
        msg_encoded = urllib.parse.quote(mensagem)
        url = f"https://web.whatsapp.com/send?phone={tel_limpo}&text={msg_encoded}"

        print(f"📱 Abrindo conversa com {tel_limpo}...")
        driver.get(url)

        if aguardar_login:
            print("⏳ Se for o primeiro acesso, escaneie o QR Code na tela...")
            time.sleep(config.WHATSAPP_CONFIG.get("login_wait_seconds", 25))

        try:
            # Aguarda a caixa de texto ou botão de envio ficar disponível
            time.sleep(4)
            xpath_botao_enviar = "//span[@data-icon='send']/parent::button | //button[@aria-label='Enviar' or @aria-label='Send']"
            
            try:
                botao_enviar = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_botao_enviar))
                )
                botao_enviar.click()
            except Exception:
                # Fallback: clica na caixa de texto e pressiona ENTER
                xpath_caixa = "//div[@contenteditable='true'][@data-tab='10']"
                caixa = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_caixa))
                )
                caixa.send_keys(Keys.ENTER)

            print(f"✅ Mensagem enviada para {tel_limpo}!")
            time.sleep(2)
            return True

        except Exception as e:
            print(f"⚠️ Erro ao enviar para {tel_limpo}: {e}")
            return False

    def disparar_lote_whatsapp(self, caminho_csv=None, template=None, modo_simulacao=False, callback_progresso=None):
        """
        Processa uma lista de contatos e dispara as mensagens personalizadas.
        Se modo_simulacao=True, apenas simula e exibe o que seria enviado.
        """
        caminho_csv = caminho_csv or config.CONTATOS_CSV
        template = template or "Olá {nome}! Seu pedido {pedido} foi atualizado para: *{status}*."

        df = pd.read_csv(caminho_csv)
        total = len(df)
        print(f"\n📨 Iniciando processamento de {total} mensagens (Modo Simulação: {modo_simulacao})...")

        sucessos = 0
        erros = 0

        for index, row in df.iterrows():
            tel = self.sanitizar_telefone(row.get("telefone", ""))
            nome = row.get("nome", "Cliente")
            msg = self.formatar_mensagem(template, row.to_dict())

            progresso_msg = f"[{index + 1}/{total}] Para: {nome} ({tel}) -> {msg[:45]}..."
            print(progresso_msg)
            if callback_progresso:
                callback_progresso(index + 1, total, progresso_msg)

            if modo_simulacao:
                time.sleep(0.5)
                sucessos += 1
            else:
                primeiro = (index == 0)
                enviado = self.enviar_whatsapp_web(tel, msg, aguardar_login=primeiro)
                if enviado:
                    sucessos += 1
                else:
                    erros += 1

                # Delay humanizado entre disparos para segurança
                if index + 1 < total:
                    print(f"⏳ Aguardando {self.delay} segundos antes do próximo envio...")
                    time.sleep(self.delay)

        resultado = f"🏁 Disparo concluído! Sucessos: {sucessos} | Falhas: {erros}"
        print(f"\n{resultado}")
        if callback_progresso:
            callback_progresso(total, total, resultado)
        return {"total": total, "sucessos": sucessos, "erros": erros}

    def disparar_desktop_pyautogui(self, mensagem, app_posicao=None):
        """
        Dispara mensagem em qualquer aplicativo aberto no desktop usando PyAutoGUI.
        (ex: WhatsApp Desktop, Telegram, Discord, Teams, Bloco de Notas).
        """
        import pyautogui
        pyautogui.FAILSAFE = config.PYAUTOGUI_CONFIG.get("failsafe", True)

        if app_posicao:
            pyautogui.click(app_posicao[0], app_posicao[1])
            time.sleep(0.3)

        # Digita a mensagem com segurança e pressiona Enter
        pyautogui.write(mensagem, interval=config.PYAUTOGUI_CONFIG.get("typing_interval", 0.05))
        pyautogui.press("enter")
        print("✅ Mensagem digitada e enviada via Desktop!")
