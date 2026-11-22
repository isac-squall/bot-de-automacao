import http.server
import socketserver
import json
import threading
import time
import os
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import config
from modules.web_automator import WebAutomator
from modules.message_sender import MessageSender
from modules.desktop_automator import DesktopAutomator

PORT = 8000

ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://src-amber-tau.vercel.app",
}
ALLOWED_ORIGINS.update(
    origin.strip()
    for origin in os.environ.get("BOT_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
)

# Logs compartilhados em memória
LOG_BUFFER = []

def registrar_log(msg):
    t = time.strftime("%H:%M:%S")
    LOG_BUFFER.append(f"[{t}] {msg}")
    print(f"[{t}] {msg}")
    if len(LOG_BUFFER) > 100:
        LOG_BUFFER.pop(0)

class BotRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Vary", "Origin")
            if self.headers.get("Access-Control-Request-Private-Network") == "true":
                self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        if self.headers.get("Origin") not in ALLOWED_ORIGINS:
            self.send_error(403, "Origin not allowed")
            return

        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        origin = self.headers.get("Origin")
        if self.path.startswith("/api/") and origin and origin not in ALLOWED_ORIGINS:
            self.send_error(403, "Origin not allowed")
            return

        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            dashboard_path = BASE_DIR / "templates" / "index.html"
            with open(dashboard_path, "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/formulario":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            form_path = BASE_DIR / "templates" / "demo_form.html"
            with open(form_path, "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = {
                "status": "online",
                "port": PORT,
                "versao": "1.0.0",
                "selenium": True,
                "pyautogui": True
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))

        elif self.path == "/api/contatos":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            sender = MessageSender()
            previas = sender.previsualizar_envios()
            self.wfile.write(json.dumps({"contatos": previas}).encode("utf-8"))

        elif self.path == "/api/desktop-info":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            desktop = DesktopAutomator()
            try:
                res = desktop.obter_resolucao()
                pos = desktop.obter_posicao_atual()
                data = {
                    "resolucao": [res[0], res[1]],
                    "mouse": [pos[0], pos[1]],
                    "failsafe": config.PYAUTOGUI_CONFIG.get("failsafe", True)
                }
            except Exception as e:
                data = {
                    "resolucao": [1920, 1080],
                    "mouse": [0, 0],
                    "failsafe": True,
                    "erro": str(e)
                }
            self.wfile.write(json.dumps(data).encode("utf-8"))

        elif self.path == "/api/logs":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"logs": LOG_BUFFER}).encode("utf-8"))

        else:
            # Fallback para arquivos estáticos
            super().do_GET()

    def do_POST(self):
        if self.headers.get("Origin") not in ALLOWED_ORIGINS:
            self.send_error(403, "Origin not allowed")
            return

        if self.path == "/api/executar-formulario":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            def rodar():
                registrar_log("Robô Selenium disparado via Painel Web!")
                try:
                    web = WebAutomator(headless=False)
                    def cb(atual, total, msg):
                        registrar_log(f"[{atual}/{total}] {msg}")
                    res = web.preencher_formulario_demo(config.CADASTROS_CSV, delay=1.0, callback_progresso=cb)
                    registrar_log(f"Finalizado: {res['sucessos']} salvos, {res['erros']} erros.")
                    time.sleep(2)
                    web.fechar_navegador()
                except Exception as e:
                    registrar_log(f"Erro no preenchimento: {e}")

            threading.Thread(target=rodar, daemon=True).start()
            resposta = {"sucesso": True, "mensagem": "Robô Selenium iniciado! O navegador abrirá e preencherá o formulário."}
            self.wfile.write(json.dumps(resposta).encode("utf-8"))

        elif self.path == "/api/simular-mensagens":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            def rodar_sim():
                registrar_log("Iniciando simulação de mensagens...")
                sender = MessageSender()
                def cb(atual, total, msg):
                    registrar_log(msg)
                res = sender.disparar_lote_whatsapp(modo_simulacao=True, callback_progresso=cb)
                registrar_log(f"Simulação concluída: {res['sucessos']} mensagens processadas.")

            threading.Thread(target=rodar_sim, daemon=True).start()
            resposta = {"sucesso": True, "mensagem": "Simulação de envio em lote iniciada! Veja o log abaixo."}
            self.wfile.write(json.dumps(resposta).encode("utf-8"))

        elif self.path == "/api/executar-desktop":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            def rodar_desktop():
                registrar_log("Iniciando demonstração do Desktop (Bloco de Notas)...")
                desktop = DesktopAutomator()
                def cb(atual, total, msg):
                    registrar_log(f"[{atual}/{total}] {msg}")
                try:
                    desktop.executar_demonstracao_bloco_de_notas(callback_progresso=cb)
                    registrar_log("Demonstração Desktop finalizada com sucesso.")
                except Exception as e:
                    registrar_log(f"Erro no DesktopAutomator: {e}")

            threading.Thread(target=rodar_desktop, daemon=True).start()
            resposta = {"sucesso": True, "mensagem": "Demonstração Desktop iniciada (Win + R -> Notepad)."}
            self.wfile.write(json.dumps(resposta).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

def iniciar_servidor(porta=PORT):
    # Permite reuso de porta imediatamente
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", porta), BotRequestHandler) as httpd:
        print(f"\n========================================================")
        print(f"🌐 Servidor Web do Bot Ativo em: http://localhost:{porta}")
        print(f"📝 Formulário direto: http://localhost:{porta}/formulario")
        print(f"========================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor encerrado.")

if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    iniciar_servidor(porta)
