"""
J.A.R.V.I.S. — Executor de Comandos do Sistema

Módulo responsável por executar ações reais no Windows:
abrir aplicativos, pesquisar, digitar, controlar sistema, etc.
"""

import os
import subprocess
import webbrowser
import datetime
import platform
import glob

import pyautogui
import psutil

from nlp import APPLICATIONS


USER_HOME = os.path.expanduser("~")

def _get_special_folder(folder_key):
    """Obtém caminho da pasta especial considerando OneDrive e pastas padrão."""
    key = folder_key.lower()
    candidates = []
    
    if key in ["documents", "documentos"]:
        candidates = [
            os.path.join(USER_HOME, "OneDrive", "Documentos"),
            os.path.join(USER_HOME, "OneDrive", "Documents"),
            os.path.join(USER_HOME, "Documents"),
            os.path.join(USER_HOME, "Documentos"),
        ]
    elif key in ["desktop", "área de trabalho", "area de trabalho"]:
        candidates = [
            os.path.join(USER_HOME, "OneDrive", "Área de Trabalho"),
            os.path.join(USER_HOME, "OneDrive", "Desktop"),
            os.path.join(USER_HOME, "Desktop"),
            os.path.join(USER_HOME, "Área de Trabalho"),
        ]
    elif key in ["downloads", "download"]:
        candidates = [
            os.path.join(USER_HOME, "Downloads"),
            os.path.join(USER_HOME, "OneDrive", "Downloads"),
        ]
    elif key in ["pictures", "imagens", "fotos"]:
        candidates = [
            os.path.join(USER_HOME, "OneDrive", "Imagens"),
            os.path.join(USER_HOME, "OneDrive", "Pictures"),
            os.path.join(USER_HOME, "Pictures"),
            os.path.join(USER_HOME, "Imagens"),
        ]
    elif key in ["music", "músicas", "musicas"]:
        candidates = [
            os.path.join(USER_HOME, "Music"),
            os.path.join(USER_HOME, "Músicas"),
        ]
    elif key in ["videos", "vídeos"]:
        candidates = [
            os.path.join(USER_HOME, "Videos"),
            os.path.join(USER_HOME, "Vídeos"),
        ]

    for p in candidates:
        if os.path.exists(p):
            return p
            
    return os.path.join(USER_HOME, folder_key)


def open_application(name, executable=None):
    """
    Abre um aplicativo pelo nome.
    """
    app_data = APPLICATIONS.get(name.lower())
    if isinstance(app_data, dict):
        exe = executable or app_data.get("exe", name)
    else:
        exe = executable or app_data or name
    
    try:
        if str(exe).startswith("ms-"):
            os.startfile(exe)
            return f"Abrindo {name}."
        
        subprocess.Popen(exe, shell=True)
        return f"Abrindo {name}."
    except Exception as e:
        try:
            subprocess.Popen(f'start {exe}', shell=True)
            return f"Abrindo {name}."
        except Exception:
            return f"Não foi possível abrir {name}."


def close_application(target="app", name=None, process=None):
    """
    Fecha um aplicativo específico ou a janela ativa.
    """
    try:
        import time
        if target == "current":
            time.sleep(0.3)
            pyautogui.hotkey('alt', 'f4')
            return "Janela atual fechada."
            
        app_data = APPLICATIONS.get((name or "").lower())
        proc_name = process
        if not proc_name and isinstance(app_data, dict):
            proc_name = app_data.get("process")
        if not proc_name:
            proc_name = f"{name}.exe"
            
        # Executa taskkill
        cmd = f"taskkill /F /IM {proc_name} /T"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if res.returncode == 0 or "SUCCESS" in res.stdout or "ÊXITO" in res.stdout or "sucesso" in res.stdout.lower():
            return f"Aplicativo {name or proc_name} encerrado com sucesso."
        else:
            # Tenta via Alt+F4 como fallback
            pyautogui.hotkey('alt', 'f4')
            return f"Comando de encerramento enviado para {name or 'janela'}."
    except Exception as e:
        return f"Erro ao fechar aplicativo: {str(e)}"


def scroll_page(direction="down", amount=6):
    """
    Executa rolagem (scroll) do mouse na tela.
    """
    try:
        import time
        time.sleep(0.2)
        # Cada 'click' padrão de roda equivale a ~120 unidades no Windows
        clicks = int(amount) * 120
        if direction == "down":
            pyautogui.scroll(-clicks)
            return f"Rolando a página para baixo."
        else:
            pyautogui.scroll(clicks)
            return f"Rolando a página para cima."
    except Exception as e:
        return f"Erro ao executar rolagem: {str(e)}"


def get_possibilities():
    """
    Retorna a lista completa de capacidades e possibilidades do J.A.R.V.I.S.
    """
    detail = (
        "🤖 CAPACIDADES E POSSIBILIDADES DO J.A.R.V.I.S.:\n\n"
        "1. 🌐 NAVEGAÇÃO & INTERNET:\n"
        "   • 'abra o youtube', 'abra o chatgpt', 'entre no github', etc.\n"
        "   • 'pesquise sobre inteligência artificial no google'\n\n"
        "2. 💻 APLICATIVOS DO SISTEMA:\n"
        "   • 'abra o bloco de notas', 'abra o chrome', 'abra a calculadora', 'abra o vs code'\n"
        "   • 'feche o chrome', 'fechar bloco de notas', 'fechar janela atual'\n\n"
        "3. 🖱️ MOUSE & SCROLL:\n"
        "   • 'rolar para baixo', 'rolar para cima', 'subir a página', 'descer a tela'\n\n"
        "4. ✍️ DIGITAÇÃO & TECLADO:\n"
        "   • 'escreva [texto]' (digita no app ativo com acentuação)\n"
        "   • 'enter', 'esc', 'tab', 'espaço'\n"
        "   • 'apagar' (1 letra), 'apagar última palavra', 'apagar 5 caracteres', 'apagar tudo'\n"
        "   • 'selecionar tudo', 'copiar', 'colar', 'desfazer', 'salvar'\n\n"
        "5. 📁 ARQUIVOS & PASTAS:\n"
        "   • 'liste meus documentos', 'liste a área de trabalho', 'liste downloads'\n"
        "   • 'abra o arquivo [nome_do_arquivo]'\n\n"
        "6. ⚙️ UTILITÁRIOS & SISTEMA:\n"
        "   • 'tire um print da tela' (salva screenshot em Imagens)\n"
        "   • 'como está o sistema?' (CPU, RAM, disco e bateria)\n"
        "   • 'que horas são?', 'que dia é hoje?'\n"
        "   • 'aumente o volume', 'diminua o volume', 'mutar som'\n"
        "   • 'desligar o computador', 'reiniciar o computador'"
    )
    
    voice = (
        "Posso navegar na internet e pesquisar no Google, "
        "abrir e fechar programas, rolar páginas para cima e para baixo, "
        "digitar textos e controlar teclas como Enter, Esc e Backspace, "
        "listar e abrir seus arquivos, tirar prints, monitorar o uso do computador, "
        "e controlar volume e energia. Você também pode conferir todas as opções no histórico."
    )
    return detail, voice


def search_web(query):
    """
    Pesquisa algo no Google.
    """
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Pesquisando na internet por: {query}"
    except Exception as e:
        return f"Erro ao pesquisar: {str(e)}"


def open_website(name, url):
    """
    Abre um site no navegador.
    """
    try:
        webbrowser.open(url)
        return f"Abrindo {name} no navegador."
    except Exception as e:
        return f"Erro ao abrir site: {str(e)}"


def type_text(text):
    """
    Digita texto na janela atualmente ativa.
    """
    try:
        import time
        time.sleep(0.5)
        
        # Usa o clipboard para suporte perfeito a acentos e caracteres especiais
        import subprocess as sp
        process = sp.Popen(['clip'], stdin=sp.PIPE, shell=True)
        process.communicate(text.encode('utf-16le'))
        
        pyautogui.hotkey('ctrl', 'v')
        return f"Texto digitado: {text}"
    except Exception as e:
        return f"Erro ao digitar: {str(e)}"


def press_key(key_name):
    """
    Pressiona uma tecla individual (ex: enter, esc, tab, space).
    """
    try:
        import time
        time.sleep(0.3)
        pyautogui.press(key_name)
        return f"Tecla {key_name.upper()} pressionada."
    except Exception as e:
        return f"Erro ao pressionar tecla {key_name}: {str(e)}"


def delete_text(mode="char", count=1):
    """
    Executa exclusão de texto:
    - 'char': apaga o último caractere (Backspace 1x)
    - 'word': apaga a última palavra (Ctrl + Backspace)
    - 'all': apaga todo o texto (Ctrl + A -> Backspace)
    - 'count': apaga N caracteres (Backspace N vezes)
    """
    try:
        import time
        time.sleep(0.3)
        
        if mode == "all":
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.05)
            pyautogui.press('backspace')
            return "Todo o texto foi apagado."
            
        elif mode == "word":
            pyautogui.hotkey('ctrl', 'backspace')
            return "Última palavra apagada."
            
        elif mode == "count":
            for _ in range(count):
                pyautogui.press('backspace')
            return f"{count} caracteres apagados."
            
        else: # 'char'
            pyautogui.press('backspace')
            return "Último caractere apagado."
            
    except Exception as e:
        return f"Erro ao apagar texto: {str(e)}"


def keyboard_shortcut(keys, action_name="Atalho"):
    """
    Executa combinação de teclas (ex: ctrl + c, ctrl + v, ctrl + a).
    """
    try:
        import time
        time.sleep(0.3)
        pyautogui.hotkey(*keys)
        return f"{action_name} executado."
    except Exception as e:
        return f"Erro ao executar atalho: {str(e)}"


def list_files(path="documents"):
    """
    Lista arquivos de uma pasta com proteção contra junctions e erros de permissão.
    """
    try:
        folder = _get_special_folder(path)
        
        if not os.path.exists(folder):
            folder = os.path.join(USER_HOME, path)
            
        if not os.path.exists(folder):
            return f"A pasta '{path}' não foi encontrada."
        
        items = []
        try:
            items = os.listdir(folder)
        except Exception as err:
            return f"Não foi possível ler a pasta: {err}"
        
        folders = []
        files = []
        
        for item in sorted(items):
            full_path = os.path.join(folder, item)
            try:
                if os.path.isdir(full_path):
                    folders.append(f"📁 {item}")
                else:
                    size = os.path.getsize(full_path)
                    size_str = _format_size(size)
                    files.append(f"📄 {item} ({size_str})")
            except (PermissionError, OSError):
                continue
        
        result_lines = []
        if folders:
            result_lines.append(f"Pastas ({len(folders)}):")
            result_lines.extend(folders[:15])
        if files:
            result_lines.append(f"\nArquivos ({len(files)}):")
            result_lines.extend(files[:20])
        
        total = len(folders) + len(files)
        folder_name = os.path.basename(folder) or folder
        header = f"Conteúdo de {folder_name} — {total} itens:"
        
        detail_msg = header + "\n" + "\n".join(result_lines)
        voice_msg = f"A pasta {folder_name} possui {len(folders)} pastas e {len(files)} arquivos."
        
        return detail_msg, voice_msg
    
    except Exception as e:
        return f"Erro ao listar arquivos: {str(e)}"


def _format_size(size_bytes):
    """Formata tamanho de arquivo em bytes para formato legível."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def open_file(filename):
    """
    Localiza e abre um arquivo com seu programa padrão.
    """
    search_dirs = [
        _get_special_folder("documents"),
        _get_special_folder("desktop"),
        _get_special_folder("downloads"),
        os.path.join(USER_HOME, "OneDrive", "Documentos", "Códigos(Variados)"),
        USER_HOME,
    ]
    
    clean_filename = filename.strip().strip("'\"")
    
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
            
        exact = os.path.join(sdir, clean_filename)
        if os.path.exists(exact):
            os.startfile(exact)
            return f"Abrindo arquivo {clean_filename}."
        
        # Busca aproximada por padrão
        matches = glob.glob(os.path.join(sdir, f"*{clean_filename}*"))
        if matches:
            target = matches[0]
            os.startfile(target)
            return f"Abrindo arquivo {os.path.basename(target)}."
            
    return f"Não encontrei o arquivo {clean_filename} nas suas pastas principais."


def get_datetime():
    """Retorna data e hora atual em português formatado."""
    now = datetime.datetime.now()
    
    dias_semana = {
        0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira",
        3: "quinta-feira", 4: "sexta-feira", 5: "sábado", 6: "domingo"
    }
    
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    
    dia_semana = dias_semana[now.weekday()]
    mes = meses[now.month]
    
    hora = now.strftime("%H")
    minuto = now.strftime("%M")
    
    return (
        f"São {hora} horas e {minuto} minutos. "
        f"Hoje é {dia_semana}, {now.day} de {mes} de {now.year}."
    )


def take_screenshot():
    """Tira captura de tela e salva na pasta de screenshots."""
    try:
        screenshots_dir = os.path.join(USER_HOME, "Pictures", "Screenshots_Jarvis")
        if not os.path.exists(screenshots_dir):
            onedrive_pics = os.path.join(USER_HOME, "OneDrive", "Imagens", "Screenshots_Jarvis")
            if os.path.exists(os.path.dirname(onedrive_pics)):
                screenshots_dir = onedrive_pics
        
        os.makedirs(screenshots_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jarvis_screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return f"Captura de tela salva em: {filepath}"
    except Exception as e:
        return f"Erro ao capturar tela: {str(e)}"


def system_info():
    """Retorna informações completas do sistema (CPU, RAM, Disco, Bateria)."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.3)
        cpu_count = psutil.cpu_count()
        
        ram = psutil.virtual_memory()
        ram_total = ram.total / (1024 ** 3)
        ram_used = ram.used / (1024 ** 3)
        ram_percent = ram.percent
        
        disk = psutil.disk_usage('C:')
        disk_total = disk.total / (1024 ** 3)
        disk_used = disk.used / (1024 ** 3)
        disk_percent = disk.percent
        
        battery_text = ""
        battery_voice = ""
        try:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "carregando" if battery.power_plugged else "na bateria"
                battery_text = f"\n🔋 Bateria: {battery.percent:.0f}% ({plugged})"
                battery_voice = f"Bateria em {battery.percent:.0f}%, {plugged}."
        except Exception:
            pass
        
        detail = (
            f"💻 Sistema: {platform.system()} {platform.release()}\n"
            f"🧠 CPU: {cpu_percent}% ({cpu_count} núcleos)\n"
            f"📊 RAM: {ram_used:.1f} GB / {ram_total:.1f} GB ({ram_percent}%)\n"
            f"💾 Disco C: {disk_used:.0f} GB / {disk_total:.0f} GB ({disk_percent}%)"
            f"{battery_text}"
        )
        
        voice = (
            f"O processador está em {cpu_percent}%. "
            f"Memória RAM em {ram_percent}%, usando {ram_used:.1f} de {ram_total:.1f} gigabytes. "
            f"Disco C em {disk_percent}%. "
            f"{battery_voice}"
        )
        
        return detail, voice
    except Exception as e:
        return f"Erro ao obter informações: {str(e)}", "Erro ao obter informações do sistema."


def control_volume(action):
    """Controla volume do sistema."""
    try:
        if action == "up":
            for _ in range(5):
                pyautogui.press('volumeup')
            return "Volume aumentado."
        elif action == "down":
            for _ in range(5):
                pyautogui.press('volumedown')
            return "Volume diminuído."
        elif action == "mute":
            pyautogui.press('volumemute')
            return "Volume silenciado."
        else:
            return "Ação de volume não reconhecida."
    except Exception as e:
        return f"Erro ao ajustar volume: {str(e)}"


def shutdown_pc():
    """Agenda desligamento do computador."""
    try:
        os.system("shutdown /s /t 30")
        return "O computador será desligado em 30 segundos. Para cancelar, diga 'cancelar desligamento'."
    except Exception as e:
        return f"Erro ao desligar: {str(e)}"


def restart_pc():
    """Agenda reinicialização do computador."""
    try:
        os.system("shutdown /r /t 30")
        return "O computador será reiniciado em 30 segundos."
    except Exception as e:
        return f"Erro ao reiniciar: {str(e)}"


def cancel_shutdown():
    """Cancela desligamento pendente."""
    try:
        os.system("shutdown /a")
        return "Desligamento cancelado."
    except Exception as e:
        return f"Erro ao cancelar: {str(e)}"
