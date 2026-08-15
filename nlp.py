"""
J.A.R.V.I.S. — Processamento de Linguagem Natural (PT-BR)

Módulo responsável por interpretar comandos de voz e texto em português,
com suporte a ambiguidade, pedidos de opções/possibilidades, controle de mouse/scroll,
fechamento de aplicativos e contexto conversacional.
"""

import re


# Tipos de comando suportados
COMMAND_OPEN_APP = "open_app"
COMMAND_CLOSE_APP = "close_app"
COMMAND_SEARCH_WEB = "search_web"
COMMAND_OPEN_SITE = "open_site"
COMMAND_TYPE_TEXT = "type_text"
COMMAND_PRESS_KEY = "press_key"
COMMAND_DELETE_TEXT = "delete_text"
COMMAND_KEY_SHORTCUT = "key_shortcut"
COMMAND_SCROLL = "scroll"
COMMAND_LIST_FILES = "list_files"
COMMAND_OPEN_FILE = "open_file"
COMMAND_DATETIME = "datetime"
COMMAND_SCREENSHOT = "screenshot"
COMMAND_SYSTEM_INFO = "system_info"
COMMAND_VOLUME_UP = "volume_up"
COMMAND_VOLUME_DOWN = "volume_down"
COMMAND_VOLUME_MUTE = "volume_mute"
COMMAND_SHUTDOWN = "shutdown"
COMMAND_RESTART = "restart"
COMMAND_POSSIBILITIES = "possibilities"
COMMAND_CLARIFY = "clarify"
COMMAND_UNKNOWN = "unknown"


# Mapa de números por extenso em PT-BR
NUMBER_WORDS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3,
    "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9,
    "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14,
    "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19,
    "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "cem": 100,
}

# Mapa de sites populares
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "reddit": "https://www.reddit.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "amazon": "https://www.amazon.com.br",
    "mercado livre": "https://www.mercadolivre.com.br",
    "linkedin": "https://www.linkedin.com",
    "chatgpt": "https://chatgpt.com",
    "stack overflow": "https://stackoverflow.com",
    "twitch": "https://www.twitch.tv",
    "discord": "https://discord.com/app",
    "tiktok": "https://www.tiktok.com",
    "noticias": "https://news.google.com",
    "g1": "https://g1.globo.com",
}

# Mapa de aplicativos do Windows e seus processos
APPLICATIONS = {
    "bloco de notas": {"exe": "notepad.exe", "process": "notepad.exe"},
    "notepad": {"exe": "notepad.exe", "process": "notepad.exe"},
    "calculadora": {"exe": "calc.exe", "process": "CalculatorApp.exe"},
    "calculador": {"exe": "calc.exe", "process": "CalculatorApp.exe"},
    "explorador": {"exe": "explorer.exe", "process": "explorer.exe"},
    "explorador de arquivos": {"exe": "explorer.exe", "process": "explorer.exe"},
    "explorer": {"exe": "explorer.exe", "process": "explorer.exe"},
    "paint": {"exe": "mspaint.exe", "process": "mspaint.exe"},
    "google chrome": {"exe": "chrome.exe", "process": "chrome.exe"},
    "chrome": {"exe": "chrome.exe", "process": "chrome.exe"},
    "firefox": {"exe": "firefox.exe", "process": "firefox.exe"},
    "edge": {"exe": "msedge.exe", "process": "msedge.exe"},
    "microsoft edge": {"exe": "msedge.exe", "process": "msedge.exe"},
    "word": {"exe": "winword.exe", "process": "WINWORD.EXE"},
    "excel": {"exe": "excel.exe", "process": "EXCEL.EXE"},
    "powerpoint": {"exe": "powerpnt.exe", "process": "POWERPNT.EXE"},
    "power point": {"exe": "powerpnt.exe", "process": "POWERPNT.EXE"},
    "cmd": {"exe": "cmd.exe", "process": "cmd.exe"},
    "terminal": {"exe": "wt.exe", "process": "WindowsTerminal.exe"},
    "prompt de comando": {"exe": "cmd.exe", "process": "cmd.exe"},
    "powershell": {"exe": "powershell.exe", "process": "powershell.exe"},
    "visual studio code": {"exe": "code", "process": "Code.exe"},
    "vs code": {"exe": "code", "process": "Code.exe"},
    "vscode": {"exe": "code", "process": "Code.exe"},
    "gerenciador de tarefas": {"exe": "taskmgr.exe", "process": "Taskmgr.exe"},
    "configurações": {"exe": "ms-settings:", "process": "SystemSettings.exe"},
    "configuracoes": {"exe": "ms-settings:", "process": "SystemSettings.exe"},
    "spotify": {"exe": "spotify.exe", "process": "Spotify.exe"},
    "discord": {"exe": "discord.exe", "process": "Discord.exe"},
    "steam": {"exe": "steam.exe", "process": "steam.exe"},
}


def _remove_wake_word(text):
    """Remove a palavra de ativação 'jarvis' do início do texto."""
    text = text.strip()
    return re.sub(r'^(?:jarvis|járvis)[,.]?\s*', '', text, flags=re.IGNORECASE).strip()


def _normalize(text):
    """Normaliza o texto."""
    return text.lower().strip()


def _extract_after(text, keywords):
    """Extrai o texto que vem depois de uma das palavras-chave."""
    sorted_kws = sorted(keywords, key=len, reverse=True)
    for kw in sorted_kws:
        pattern = re.compile(r'\b' + re.escape(kw) + r'\b\s*(.*)', re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return True, match.group(1).strip()
    return False, ''


def _check_keywords(text, keywords):
    """Verifica se alguma das palavras-chave está presente no texto."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def parse_command(raw_text, pending_clarification=None):
    """
    Analisa o texto de voz ou digitação e retorna (tipo_comando, parâmetros).
    Suporta resolução de contexto pendente para desambiguação.
    """
    text_no_wake = _remove_wake_word(raw_text)
    text_lower = _normalize(text_no_wake)
    
    if not text_lower:
        return COMMAND_UNKNOWN, {"raw": raw_text}
    
    # ----------------------------------------------------
    # 0. RESOLUÇÃO DE CONTEXTO PENDENTE (Perguntas de Desambiguação)
    # ----------------------------------------------------
    if pending_clarification:
        topic = pending_clarification.get("topic")
        
        if topic == "browser_choice":
            if "chrome" in text_lower:
                return COMMAND_OPEN_APP, {"name": "google chrome", "executable": "chrome.exe"}
            elif "edge" in text_lower:
                return COMMAND_OPEN_APP, {"name": "microsoft edge", "executable": "msedge.exe"}
            elif "firefox" in text_lower:
                return COMMAND_OPEN_APP, {"name": "firefox", "executable": "firefox.exe"}
                
        elif topic == "office_choice":
            if "word" in text_lower:
                return COMMAND_OPEN_APP, {"name": "word", "executable": "winword.exe"}
            elif "excel" in text_lower:
                return COMMAND_OPEN_APP, {"name": "excel", "executable": "excel.exe"}
            elif "powerpoint" in text_lower or "power point" in text_lower:
                return COMMAND_OPEN_APP, {"name": "powerpoint", "executable": "powerpnt.exe"}
                
        elif topic == "scroll_direction":
            if _check_keywords(text_lower, ["cima", "subir", "sobe", "suba", "topo"]):
                return COMMAND_SCROLL, {"direction": "up", "amount": 6}
            elif _check_keywords(text_lower, ["baixo", "descer", "desce", "desça", "fim"]):
                return COMMAND_SCROLL, {"direction": "down", "amount": 6}
                
        elif topic == "close_target":
            if _check_keywords(text_lower, ["janela atual", "esta janela", "essa janela", "tela atual", "este app", "esse"]):
                return COMMAND_CLOSE_APP, {"target": "current", "name": "janela atual"}
            for app_k in APPLICATIONS:
                if app_k in text_lower:
                    return COMMAND_CLOSE_APP, {"target": "app", "name": app_k, "process": APPLICATIONS[app_k]["process"]}

    # ----------------------------------------------------
    # 1. MOSTRAR POSSIBILIDADES / COMANDOS / AJUDA
    # ----------------------------------------------------
    possibilities_keywords = [
        "quais possibilidades", "quais possibilidades você tem", "quais possibilidades você possui",
        "quais as possibilidades", "quais possibilidades tem", "quais são as possibilidades",
        "o que você pode fazer", "o que voce pode fazer", "o que você faz", "o que voce faz",
        "quais são seus comandos", "quais sao seus comandos", "quais comandos você tem",
        "quais opções você tem", "quais opcoes voce tem", "quais opções tem",
        "me mostre as possibilidades", "mostrar possibilidades", "mostre as opções",
        "quais são as opções", "lista de comandos", "comandos disponíveis", "ajuda", "menu de opções"
    ]
    if _check_keywords(text_lower, possibilities_keywords) or text_lower in ["possibilidades", "opções", "opcoes", "comandos"]:
        return COMMAND_POSSIBILITIES, {}

    # ----------------------------------------------------
    # 2. SCROLL / ROLAGEM DO MOUSE
    # ----------------------------------------------------
    # Extração de quantidade de scroll se houver (ex: "role 10 vezes para baixo", "rolar muito para cima")
    scroll_amount = 6
    if "muito" in text_lower or "bastante" in text_lower or "tudo" in text_lower:
        scroll_amount = 15
    elif "pouco" in text_lower or "um pouco" in text_lower:
        scroll_amount = 3
    
    # Scroll para Cima
    if _check_keywords(text_lower, [
        "suba", "subir", "subiu",
        "rolar para cima", "role para cima", "rola para cima", "rolar pra cima", "role pra cima",
        "subir a página", "subir pagina", "suba a página", "suba a tela", "sobe a tela", "sobe a página",
        "subir a tela", "subir tela", "subir a tela", "subir página", "subir pagina",
        "scroll para cima", "scroll pra cima", "rolar tela para cima", "role a tela para cima", "scroll up"
    ]):
        return COMMAND_SCROLL, {"direction": "up", "amount": scroll_amount}

    # Scroll para Baixo
    if _check_keywords(text_lower, [
        "desca", "desça", "desceu",
        "rolar para baixo", "role para baixo", "rola para baixo", "rolar pra baixo", "role pra baixo",
        "descer a página", "descer pagina", "desça a página", "desça a tela", "desce a tela", "desce a página",
        "descer a tela", "descer tela", "descer página", "descer pagina",
        "scroll para baixo", "scroll pra baixo", "rolar tela para baixo", "role a tela para baixo", "scroll down"
    ]):
        return COMMAND_SCROLL, {"direction": "down", "amount": scroll_amount}

    # Scroll ambíguo (sem especificar se é para cima ou para baixo)
    if text_lower in ["rolar", "role", "scroll", "rolar a tela", "role a tela", "rolar a página", "role a página", "fazer scroll"]:
        return COMMAND_CLARIFY, {
            "topic": "scroll_direction",
            "question": "Você gostaria de rolar a página para cima ou para baixo?",
            "options": ["Para cima (subir tela)", "Para baixo (descer tela)"]
        }

    # ----------------------------------------------------
    # 3. FECHAR APLICATIVOS / JANELAS
    # ----------------------------------------------------
    close_keywords = [
        "fechar o aplicativo", "feche o aplicativo", "fecha o aplicativo",
        "fechar o programa", "feche o programa", "fecha o programa",
        "fechar a janela", "feche a janela", "fecha a janela",
        "fechar janela atual", "feche janela atual", "feche a janela atual",
        "fechar o", "feche o", "fecha o", "fechar a", "feche a", "fecha a",
        "fechar", "feche", "fecha", "encerrar o", "encerre o", "encerra o",
        "encerrar", "encerre", "finalizar", "finalize"
    ]
    
    # Caso geral de fechar janela atual
    if _check_keywords(text_lower, ["fechar janela", "feche a janela", "feche esta janela", "feche essa janela", "fechar janela atual", "feche janela atual"]):
        return COMMAND_CLOSE_APP, {"target": "current", "name": "janela atual"}
    
    found_close, close_target = _extract_after(text_lower, close_keywords)
    if found_close:
        target_clean = re.sub(r'^(o|a|os|as|do|da|no|na|aplicativo|programa|app)\s+', '', close_target).strip()
        
        if not target_clean or target_clean in ["aplicativo", "programa", "app", "janela"]:
            # Ambíguo: perguntar o que fechar
            return COMMAND_CLARIFY, {
                "topic": "close_target",
                "question": "Qual aplicativo você deseja fechar? Você pode dizer o nome do aplicativo (ex: 'Chrome', 'Bloco de Notas') ou dizer 'janela atual'.",
                "options": ["Janela atual", "Google Chrome", "Bloco de Notas", "Visual Studio Code", "Outro aplicativo"]
            }
        
        # Procura processo mapeado
        for app_name, app_info in sorted(APPLICATIONS.items(), key=lambda x: len(x[0]), reverse=True):
            if app_name == target_clean or app_name in target_clean:
                return COMMAND_CLOSE_APP, {"target": "app", "name": app_name, "process": app_info["process"]}
        
        # Caso genérico
        return COMMAND_CLOSE_APP, {"target": "app", "name": target_clean, "process": f"{target_clean}.exe"}

    # ----------------------------------------------------
    # 4. TRATAMENTO DE COMANDOS ABRANGENTES / AMBÍGUOS
    # ----------------------------------------------------
    # A) Abrir navegador (sem dizer qual)
    if text_lower in ["abra um navegador", "abra o navegador", "abrir navegador", "iniciar navegador", "navegador de internet", "abrir um navegador"]:
        return COMMAND_CLARIFY, {
            "topic": "browser_choice",
            "question": "Identifiquei múltiplos navegadores disponíveis no seu sistema. Você prefere abrir o Google Chrome, Microsoft Edge ou Firefox?",
            "options": ["Google Chrome", "Microsoft Edge", "Firefox"]
        }

    # B) Abrir Office (sem dizer qual aplicativo)
    if text_lower in ["abra o office", "abrir office", "abrir microsoft office", "abra o pacote office", "pacote office"]:
        return COMMAND_CLARIFY, {
            "topic": "office_choice",
            "question": "O pacote Office possui diversos programas. Qual deles você gostaria de abrir: Word, Excel ou PowerPoint?",
            "options": ["Microsoft Word", "Microsoft Excel", "Microsoft PowerPoint"]
        }

    # ----------------------------------------------------
    # 5. TECLAS ESPECÍFICAS (Enter, Esc, Tab, Espaço)
    # ----------------------------------------------------
    enter_matches = ["enter", "dar enter", "da enter", "dê enter", "de enter",
                     "pressione enter", "aperte enter", "aperta enter", "tecla enter"]
    if text_lower in enter_matches or any(text_lower == m for m in enter_matches):
        return COMMAND_PRESS_KEY, {"key": "enter", "name": "Enter"}
    
    esc_matches = ["esc", "escape", "pressione esc", "aperte esc", "aperta esc",
                   "tecla esc", "cancelar", "tecla escape"]
    if text_lower in esc_matches or any(text_lower == m for m in esc_matches):
        return COMMAND_PRESS_KEY, {"key": "esc", "name": "Escape"}
    
    tab_matches = ["tab", "pressione tab", "aperte tab", "aperta tab", "tecla tab"]
    if text_lower in tab_matches or any(text_lower == m for m in tab_matches):
        return COMMAND_PRESS_KEY, {"key": "tab", "name": "Tab"}
    
    space_matches = ["espaço", "espaco", "barra de espaço", "barra de espaco", "pressione espaço", "aperte espaço"]
    if text_lower in space_matches:
        return COMMAND_PRESS_KEY, {"key": "space", "name": "Espaço"}

    # ----------------------------------------------------
    # 6. COMANDOS DE APAGAR / MANIPULAÇÃO DE TEXTO
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["apagar tudo", "apague tudo", "apaga tudo",
                                     "deletar tudo", "delete tudo", "limpar tudo", "limpe tudo"]):
        return COMMAND_DELETE_TEXT, {"mode": "all", "description": "todo o texto"}

    if _check_keywords(text_lower, ["apagar última palavra", "apagar ultima palavra",
                                     "apague a última palavra", "apague a ultima palavra",
                                     "apague última palavra", "apague ultima palavra",
                                     "apaga última palavra", "apaga ultima palavra",
                                     "apagar a última palavra", "apagar a ultima palavra",
                                     "apagar palavra", "apague palavra", "apaga palavra",
                                     "deletar última palavra", "deletar ultima palavra"]):
        return COMMAND_DELETE_TEXT, {"mode": "word", "description": "a última palavra"}

    delete_n_regex = re.compile(r'(?:apagar|apague|apaga|deletar|delete)\s+(\d+|\w+)\s+(?:caracteres|caracter|carácteres|letras|letra)', re.IGNORECASE)
    n_match = delete_n_regex.search(text_lower)
    if n_match:
        val_str = n_match.group(1).lower()
        count = 1
        if val_str.isdigit():
            count = int(val_str)
        elif val_str in NUMBER_WORDS:
            count = NUMBER_WORDS[val_str]
        return COMMAND_DELETE_TEXT, {"mode": "count", "count": max(1, count), "description": f"{count} caracteres"}

    exact_delete_single = [
        "apagar", "apague", "apaga", "deletar", "delete", "backspace",
        "apagar caractere", "apague o caractere", "apagar letra", "apague a letra",
        "apagar último caractere", "apagar ultimo caractere",
        "apagar última letra", "apagar ultima letra"
    ]
    if text_lower in exact_delete_single:
        return COMMAND_DELETE_TEXT, {"mode": "char", "count": 1, "description": "o último caractere"}

    # ----------------------------------------------------
    # 7. ATALHOS DE TECLADO RÁPIDOS
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["selecionar tudo", "selecione tudo", "marcar tudo", "marque tudo"]):
        return COMMAND_KEY_SHORTCUT, {"action": "select_all", "keys": ["ctrl", "a"], "name": "Selecionar Tudo"}
    
    if _check_keywords(text_lower, ["copiar", "copie", "copia"]):
        return COMMAND_KEY_SHORTCUT, {"action": "copy", "keys": ["ctrl", "c"], "name": "Copiar"}
    
    if _check_keywords(text_lower, ["colar", "cole", "cola"]):
        return COMMAND_KEY_SHORTCUT, {"action": "paste", "keys": ["ctrl", "v"], "name": "Colar"}
    
    if _check_keywords(text_lower, ["desfazer", "desfaça", "desfaca"]):
        return COMMAND_KEY_SHORTCUT, {"action": "undo", "keys": ["ctrl", "z"], "name": "Desfazer"}
    
    if _check_keywords(text_lower, ["salvar", "salve", "salva"]):
        return COMMAND_KEY_SHORTCUT, {"action": "save", "keys": ["ctrl", "s"], "name": "Salvar"}

    # ----------------------------------------------------
    # 8. HORA E DATA
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["que horas", "que hora", "horas são", "hora é",
                                     "que dia", "data de hoje", "dia é hoje",
                                     "data atual", "hora atual", "horário", "horario"]):
        return COMMAND_DATETIME, {}

    # ----------------------------------------------------
    # 9. SCREENSHOT
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["print", "screenshot", "captura de tela",
                                     "tire um print", "tira um print", "tirar print",
                                     "captura a tela", "capturar tela",
                                     "foto da tela", "printscreen"]):
        return COMMAND_SCREENSHOT, {}

    # ----------------------------------------------------
    # 10. INFO DO SISTEMA
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["como está o sistema", "como esta o sistema",
                                     "status do sistema", "informações do sistema",
                                     "como está o pc", "como esta o pc",
                                     "como está o computador", "como esta o computador",
                                     "desempenho do pc", "status do pc", "uso de memória",
                                     "uso de cpu", "nível da bateria", "nivel da bateria"]):
        return COMMAND_SYSTEM_INFO, {}

    # ----------------------------------------------------
    # 11. VOLUME
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["aumente o volume", "aumentar volume", "aumenta o volume",
                                     "volume mais alto", "mais alto", "sobe o volume",
                                     "subir volume", "sobe volume"]):
        return COMMAND_VOLUME_UP, {}
    
    if _check_keywords(text_lower, ["diminua o volume", "diminuir volume", "diminui o volume",
                                     "volume mais baixo", "mais baixo", "abaixa o volume",
                                     "abaixar volume", "abaixa volume", "baixa o volume"]):
        return COMMAND_VOLUME_DOWN, {}
    
    if _check_keywords(text_lower, ["mutar", "mude o som", "silenciar", "silêncio",
                                     "silencia", "tira o som", "sem som", "mudo"]):
        return COMMAND_VOLUME_MUTE, {}

    # ----------------------------------------------------
    # 12. DESLIGAR / REINICIAR
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["desligar o computador", "desligar o pc", "desligue o computador",
                                     "desligue o pc", "desliga o pc", "desligar computador"]):
        return COMMAND_SHUTDOWN, {}
    
    if _check_keywords(text_lower, ["reiniciar o computador", "reiniciar o pc", "reinicie o computador",
                                     "reinicie o pc", "reinicia o pc"]):
        return COMMAND_RESTART, {}

    # ----------------------------------------------------
    # 13. ABRIR ARQUIVO
    # ----------------------------------------------------
    file_open_kws = ["abra o arquivo", "abre o arquivo", "abrir o arquivo",
                     "abrir arquivo", "abra arquivo", "abre arquivo"]
    found_file, filename = _extract_after(text_lower, file_open_kws)
    if found_file and filename:
        return COMMAND_OPEN_FILE, {"filename": filename}

    # ----------------------------------------------------
    # 14. LISTAR ARQUIVOS
    # ----------------------------------------------------
    if _check_keywords(text_lower, ["liste", "listar", "lista", "mostre os arquivos",
                                      "mostrar arquivos", "quais arquivos", "ver arquivos"]):
        if "documentos" in text_lower or "documento" in text_lower:
            return COMMAND_LIST_FILES, {"path": "documents"}
        elif "desktop" in text_lower or "área de trabalho" in text_lower or "area de trabalho" in text_lower:
            return COMMAND_LIST_FILES, {"path": "desktop"}
        elif "downloads" in text_lower or "download" in text_lower:
            return COMMAND_LIST_FILES, {"path": "downloads"}
        elif "imagens" in text_lower or "fotos" in text_lower or "pictures" in text_lower:
            return COMMAND_LIST_FILES, {"path": "pictures"}
        elif "músicas" in text_lower or "musicas" in text_lower or "music" in text_lower:
            return COMMAND_LIST_FILES, {"path": "music"}
        elif "vídeos" in text_lower or "videos" in text_lower:
            return COMMAND_LIST_FILES, {"path": "videos"}
        else:
            return COMMAND_LIST_FILES, {"path": "documents"}

    # ----------------------------------------------------
    # 15. ESCREVER / DIGITAR TEXTO
    # ----------------------------------------------------
    type_keywords = ["escreva", "escrever", "digite", "digitar", "digita",
                     "escreve", "anote", "anotar", "anota"]
    found_type, content = _extract_after(text_lower, type_keywords)
    if found_type and content:
        orig_found, orig_content = _extract_after(text_no_wake, type_keywords)
        return COMMAND_TYPE_TEXT, {"text": orig_content if orig_found else content}

    # ----------------------------------------------------
    # 16. PESQUISAR NA INTERNET
    # ----------------------------------------------------
    search_keywords = [
        "pesquise sobre", "pesquisa sobre", "pesquisar sobre",
        "pesquise por", "pesquisa por", "pesquisar por",
        "busque sobre", "busque por", "buscar por", "buscar sobre",
        "procure sobre", "procure por", "procura por",
        "pesquise no google", "pesquisa no google", "busque no google",
        "pesquise", "pesquisar", "pesquisa", "busque", "buscar", "procure", "procura"
    ]
    found_search, query = _extract_after(text_lower, search_keywords)
    if found_search and query:
        query_clean = re.sub(r'^(sobre|por|no google|na internet|o que é|quem é)\s*', '', query).strip()
        if query_clean:
            return COMMAND_SEARCH_WEB, {"query": query_clean}

    # ----------------------------------------------------
    # 17. ABRIR SITE OU APLICATIVO
    # ----------------------------------------------------
    open_keywords = [
        "abra o site", "abre o site", "abrir o site",
        "abra a página", "abre a página", "abrir a página",
        "entre no site", "entre na página", "acesse o site", "acesse a página",
        "abra o", "abre o", "abrir o", "abra a", "abre a", "abrir a",
        "abra", "abre", "abrir", "entre no", "entre na", "acesse o", "acesse a"
    ]
    found_open, target = _extract_after(text_lower, open_keywords)
    if found_open and target:
        target_clean = re.sub(r'^(o|a|os|as|do|da|no|na)\s+', '', target).strip()
        
        for app_name in sorted(APPLICATIONS.keys(), key=len, reverse=True):
            if app_name == target_clean or app_name in target_clean:
                return COMMAND_OPEN_APP, {"name": app_name, "executable": APPLICATIONS[app_name]["exe"]}
        
        for site_name in sorted(WEBSITES.keys(), key=len, reverse=True):
            if site_name == target_clean or site_name in target_clean:
                return COMMAND_OPEN_SITE, {"name": site_name, "url": WEBSITES[site_name]}
        
        if "." in target_clean or "http" in target_clean or "www" in target_clean:
            url = target_clean
            if not url.startswith("http"):
                url = "https://" + url
            return COMMAND_OPEN_SITE, {"name": target_clean, "url": url}
        
        return COMMAND_OPEN_APP, {"name": target_clean, "executable": target_clean}

    return COMMAND_UNKNOWN, {"raw": raw_text, "processed": text_lower}
