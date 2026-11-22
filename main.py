import sys
import os
import time
from pathlib import Path

# Adiciona o diretório atual ao sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    console = Console()
except ImportError:
    console = None

import config
from modules.web_automator import WebAutomator
from modules.message_sender import MessageSender
from modules.desktop_automator import DesktopAutomator

def print_banner():
    if console:
        console.clear()
        banner_text = """
 [bold cyan]🤖 BOT DE AUTOMAÇÃO INTELIGENTE[/bold cyan]
 [dim]• Envio de Mensagens Automáticas[/dim]
 [dim]• Preenchimento Automático de Formulários[/dim]
 [dim]• Automação de Tarefas Repetitivas no Desktop[/dim]
 [yellow]Bibliotecas principais: Selenium | PyAutoGUI | Pandas[/yellow]
        """
        console.print(Panel(banner_text, border_style="cyan", expand=False))
    else:
        print("=" * 60)
        print("🤖 BOT DE AUTOMAÇÃO INTELIGENTE (Selenium & PyAutoGUI)")
        print("=" * 60)

def exibir_menu_principal():
    print_banner()
    if console:
        table = Table(title="📋 Menu Principal", show_header=True, header_style="bold magenta")
        table.add_column("Opção", style="bold green", width=8, justify="center")
        table.add_column("Funcionalidade", style="white")
        table.add_column("Tecnologia", style="dim")

        table.add_row("1", "Preenchimento de Formulários", "Selenium (Web)")
        table.add_row("2", "Envio de Mensagens Automáticas", "WhatsApp Web / Disparo em Lote")
        table.add_row("3", "Tarefas Repetitivas no Computador", "PyAutoGUI (Mouse/Teclado/Macros)")
        table.add_row("4", "Abrir Painel Gráfico Visual (GUI)", "CustomTkinter")
        table.add_row("5", "Verificar Coordenadas do Mouse", "PyAutoGUI Utilitário")
        table.add_row("0", "Sair", "-")

        console.print(table)
    else:
        print("1. Preenchimento de Formulários (Selenium)")
        print("2. Envio de Mensagens Automáticas (WhatsApp)")
        print("3. Tarefas Repetitivas no Computador (PyAutoGUI)")
        print("4. Abrir Painel Gráfico (GUI)")
        print("5. Verificar Coordenadas do Mouse")
        print("0. Sair")

def menu_formularios():
    print_banner()
    if console:
        console.print("[bold yellow]📝 AUTOMAÇÃO DE FORMULÁRIOS WEB (SELENIUM)[/bold yellow]\n")
        console.print("1. Executar Demonstração Local ([italic]demo_form.html[/italic] + planilha de cadastros)")
        console.print("2. Abrir Navegador e Acessar URL Personalizada")
        console.print("0. Voltar ao Menu Principal\n")
        opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "0"], default="1")
    else:
        print("\n1. Executar Demonstração Local\n2. Abrir URL Personalizada\n0. Voltar")
        opcao = input("Opção: ").strip()

    if opcao == "1":
        automator = WebAutomator(headless=False)
        try:
            automator.preencher_formulario_demo(config.CADASTROS_CSV, delay=1.2)
            if console:
                console.print("\n[bold green]✅ Sucesso![/bold green] Formulário preenchido com dados do CSV.")
            input("\nPressione ENTER para fechar o navegador...")
        finally:
            automator.fechar_navegador()

    elif opcao == "2":
        url = input("Digite a URL a ser acessada: ").strip()
        if url:
            automator = WebAutomator(headless=False)
            try:
                automator.abrir_pagina(url)
                input("\nPágina aberta. Pressione ENTER quando desejar fechar...")
            finally:
                automator.fechar_navegador()

def menu_mensagens():
    print_banner()
    if console:
        console.print("[bold yellow]📨 ENVIO DE MENSAGENS AUTOMÁTICAS[/bold yellow]\n")
        console.print("1. Pré-visualizar / Simular Envio de Mensagens (Sem disparar)")
        console.print("2. Disparar Mensagens em Lote via WhatsApp Web (Real)")
        console.print("0. Voltar ao Menu Principal\n")
        opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "0"], default="1")
    else:
        print("\n1. Pré-visualizar Envio\n2. Disparar via WhatsApp Web\n0. Voltar")
        opcao = input("Opção: ").strip()

    sender = MessageSender()

    if opcao == "1":
        previas = sender.previsualizar_envios()
        if console:
            tabela = Table(title="👁️ Pré-visualização das Mensagens Personalizadas", show_header=True)
            tabela.add_column("Nome", style="cyan")
            tabela.add_column("Telefone", style="green")
            tabela.add_column("Mensagem Formatada", style="white")
            for item in previas:
                tabela.add_row(item["nome"], item["telefone"], item["mensagem"])
            console.print(tabela)
            console.print(f"\n[green]Total de contatos prontos para envio: {len(previas)}[/green]")
        else:
            for item in previas:
                print(f"[{item['nome']} - {item['telefone']}] -> {item['mensagem']}")
        input("\nPressione ENTER para continuar...")

    elif opcao == "2":
        if console:
            confirm = Confirm.ask("Deseja realmente iniciar o envio das mensagens via WhatsApp Web?", default=False)
        else:
            confirm = input("Deseja iniciar o envio? (s/n): ").strip().lower() == "s"

        if confirm:
            try:
                sender.disparar_lote_whatsapp(config.CONTATOS_CSV, modo_simulacao=False)
            finally:
                sender.web.fechar_navegador()
            input("\nPressione ENTER para continuar...")
        else:
            print("Envio cancelado.")
            time.sleep(1)

def menu_desktop():
    print_banner()
    if console:
        console.print("[bold yellow]🖥️ AUTOMAÇÃO DESKTOP REPETITIVA (PYAUTOGUI)[/bold yellow]\n")
        console.print("1. Executar Demonstração ao Vivo no Bloco de Notas (Notepad)")
        console.print("2. Tirar Captura de Tela (Screenshot)")
        console.print("3. Monitorar Coordenadas do Mouse em Tempo Real")
        console.print("0. Voltar ao Menu Principal\n")
        opcao = Prompt.ask("Escolha uma opção", choices=["1", "2", "3", "0"], default="1")
    else:
        print("\n1. Demo no Bloco de Notas\n2. Tirar Screenshot\n3. Monitorar Mouse\n0. Voltar")
        opcao = input("Opção: ").strip()

    desktop = DesktopAutomator()

    if opcao == "1":
        if console:
            console.print("[yellow]Atenção: O robô abrirá o Bloco de Notas e demonstrará digitação automática.[/yellow]")
            console.print("[dim]Para parar a qualquer momento, arraste o cursor para o canto superior esquerdo da tela.[/dim]\n")
        desktop.executar_demonstracao_bloco_de_notas()
        input("\nPressione ENTER para continuar...")

    elif opcao == "2":
        caminho = desktop.tirar_screenshot()
        if console:
            console.print(f"[bold green]✅ Captura salva em:[/bold green] {caminho}")
        else:
            print(f"Captura salva em: {caminho}")
        input("\nPressione ENTER para continuar...")

    elif opcao == "3":
        monitorar_mouse(desktop)

def monitorar_mouse(desktop):
    print("\n🔍 Monitorando coordenadas do mouse (Pressione Ctrl+C para encerrar):")
    try:
        while True:
            x, y = desktop.obter_posicao_atual()
            pos_str = f"Posição X: {x:<5} | Y: {y:<5}"
            print(f"\r{pos_str}", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nMonitoramento finalizado.")
        time.sleep(1)

def abrir_interface_grafica():
    print("\n🎨 Iniciando Interface Gráfica Moderna (CustomTkinter)...")
    try:
        from gui import iniciar_gui
        iniciar_gui()
    except Exception as e:
        print(f"❌ Erro ao abrir interface gráfica: {e}")
        time.sleep(2)

def main():
    while True:
        try:
            exibir_menu_principal()
            if console:
                opcao = Prompt.ask("\nEscolha uma opção", choices=["1", "2", "3", "4", "5", "0"], default="1")
            else:
                opcao = input("\nEscolha uma opção (0-5): ").strip()

            if opcao == "1":
                menu_formularios()
            elif opcao == "2":
                menu_mensagens()
            elif opcao == "3":
                menu_desktop()
            elif opcao == "4":
                abrir_interface_grafica()
            elif opcao == "5":
                desktop = DesktopAutomator()
                monitorar_mouse(desktop)
            elif opcao == "0":
                if console:
                    console.print("\n[bold cyan]Até logo! Robô encerrado com sucesso.[/bold cyan] 👋")
                else:
                    print("\nRobô encerrado.")
                break
        except KeyboardInterrupt:
            print("\nOperação interrompida pelo usuário.")
            break

if __name__ == "__main__":
    main()
