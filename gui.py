import os
import sys
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from modules.web_automator import WebAutomator
from modules.message_sender import MessageSender
from modules.desktop_automator import DesktopAutomator

class AutomationBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("🤖 Bot de Automação Inteligente - Painel de Controle")
        self.geometry("900x680")
        self.minsize(800, 600)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Instâncias de serviços
        self.web = WebAutomator(headless=False)
        self.sender = MessageSender(self.web)
        self.desktop = DesktopAutomator()

        self._criar_layout()

    def _criar_layout(self):
        # Cabeçalho Principal
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray15"))
        self.header_frame.pack(fill="x", padx=0, pady=0)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🤖 Bot de Automação - Selenium & PyAutoGUI",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=12)

        self.status_badge = ctk.CTkLabel(
            self.header_frame,
            text="● Sistema Pronto",
            text_color="#22c55e",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_badge.pack(side="right", padx=20, pady=12)

        # Tabview Central
        self.tabview = ctk.CTkTabview(self, width=860, height=360)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_form = self.tabview.add("📝 Formulários (Selenium)")
        self.tab_msg = self.tabview.add("📨 Mensagens (WhatsApp)")
        self.tab_desk = self.tabview.add("🖥️ Automação Desktop (PyAutoGUI)")

        self._setup_tab_formularios()
        self._setup_tab_mensagens()
        self._setup_tab_desktop()

        # Área de Logs em Tempo Real
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.log_label = ctk.CTkLabel(
            self.log_frame,
            text="📜 Log de Execução:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.log_label.pack(anchor="w", padx=10, pady=(5, 0))

        self.log_textbox = ctk.CTkTextbox(self.log_frame, height=110, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_textbox.pack(fill="x", padx=10, pady=5)
        self.log("Painel iniciado. Pronto para executar automações.")

    def log(self, mensagem):
        """Escreve uma linha no console de log da interface."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {mensagem}\n")
        self.log_textbox.see("end")

    # =========================================================================
    # ABA 1: FORMULÁRIOS WEB (SELENIUM)
    # =========================================================================
    def _setup_tab_formularios(self):
        tab = self.tab_form

        # Seletor de Arquivo CSV
        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=6)
        ctk.CTkLabel(row1, text="Planilha de Cadastros:", width=150, anchor="w").pack(side="left")
        self.entry_csv_form = ctk.CTkEntry(row1, width=460)
        self.entry_csv_form.insert(0, str(config.CADASTROS_CSV))
        self.entry_csv_form.pack(side="left", padx=5)
        ctk.CTkButton(row1, text="Procurar...", width=90, command=self._procurar_csv_form).pack(side="left")

        # Opção Headless e Delay
        row2 = ctk.CTkFrame(tab, fg_color="transparent")
        row2.pack(fill="x", pady=6)
        ctk.CTkLabel(row2, text="Intervalo entre envios (s):", width=150, anchor="w").pack(side="left")
        self.slider_delay_form = ctk.CTkSlider(row2, from_=0.5, to=5.0, number_of_steps=9, width=200)
        self.slider_delay_form.set(1.2)
        self.slider_delay_form.pack(side="left", padx=5)

        self.lbl_delay_form = ctk.CTkLabel(row2, text="1.2s", width=50)
        self.lbl_delay_form.pack(side="left")
        self.slider_delay_form.configure(command=lambda val: self.lbl_delay_form.configure(text=f"{val:.1f}s"))

        self.check_headless = ctk.CTkCheckBox(row2, text="Modo Oculto (Headless)")
        self.check_headless.pack(side="left", padx=20)

        # Barra de Progresso
        self.progress_form = ctk.CTkProgressBar(tab)
        self.progress_form.set(0)
        self.progress_form.pack(fill="x", pady=15)

        # Botões de Ação
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        self.btn_exec_form = ctk.CTkButton(
            btn_frame,
            text="▶️ Iniciar Preenchimento Automático (Demo)",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=40,
            command=self._executar_preenchimento_form
        )
        self.btn_exec_form.pack(side="left", fill="x", expand=True, padx=5)

    def _procurar_csv_form(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv"), ("Todos os Arquivos", "*.*")])
        if caminho:
            self.entry_csv_form.delete(0, "end")
            self.entry_csv_form.insert(0, caminho)

    def _executar_preenchimento_form(self):
        caminho_csv = self.entry_csv_form.get()
        delay = float(self.slider_delay_form.get())
        headless = bool(self.check_headless.get())

        self.btn_exec_form.configure(state="disabled")
        self.status_badge.configure(text="● Executando Formulário...", text_color="#f59e0b")
        self.log(f"Iniciando preenchimento com '{Path(caminho_csv).name}' (Delay: {delay:.1f}s)...")

        def task():
            try:
                web = WebAutomator(headless=headless)
                def callback(atual, total, msg):
                    prog = atual / total if total > 0 else 0
                    self.progress_form.set(prog)
                    self.log(msg)

                res = web.preencher_formulario_demo(caminho_csv, delay=delay, callback_progresso=callback)
                self.log(f"Finalizado: {res['sucessos']} salvos, {res['erros']} erros.")
                messagebox.showinfo("Sucesso", f"Preenchimento concluído!\nSucessos: {res['sucessos']}\nErros: {res['erros']}")
            except Exception as e:
                self.log(f"Erro na execução: {e}")
                messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            finally:
                self.btn_exec_form.configure(state="normal")
                self.status_badge.configure(text="● Sistema Pronto", text_color="#22c55e")

        threading.Thread(target=task, daemon=True).start()

    # =========================================================================
    # ABA 2: MENSAGENS (WHATSAPP WEB)
    # =========================================================================
    def _setup_tab_mensagens(self):
        tab = self.tab_msg

        # Seletor de Contatos
        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Lista de Contatos:", width=130, anchor="w").pack(side="left")
        self.entry_csv_msg = ctk.CTkEntry(row1, width=480)
        self.entry_csv_msg.insert(0, str(config.CONTATOS_CSV))
        self.entry_csv_msg.pack(side="left", padx=5)
        ctk.CTkButton(row1, text="Procurar...", width=90, command=self._procurar_csv_msg).pack(side="left")

        # Template de Mensagem
        lbl_msg = ctk.CTkLabel(tab, text="Modelo da Mensagem (Use {nome}, {pedido}, {status}):", anchor="w")
        lbl_msg.pack(fill="x", pady=(5, 0))

        self.txt_template = ctk.CTkTextbox(tab, height=70, font=ctk.CTkFont(size=12))
        self.txt_template.insert("1.0", "Olá {nome}! Seu pedido {pedido} foi atualizado para: *{status}*.")
        self.txt_template.pack(fill="x", pady=5)

        # Botões de Ação
        row_btn = ctk.CTkFrame(tab, fg_color="transparent")
        row_btn.pack(fill="x", pady=10)

        self.btn_previa = ctk.CTkButton(
            row_btn,
            text="👁️ Pré-visualizar Mensagens",
            command=self._previsualizar_mensagens,
            width=180
        )
        self.btn_previa.pack(side="left", padx=5)

        self.btn_disparar_msg = ctk.CTkButton(
            row_btn,
            text="▶️ Iniciar Disparo via WhatsApp Web",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self._iniciar_disparo_whatsapp
        )
        self.btn_disparar_msg.pack(side="left", fill="x", expand=True, padx=5)

    def _procurar_csv_msg(self):
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv"), ("Todos os Arquivos", "*.*")])
        if caminho:
            self.entry_csv_msg.delete(0, "end")
            self.entry_csv_msg.insert(0, caminho)

    def _previsualizar_mensagens(self):
        try:
            caminho_csv = self.entry_csv_msg.get()
            template = self.txt_template.get("1.0", "end").strip()
            previas = self.sender.previsualizar_envios(caminho_csv, template)

            self.log(f"--- Pré-visualização de {len(previas)} Mensagens ---")
            for item in previas:
                self.log(f"Para: {item['nome']} ({item['telefone']}) -> \"{item['mensagem']}\"")
            messagebox.showinfo("Pré-visualização", f"Foram geradas {len(previas)} mensagens personalizadas.\nConsulte o console de logs abaixo.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na pré-visualização: {e}")

    def _iniciar_disparo_whatsapp(self):
        if not messagebox.askyesno("Confirmar Envio", "Deseja realmente iniciar os disparos via WhatsApp Web?\nCertifique-se de que o navegador abrirá para login/leitura de QR Code."):
            return

        caminho_csv = self.entry_csv_msg.get()
        template = self.txt_template.get("1.0", "end").strip()

        self.btn_disparar_msg.configure(state="disabled")
        self.status_badge.configure(text="● Disparando Mensagens...", text_color="#f59e0b")

        def task():
            try:
                def callback(atual, total, msg):
                    self.log(msg)

                sender = MessageSender()
                res = sender.disparar_lote_whatsapp(caminho_csv, template=template, modo_simulacao=False, callback_progresso=callback)
                messagebox.showinfo("Concluído", f"Envios finalizados!\nSucessos: {res['sucessos']}\nFalhas: {res['erros']}")
            except Exception as e:
                self.log(f"Erro no disparo: {e}")
                messagebox.showerror("Erro", f"Erro no envio: {e}")
            finally:
                self.btn_disparar_msg.configure(state="normal")
                self.status_badge.configure(text="● Sistema Pronto", text_color="#22c55e")

        threading.Thread(target=task, daemon=True).start()

    # =========================================================================
    # ABA 3: DESKTOP (PYAUTOGUI)
    # =========================================================================
    def _setup_tab_desktop(self):
        tab = self.tab_desk

        info_box = ctk.CTkFrame(tab, fg_color=("gray90", "gray20"))
        info_box.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(
            info_box,
            text="🛡️ Mecanismo de Segurança (Fail-Safe):",
            font=ctk.CTkFont(weight="bold", size=13)
        ).pack(anchor="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            info_box,
            text="Se precisar parar o robô a qualquer instante, basta mover bruscamente o mouse\npara o CANTO SUPERIOR ESQUERDO da sua tela.",
            justify="left",
            text_color="#94a3b8"
        ).pack(anchor="w", padx=10, pady=(0, 8))

        btn_grid = ctk.CTkFrame(tab, fg_color="transparent")
        btn_grid.pack(fill="x", pady=15)

        ctk.CTkButton(
            btn_grid,
            text="📝 Executar Demo ao Vivo\n(Abre Bloco de Notas e Digita)",
            height=60,
            command=self._executar_demo_desktop
        ).pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            btn_grid,
            text="📸 Tirar Captura de Tela\n(Salva na pasta /screenshots)",
            height=60,
            command=self._tirar_screenshot
        ).pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            btn_grid,
            text="🖱️ Obter Posição do Mouse\n(Exibe Coordenadas Atuais)",
            height=60,
            command=self._obter_coordenadas_mouse
        ).pack(side="left", fill="x", expand=True, padx=5)

    def _executar_demo_desktop(self):
        self.log("Iniciando demonstração do DesktopAutomator...")

        def task():
            try:
                def callback(atual, total, msg):
                    self.log(f"[{atual}/{total}] {msg}")
                self.desktop.executar_demonstracao_bloco_de_notas(callback_progresso=callback)
                messagebox.showinfo("Sucesso", "Demonstração no Bloco de Notas concluída!")
            except Exception as e:
                self.log(f"Erro no PyAutoGUI: {e}")
                messagebox.showerror("Erro", f"Falha na automação desktop: {e}")

        threading.Thread(target=task, daemon=True).start()

    def _tirar_screenshot(self):
        try:
            caminho = self.desktop.tirar_screenshot()
            self.log(f"Captura realizada com sucesso: {caminho}")
            messagebox.showinfo("Captura Salva", f"Screenshot salva em:\n{caminho}")
        except Exception as e:
            self.log(f"Erro ao capturar tela: {e}")
            messagebox.showerror("Erro", f"Falha: {e}")

    def _obter_coordenadas_mouse(self):
        try:
            x, y = self.desktop.obter_posicao_atual()
            res = self.desktop.obter_resolucao()
            msg = f"Posição do Mouse: X={x}, Y={y} | Resolução da Tela: {res[0]}x{res[1]}"
            self.log(msg)
            messagebox.showinfo("Coordenadas do Mouse", msg)
        except Exception as e:
            self.log(f"Erro ao obter posição: {e}")

def iniciar_gui():
    app = AutomationBotGUI()
    app.mainloop()

if __name__ == "__main__":
    iniciar_gui()
