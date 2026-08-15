"""
J.A.R.V.I.S. — Just A Rather Very Intelligent System

Assistente de voz desktop para Windows.
Ponto de entrada principal do software.
"""

import sys
import os
import threading
import queue
import time

import customtkinter as ctk
import speech_recognition as sr

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import JarvisUI
from audio_recorder import SoundDeviceMicrophone
from nlp import (
    parse_command,
    COMMAND_OPEN_APP, COMMAND_CLOSE_APP, COMMAND_SEARCH_WEB, COMMAND_OPEN_SITE,
    COMMAND_TYPE_TEXT, COMMAND_PRESS_KEY, COMMAND_DELETE_TEXT,
    COMMAND_KEY_SHORTCUT, COMMAND_SCROLL, COMMAND_LIST_FILES, COMMAND_OPEN_FILE,
    COMMAND_DATETIME, COMMAND_SCREENSHOT, COMMAND_SYSTEM_INFO,
    COMMAND_VOLUME_UP, COMMAND_VOLUME_DOWN, COMMAND_VOLUME_MUTE,
    COMMAND_SHUTDOWN, COMMAND_RESTART, COMMAND_POSSIBILITIES, COMMAND_CLARIFY,
    COMMAND_UNKNOWN,
)
from commands import (
    open_application, close_application, search_web, open_website, type_text,
    press_key, delete_text, keyboard_shortcut, scroll_page, get_possibilities,
    list_files, open_file, get_datetime, take_screenshot,
    system_info, control_volume, shutdown_pc, restart_pc,
    cancel_shutdown,
)


# ============================================================
# MOTOR DE VOZ
# ============================================================

class VoiceEngine:
    """Motor de reconhecimento de voz e síntese de fala."""
    
    def __init__(self, ui: JarvisUI):
        self.ui = ui
        self.is_running = False
        self.stop_event = threading.Event()
        self.listen_thread = None
        self.recognizer = sr.Recognizer()
        self.pending_clarification = None
        
        # Inicializa TTS e STT
        self._init_tts()
        self._init_stt()
    
    def _init_tts(self):
        """Inicializa o motor de texto-para-fala (pyttsx3)."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configurar voz em português
            voices = self.tts_engine.getProperty('voices')
            pt_voice = None
            
            for voice in voices:
                v_name = voice.name.lower()
                v_langs = [str(l).lower() for l in getattr(voice, 'languages', [])]
                if any(k in v_name for k in ['portuguese', 'brazil', 'brasil', 'pt-br', 'maria', 'daniel', 'helena']):
                    pt_voice = voice.id
                    break
                elif any('pt' in l or 'portuguese' in l for l in v_langs):
                    pt_voice = voice.id
                    break
            
            if pt_voice:
                self.tts_engine.setProperty('voice', pt_voice)
                self.ui.queue_message("log_detail", "Voz TTS configurada para Português (Brasil).")
            elif voices:
                self.tts_engine.setProperty('voice', voices[0].id)
                self.ui.queue_message("log_detail", f"Voz padrão configurada: {voices[0].name}")
            
            # Velocidade da fala e volume
            self.tts_engine.setProperty('rate', 210)
            self.tts_engine.setProperty('volume', 1.0)
            self.tts_available = True
        except Exception as e:
            self.tts_available = False
            self.ui.queue_message("error", f"Aviso TTS: {e}")
    
    def _init_stt(self):
        """Inicializa o microfone inteligente via SoundDevice."""
        try:
            self.mic = SoundDeviceMicrophone(sample_rate=16000)
            self.stt_available = True
            
            # Calibração rápida em thread de background
            def _calibrate():
                self.ui.queue_message("log_detail", "Calibrando microfone para ruído ambiente...")
                threshold = self.mic.adjust_for_ambient_noise(duration=0.4)
                self.ui.queue_message("log_success", f"Microfone calibrado (Sensibilidade: {int(threshold)}). Pronto!")
            
            threading.Thread(target=_calibrate, daemon=True).start()
        except Exception as e:
            self.stt_available = False
            self.ui.queue_message("error", f"Erro no microfone: {e}")

    def speak(self, text):
        """Fala o texto usando pyttsx3 em thread separada."""
        if not self.tts_available:
            return
        
        def _speak_thread():
            try:
                self.ui.queue_message("state_change", "speaking")
                # Cria uma instância segura de TTS na thread se necessário
                import pyttsx3
                engine = pyttsx3.init()
                
                # Configurar mesma voz
                voice = self.tts_engine.getProperty('voice')
                if voice:
                    engine.setProperty('voice', voice)
                engine.setProperty('rate', 210)
                
                engine.say(text)
                engine.runAndWait()
                
                if self.is_running:
                    self.ui.queue_message("state_change", "listening")
                else:
                    self.ui.queue_message("state_change", "idle")
            except Exception as e:
                self.ui.queue_message("error", f"Erro na fala: {e}")
                self.ui.queue_message("state_change", "idle")
        
        threading.Thread(target=_speak_thread, daemon=True).start()
    
    def start_listening(self):
        """Inicia a escuta contínua em uma thread separada."""
        if not self.stt_available:
            self.ui.queue_message("error", "Microfone não está disponível.")
            return
        
        self.is_running = True
        self.stop_event.clear()
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
    
    def stop_listening(self):
        """Para a escuta."""
        self.is_running = False
        self.stop_event.set()
    
    def _listen_loop(self):
        """Loop de escuta contínua — roda em background."""
        self.speak("Olá! J.A.R.V.I.S. online. Como posso ajudar?")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                self.ui.queue_message("state_change", "listening")
                
                # Captura frase usando nosso SoundDeviceMicrophone inteligente
                audio_data = self.mic.listen_phrase(
                    timeout=3.0,
                    phrase_time_limit=8.0,
                    silence_limit=0.7,
                    stop_event=self.stop_event
                )
                
                if self.stop_event.is_set() or not self.is_running:
                    break
                
                if audio_data is None:
                    # Timeout de silêncio: continua em loop de escuta
                    continue
                
                # Processando áudio
                self.ui.queue_message("state_change", "processing")
                
                try:
                    # Reconhecimento Google em Português
                    text = self.recognizer.recognize_google(audio_data, language="pt-BR")
                    if text and text.strip():
                        self.ui.queue_message("user_said", text.strip())
                        self.speak(text.strip())
                        self._process_command(text.strip())
                except sr.UnknownValueError:
                    # Não identificou palavras claras
                    pass
                except sr.RequestError as e:
                    self.ui.queue_message("error", f"Erro de conexão com serviço de voz: {e}")
                    time.sleep(2)
            
            except Exception as e:
                if self.is_running and not self.stop_event.is_set():
                    self.ui.queue_message("error", f"Falha na escuta: {e}")
                    time.sleep(1)
        
        self.ui.queue_message("state_change", "idle")
        self.ui.queue_message("voice_stopped", None)
    
    def _process_command(self, text):
        """Processa e despacha o comando reconhecido com suporte a desambiguação."""
        cmd_type, params = parse_command(text, self.pending_clarification)
        
        # Se não for uma nova pergunta de clarificação, limpa o contexto pendente
        if cmd_type != COMMAND_CLARIFY:
            self.pending_clarification = None
            
        try:
            if cmd_type == COMMAND_CLARIFY:
                self.pending_clarification = params
                question = params.get("question", "Poderia especificar qual opção deseja?")
                options = params.get("options", [])
                
                # Monta visualização no log
                log_msg = f"{question}"
                if options:
                    opt_str = "\n".join([f"   • {opt}" for opt in options])
                    log_msg += f"\n\nOpções disponíveis:\n{opt_str}"
                    
                self.ui.queue_message("jarvis_response", log_msg)
                self.speak(question)

            elif cmd_type == COMMAND_POSSIBILITIES:
                detail_text, voice_text = get_possibilities()
                self.ui.queue_message("jarvis_response", detail_text)
                self.speak(voice_text)

            elif cmd_type == COMMAND_SCROLL:
                direction = params.get("direction", "down")
                amount = params.get("amount", 6)
                response = scroll_page(direction=direction, amount=amount)
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)

            elif cmd_type == COMMAND_CLOSE_APP:
                target = params.get("target", "app")
                name = params.get("name")
                process = params.get("process")
                response = close_application(target=target, name=name, process=process)
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)

            elif cmd_type == COMMAND_OPEN_APP:
                response = open_application(params["name"], params.get("executable"))
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_SEARCH_WEB:
                response = search_web(params["query"])
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_OPEN_SITE:
                response = open_website(params["name"], params["url"])
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_TYPE_TEXT:
                self.ui.queue_message("jarvis_response", f"Digitando: {params['text']}")
                self.speak("Digitando.")
                response = type_text(params["text"])
                self.ui.queue_message("log_detail", response)
            
            elif cmd_type == COMMAND_PRESS_KEY:
                key_name = params.get("key", "enter")
                display_name = params.get("name", key_name.upper())
                response = press_key(key_name)
                self.ui.queue_message("jarvis_response", response)
                self.speak(f"Tecla {display_name} pressionada.")
            
            elif cmd_type == COMMAND_DELETE_TEXT:
                mode = params.get("mode", "char")
                count = params.get("count", 1)
                desc = params.get("description", "texto")
                response = delete_text(mode=mode, count=count)
                self.ui.queue_message("jarvis_response", response)
                self.speak(f"Apagando {desc}.")
            
            elif cmd_type == COMMAND_KEY_SHORTCUT:
                keys = params.get("keys", [])
                action_name = params.get("name", "Atalho")
                response = keyboard_shortcut(keys, action_name)
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_LIST_FILES:
                result = list_files(params.get("path", "documents"))
                if isinstance(result, tuple):
                    detail_text, voice_text = result
                    self.ui.queue_message("jarvis_response", detail_text)
                    self.speak(voice_text)
                else:
                    self.ui.queue_message("jarvis_response", result)
                    self.speak(result)
            
            elif cmd_type == COMMAND_OPEN_FILE:
                response = open_file(params["filename"])
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_DATETIME:
                response = get_datetime()
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_SCREENSHOT:
                self.speak("Tirando captura de tela.")
                response = take_screenshot()
                self.ui.queue_message("jarvis_response", response)
                self.speak("Captura realizada com sucesso.")
            
            elif cmd_type == COMMAND_SYSTEM_INFO:
                result = system_info()
                if isinstance(result, tuple):
                    detail_text, voice_text = result
                    self.ui.queue_message("jarvis_response", detail_text)
                    self.speak(voice_text)
                else:
                    self.ui.queue_message("jarvis_response", result)
                    self.speak(result)
            
            elif cmd_type == COMMAND_VOLUME_UP:
                response = control_volume("up")
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_VOLUME_DOWN:
                response = control_volume("down")
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_VOLUME_MUTE:
                response = control_volume("mute")
                self.ui.queue_message("jarvis_response", response)
                self.speak(response)
            
            elif cmd_type == COMMAND_SHUTDOWN:
                self.speak("Aviso: o computador será desligado em 30 segundos. Para cancelar diga cancelar desligamento.")
                response = shutdown_pc()
                self.ui.queue_message("jarvis_response", response)
            
            elif cmd_type == COMMAND_RESTART:
                self.speak("Aviso: o computador será reiniciado em 30 segundos.")
                response = restart_pc()
                self.ui.queue_message("jarvis_response", response)
            
            elif cmd_type == COMMAND_UNKNOWN:
                response = f"Não compreendi o comando: \"{params.get('processed', params.get('raw', text))}\""
                self.ui.queue_message("jarvis_response", response)
                self.speak("Desculpe, não entendi o comando. Poderia repetir?")
        
        except Exception as e:
            error_msg = f"Erro ao executar comando: {str(e)}"
            self.ui.queue_message("error", error_msg)
            self.speak("Ocorreu um problema ao executar essa ação.")


# ============================================================
# PONTO DE ENTRADA
# ============================================================

def main():
    """Função principal — inicializa e roda o J.A.R.V.I.S."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    voice_engine = None
    
    def on_start_voice():
        nonlocal voice_engine
        if voice_engine is None:
            voice_engine = VoiceEngine(ui)
        voice_engine.start_listening()
    
    def on_stop_voice():
        if voice_engine:
            voice_engine.stop_listening()
    
    def on_text_command(text):
        """Processa comando digitado pelo usuário na interface."""
        nonlocal voice_engine
        if voice_engine is None:
            voice_engine = VoiceEngine(ui)
        
        ui.log_user(text)
        
        # Executa em thread separada para não travar a interface
        def _exec_text():
            ui.queue_message("state_change", "processing")
            voice_engine._process_command(text)
        
        threading.Thread(target=_exec_text, daemon=True).start()
    
    ui = JarvisUI(
        root,
        voice_callback=on_start_voice,
        stop_callback=on_stop_voice,
        text_command_callback=on_text_command,
    )
    
    # Inicializa o motor de voz imediatamente para calibração em background
    voice_engine = VoiceEngine(ui)
    
    def on_closing():
        if voice_engine:
            voice_engine.stop_listening()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Mensagens de boas-vindas
    ui.log_jarvis("Protocolos de inteligência inicializados.")
    ui.log_system("Você pode falar clicando em 'Ativar Voz' ou digitar um comando diretamente abaixo.")
    
    root.mainloop()


if __name__ == "__main__":
    main()
