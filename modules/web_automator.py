import time
import os
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import config

class WebAutomator:
    """
    Classe responsável pelo gerenciamento do navegador e preenchimento
    automático de formulários web utilizando Selenium.
    """

    def __init__(self, headless=False, browser="chrome"):
        self.headless = headless
        self.browser_name = browser.lower()
        self.driver = None
        self.timeout = config.SELENIUM_CONFIG.get("timeout", 15)

    def iniciar_navegador(self):
        """Inicializa a instância do navegador configurado."""
        if self.driver:
            return self.driver

        print(f"🚀 Iniciando navegador ({self.browser_name.upper()})...")

        if self.browser_name == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e:
                print(f"⚠️ Tentativa direta falhou ({e}), tentando com WebDriver Manager...")
                try:
                    service = ChromeService(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as e2:
                    print(f"⚠️ Chrome falhou ({e2}), tentando com Microsoft Edge...")
                    options_edge = EdgeOptions()
                    if self.headless:
                        options_edge.add_argument("--headless=new")
                    self.driver = webdriver.Edge(options=options_edge)

        elif self.browser_name == "edge":
            options = EdgeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            try:
                self.driver = webdriver.Edge(options=options)
            except Exception as e:
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
        else:
            raise ValueError(f"Navegador '{self.browser_name}' não suportado. Use 'chrome' ou 'edge'.")

        self.driver.implicitly_wait(2)
        print("✅ Navegador iniciado com sucesso!")
        return self.driver

    def fechar_navegador(self):
        """Fecha o navegador e encerra a sessão do WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            print("🛑 Navegador encerrado.")

    def abrir_pagina(self, url):
        """Abre uma URL (suporta URLs web http/https e arquivos locais file:///)."""
        if not self.driver:
            self.iniciar_navegador()
        
        # Converte caminho local para URI caso seja arquivo local
        if isinstance(url, Path) or (isinstance(url, str) and os.path.exists(url)):
            url = Path(url).resolve().as_uri()

        print(f"🌐 Acessando: {url}")
        self.driver.get(url)

    def esperar_elemento(self, by, seletor, tempo=None):
        """Aguarda a presença e visibilidade de um elemento na tela."""
        t = tempo or self.timeout
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located((by, seletor))
        )

    def preencher_campo(self, by, seletor, valor, limpar=True):
        """Localiza e preenche um campo de texto ou input."""
        elemento = self.esperar_elemento(by, seletor)
        if limpar:
            elemento.clear()
        elemento.send_keys(str(valor))
        return elemento

    def selecionar_dropdown(self, by, seletor, texto_visivel=None, valor=None):
        """Seleciona uma opção dentro de um elemento <select>."""
        elemento = self.esperar_elemento(by, seletor)
        select = Select(elemento)
        if texto_visivel:
            select.select_by_visible_text(str(texto_visivel))
        elif valor:
            select.select_by_value(str(valor))

    def marcar_radio(self, nome_grupo, valor):
        """Marca uma opção específica de um grupo de radio buttons."""
        xpath = f"//input[@type='radio'][@name='{nome_grupo}'][@value='{valor}']"
        elemento = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        if not elemento.is_selected():
            elemento.click()

    def marcar_checkbox(self, by, seletor, marcar=True):
        """Marca ou desmarca uma caixa de seleção (checkbox)."""
        elemento = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((by, seletor))
        )
        if (marcar and not elemento.is_selected()) or (not marcar and elemento.is_selected()):
            elemento.click()

    def clicar_botao(self, by, seletor):
        """Clica em um botão ou elemento clicável."""
        elemento = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable((by, seletor))
        )
        elemento.click()
        return elemento

    def preencher_formulario_demo(self, caminho_csv=None, delay=1.0, callback_progresso=None):
        """
        Executa o fluxo completo de demonstração preenchendo o formulário local
        'demo_form.html' com as linhas do CSV de exemplo.
        """
        caminho_csv = caminho_csv or config.CADASTROS_CSV
        if not os.path.exists(caminho_csv):
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

        df = pd.read_csv(caminho_csv)
        total = len(df)
        print(f"\n📋 Iniciando preenchimento de {total} registros do arquivo '{Path(caminho_csv).name}'...")

        self.abrir_pagina(config.DEMO_FORM_PATH)
        time.sleep(1)

        sucessos = 0
        erros = 0

        for index, row in df.iterrows():
            try:
                progresso_msg = f"[{index + 1}/{total}] Cadastrando: {row['nome']} ({row['departamento']})..."
                print(progresso_msg)
                if callback_progresso:
                    callback_progresso(index + 1, total, progresso_msg)

                # Preenche campos de texto
                self.preencher_campo(By.ID, "nome", row["nome"])
                self.preencher_campo(By.ID, "email", row["email"])
                self.preencher_campo(By.ID, "telefone", row["telefone"])

                # Seleciona Departamento (Select)
                self.selecionar_dropdown(By.ID, "departamento", texto_visivel=row["departamento"])

                # Marca Nível de Experiência (Radio)
                if "experiencia" in row and pd.notna(row["experiencia"]):
                    self.marcar_radio("experiencia", row["experiencia"])

                # Garante checkbox de termos
                self.marcar_checkbox(By.ID, "termos", marcar=True)

                # Clica em Salvar
                self.clicar_botao(By.ID, "btnSalvar")
                sucessos += 1

                time.sleep(delay)

            except Exception as e:
                erros += 1
                print(f"❌ Erro ao cadastrar linha {index + 1}: {e}")

        relatorio = f"\n🏁 Preenchimento finalizado! Sucessos: {sucessos} | Erros: {erros}"
        print(relatorio)
        if callback_progresso:
            callback_progresso(total, total, relatorio)
        return {"total": total, "sucessos": sucessos, "erros": erros}
