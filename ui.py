"""
J.A.R.V.I.S. — Interface Gráfica Desktop

Interface futurista estilo Homem de Ferro usando CustomTkinter.
Inclui círculo animado reativo, visualização de status, métricas do PC e log de atividades.
"""

import customtkinter as ctk
import tkinter as tk
import math
import datetime
import queue


# ============================================================
# CONSTANTES DE DESIGN
# ============================================================

COLOR_BG_DARK = "#06080d"
COLOR_BG_PANEL = "#0c1018"
COLOR_BG_CARD = "#111822"
COLOR_BLUE = "#0099ff"
COLOR_CYAN = "#00d4ff"
COLOR_CYAN_DIM = "#005f73"
COLOR_TEXT = "#c8d6e5"
COLOR_TEXT_DIM = "#5a7082"
COLOR_ACCENT = "#00b4d8"
COLOR_SUCCESS = "#00e676"
COLOR_WARNING = "#ffab00"
COLOR_ERROR = "#ff3d00"
COLOR_USER_MSG = "#00a8ff"
COLOR_JARVIS_MSG = "#00e5ff"

FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 26, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13)
FONT_STATUS = (FONT_FAMILY, 11)
FONT_LOG = (FONT_FAMILY, 12)
FONT_LOG_BOLD = (FONT_FAMILY, 12, "bold")
FONT_BUTTON = (FONT_FAMILY, 14, "bold")
FONT_SMALL = (FONT_FAMILY, 10)


# ============================================================
# CLASSE PRINCIPAL DA UI
# ============================================================

class JarvisUI:
    """Interface gráfica interativa do J.A.R.V.I.S."""
    
    def __init__(self, root, voice_callback=None, stop_callback=None, text_command_callback=None):
        self.root = root
        self.voice_callback = voice_callback
        self.stop_callback = stop_callback
        self.text_command_callback = text_command_callback
        
        # Estado da animação
        self.state = "idle"  # idle, listening, processing, speaking
        self.animation_angle = 0
        self.pulse_phase = 0
        self.ring_angles = [0, 120, 240]
        self.is_listening = False
        self.audio_level = 0.0
        
        # Centro do Canvas dinâmico
        self.cx = 550
        self.cy = 130
        
        # Fila de mensagens da thread de voz
        self.message_queue = queue.Queue()
        
        self._setup_window()
        self._build_ui()
        self._start_animations()
        self._check_message_queue()
    
    def _setup_window(self):
        """Configura a janela principal."""
        self.root.title("J.A.R.V.I.S. — Voice & Command Assistant")
        
        width, height = 1100, 780
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(880, 620)
        self.root.configure(fg_color=COLOR_BG_DARK)
    
    def _build_ui(self):
        """Monta todos os componentes da interface."""
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLOR_BG_DARK, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self._build_header()
        self._build_center()
        self._build_log()
        self._build_status_bar()
    
    def _build_header(self):
        """Cabeçalho com título estilizado e status de conexão."""
        header = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG_PANEL, height=58, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)
        
        title = ctk.CTkLabel(
            title_frame,
            text="J.A.R.V.I.S.",
            font=FONT_TITLE,
            text_color=COLOR_CYAN,
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="  //  SISTEMA DE COMANDO POR VOZ E TEXTO",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_DIM,
        )
        subtitle.pack(side="left", padx=(8, 0), pady=(6, 0))
        
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=20, pady=10)
        
        self.status_dot = ctk.CTkLabel(
            status_frame,
            text="●",
            font=(FONT_FAMILY, 14),
            text_color=COLOR_SUCCESS,
        )
        self.status_dot.pack(side="left", padx=(0, 6))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="SISTEMA ATIVO",
            font=FONT_STATUS,
            text_color=COLOR_TEXT_DIM,
        )
        self.status_label.pack(side="left")
        
        sep = ctk.CTkFrame(self.main_frame, fg_color=COLOR_CYAN_DIM, height=1, corner_radius=0)
        sep.pack(fill="x")
    
    def _build_center(self):
        """Área do HUD animado com o reator ARC/círculo pulsante e barra de comandos."""
        center_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG_DARK, corner_radius=0)
        center_frame.pack(fill="x", padx=0, pady=0)
        
        self.canvas = tk.Canvas(
            center_frame,
            width=1100,
            height=250,
            bg=COLOR_BG_DARK,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(pady=(8, 0), fill="x", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        self.state_label = ctk.CTkLabel(
            center_frame,
            text="Aguardando comando por voz ou digitação...",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_DIM,
        )
        self.state_label.pack(pady=(2, 6))
        
        # Barra de Controles (Voz + Campo de Digitação)
        control_bar = ctk.CTkFrame(center_frame, fg_color="transparent")
        control_bar.pack(pady=(0, 10), fill="x", padx=40)
        
        # Botão de Microfone
        self.mic_button = ctk.CTkButton(
            control_bar,
            text="🎤  Ativar Voz",
            font=FONT_BUTTON,
            fg_color=COLOR_BLUE,
            hover_color=COLOR_CYAN,
            text_color="#ffffff",
            width=160,
            height=42,
            corner_radius=21,
            command=self._toggle_voice,
        )
        self.mic_button.pack(side="left", padx=(0, 12))
        
        # Container de Entrada de Texto
        input_container = ctk.CTkFrame(control_bar, fg_color=COLOR_BG_CARD, corner_radius=21, height=42)
        input_container.pack(side="left", fill="x", expand=True)
        input_container.pack_propagate(False)
        
        self.cmd_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Digite um comando aqui (ex: 'abra o youtube', 'que horas são?', 'pesquise sobre IA')...",
            placeholder_text_color=COLOR_TEXT_DIM,
            font=FONT_LOG,
            fg_color="transparent",
            text_color=COLOR_TEXT,
            border_width=0,
        )
        self.cmd_entry.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=2)
        self.cmd_entry.bind("<Return>", lambda e: self._on_send_text_command())
        
        # Botão Enviar
        self.send_button = ctk.CTkButton(
            input_container,
            text="Enviar ➔",
            font=FONT_LOG_BOLD,
            fg_color=COLOR_CYAN_DIM,
            hover_color=COLOR_BLUE,
            text_color="#ffffff",
            width=90,
            height=34,
            corner_radius=17,
            command=self._on_send_text_command,
        )
        self.send_button.pack(side="right", padx=(0, 4), pady=4)

    def _on_send_text_command(self):
        """Dispara o comando de texto digitado."""
        text = self.cmd_entry.get().strip()
        if text:
            self.cmd_entry.delete(0, "end")
            if self.text_command_callback:
                self.text_command_callback(text)
    
    def _on_canvas_resize(self, event):
        """Adapta o centro da animação à largura real da janela."""
        self.cx = event.width // 2
        self.cy = event.height // 2
    
    def _build_log(self):
        """Painel com histórico de comandos e respostas."""
        log_container = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG_PANEL, corner_radius=10)
        log_container.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        
        log_header = ctk.CTkFrame(log_container, fg_color="transparent", height=32)
        log_header.pack(fill="x", padx=14, pady=(8, 2))
        log_header.pack_propagate(False)
        
        ctk.CTkLabel(
            log_header,
            text="📋  HISTÓRICO DE ATIVIDADE",
            font=FONT_LOG_BOLD,
            text_color=COLOR_TEXT_DIM,
        ).pack(side="left")
        
        clear_btn = ctk.CTkButton(
            log_header,
            text="Limpar",
            font=FONT_SMALL,
            fg_color="transparent",
            hover_color=COLOR_BG_CARD,
            text_color=COLOR_TEXT_DIM,
            width=50,
            height=24,
            corner_radius=12,
            command=self._clear_log,
        )
        clear_btn.pack(side="right")
        
        self.log_text = ctk.CTkTextbox(
            log_container,
            font=FONT_LOG,
            fg_color=COLOR_BG_CARD,
            text_color=COLOR_TEXT,
            corner_radius=6,
            wrap="word",
            state="disabled",
            scrollbar_button_color=COLOR_CYAN_DIM,
            scrollbar_button_hover_color=COLOR_BLUE,
        )
        self.log_text.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        
        self.log_text._textbox.tag_configure("user", foreground=COLOR_USER_MSG)
        self.log_text._textbox.tag_configure("jarvis", foreground=COLOR_JARVIS_MSG)
        self.log_text._textbox.tag_configure("system", foreground=COLOR_TEXT_DIM)
        self.log_text._textbox.tag_configure("error", foreground=COLOR_ERROR)
        self.log_text._textbox.tag_configure("timestamp", foreground=COLOR_TEXT_DIM)
        self.log_text._textbox.tag_configure("success", foreground=COLOR_SUCCESS)
    
    def _build_status_bar(self):
        """Barra inferior com métricas do sistema em tempo real."""
        status_bar = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG_PANEL, height=32, corner_radius=0)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        self.bottom_status = ctk.CTkLabel(
            status_bar,
            text="● PRONTO",
            font=FONT_SMALL,
            text_color=COLOR_SUCCESS,
        )
        self.bottom_status.pack(side="left", padx=16)
        
        self.system_info_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_DIM,
        )
        self.system_info_label.pack(side="right", padx=16)
        
        self._update_system_info()
    
    # --------------------------------------------------------
    # ANIMAÇÕES DO CANVAS (HUD / ARC REACTOR)
    # --------------------------------------------------------
    
    def _start_animations(self):
        self._animate()
    
    def _animate(self):
        self.canvas.delete("all")
        cx, cy = self.cx, self.cy
        
        if self.state == "idle":
            self._draw_idle(cx, cy)
        elif self.state == "listening":
            self._draw_listening(cx, cy)
        elif self.state == "processing":
            self._draw_processing(cx, cy)
        elif self.state == "speaking":
            self._draw_speaking(cx, cy)
        
        self.animation_angle = (self.animation_angle + 1.8) % 360
        self.pulse_phase += 0.07
        
        for i in range(len(self.ring_angles)):
            self.ring_angles[i] = (self.ring_angles[i] + (1.2 + i * 0.5)) % 360
        
        self.root.after(33, self._animate)
    
    def _draw_idle(self, cx, cy):
        pulse = math.sin(self.pulse_phase) * 6
        base_r = 55
        r = base_r + pulse
        
        for i, offset in enumerate([30, 48, 64]):
            ring_r = base_r + offset
            self.canvas.create_oval(
                cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r,
                outline=COLOR_CYAN_DIM,
                width=1,
                dash=(3, 7),
            )
        
        for i, angle in enumerate(self.ring_angles):
            arc_r = base_r + 25 + i * 14
            self.canvas.create_arc(
                cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                start=angle, extent=45,
                outline=COLOR_CYAN_DIM,
                width=2,
                style="arc",
            )
        
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=COLOR_BLUE,
            width=2.5,
        )
        
        inner_r = r * 0.6
        self.canvas.create_oval(
            cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
            outline=COLOR_CYAN,
            width=1,
        )
        
        self.canvas.create_text(
            cx, cy,
            text="J",
            font=(FONT_FAMILY, 26, "bold"),
            fill=COLOR_CYAN,
        )
        
        for side in [-1, 1]:
            x_start = cx + side * (base_r + 75)
            x_end = cx + side * (base_r + 170)
            self.canvas.create_line(
                x_start, cy, x_end, cy,
                fill=COLOR_CYAN_DIM,
                width=1,
                dash=(4, 6),
            )
    
    def _draw_listening(self, cx, cy):
        num_waves = 4
        for i in range(num_waves):
            wave_phase = (self.pulse_phase * 1.6 + i * 1.4) % (math.pi * 2)
            wave_r = 55 + (math.sin(wave_phase) + 1) * 45
            opacity = max(0.1, 1 - (wave_r - 55) / 90)
            
            blue_val = int(0x88 * opacity)
            cyan_val = int(0xee * opacity)
            color = f"#00{blue_val:02x}{cyan_val:02x}"
            try:
                self.canvas.create_oval(
                    cx - wave_r, cy - wave_r, cx + wave_r, cy + wave_r,
                    outline=color,
                    width=2,
                )
            except Exception:
                pass
        
        for i, angle in enumerate(self.ring_angles):
            arc_r = 80 + i * 16
            self.canvas.create_arc(
                cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                start=angle, extent=65,
                outline=COLOR_CYAN,
                width=2.5,
                style="arc",
            )
            self.canvas.create_arc(
                cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                start=angle + 180, extent=65,
                outline=COLOR_BLUE,
                width=2,
                style="arc",
            )
        
        pulse = math.sin(self.pulse_phase * 2.2) * 5
        r = 55 + pulse
        
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=COLOR_CYAN,
            width=3,
        )
        
        num_bars = 20
        for i in range(num_bars):
            angle_rad = math.radians(i * (360 / num_bars) + self.animation_angle * 0.6)
            bar_height = 8 + math.sin(self.pulse_phase * 3.5 + i * 0.8) * 14
            inner = r + 8
            outer = inner + max(2, bar_height)
            
            x1 = cx + math.cos(angle_rad) * inner
            y1 = cy + math.sin(angle_rad) * inner
            x2 = cx + math.cos(angle_rad) * outer
            y2 = cy + math.sin(angle_rad) * outer
            
            self.canvas.create_line(x1, y1, x2, y2, fill=COLOR_CYAN, width=2)
        
        self.canvas.create_text(
            cx, cy,
            text="🎤",
            font=(FONT_FAMILY, 22),
        )
    
    def _draw_processing(self, cx, cy):
        for i in range(4):
            arc_r = 45 + i * 18
            angle = self.animation_angle * (2.2 + i * 0.6)
            extent = 90 - i * 12
            color = [COLOR_CYAN, COLOR_BLUE, COLOR_ACCENT, COLOR_CYAN_DIM][i]
            
            self.canvas.create_arc(
                cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                start=angle, extent=extent,
                outline=color,
                width=2.5,
                style="arc",
            )
            self.canvas.create_arc(
                cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                start=angle + 180, extent=extent,
                outline=color,
                width=2.5,
                style="arc",
            )
        
        num_dots = 6
        orbit_r = 40
        for i in range(num_dots):
            dot_angle = math.radians(self.animation_angle * 3.2 + i * (360 / num_dots))
            dx = cx + math.cos(dot_angle) * orbit_r
            dy = cy + math.sin(dot_angle) * orbit_r
            self.canvas.create_oval(dx - 3, dy - 3, dx + 3, dy + 3, fill=COLOR_CYAN, outline="")
        
        self.canvas.create_text(
            cx, cy,
            text="⚙",
            font=(FONT_FAMILY, 20),
            fill=COLOR_CYAN,
        )
    
    def _draw_speaking(self, cx, cy):
        for i in range(4):
            phase = (self.pulse_phase * 2.2 + i * 0.9) % (math.pi * 2)
            arc_r = 45 + i * 22 + math.sin(phase) * 8
            color = COLOR_CYAN if i % 2 == 0 else COLOR_BLUE
            
            try:
                self.canvas.create_arc(
                    cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                    start=-35 + math.sin(phase) * 10,
                    extent=70,
                    outline=color,
                    width=2,
                    style="arc",
                )
                self.canvas.create_arc(
                    cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                    start=145 + math.sin(phase) * 10,
                    extent=70,
                    outline=color,
                    width=2,
                    style="arc",
                )
            except Exception:
                pass
        
        pulse = math.sin(self.pulse_phase * 2.8) * 6
        r = 50 + pulse
        
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=COLOR_ACCENT, width=2.5)
        
        self.canvas.create_text(
            cx, cy,
            text="🔊",
            font=(FONT_FAMILY, 20),
        )
    
    # --------------------------------------------------------
    # CONTROLES E ESTADOS
    # --------------------------------------------------------
    
    def _toggle_voice(self):
        if self.is_listening:
            self.is_listening = False
            self.mic_button.configure(text="🎤  Ativar Voz", fg_color=COLOR_BLUE)
            self.set_state("idle")
            if self.stop_callback:
                self.stop_callback()
        else:
            self.is_listening = True
            self.mic_button.configure(text="⏹  Parar", fg_color=COLOR_ERROR)
            self.set_state("listening")
            if self.voice_callback:
                self.voice_callback()
    
    def set_state(self, new_state):
        self.state = new_state
        state_config = {
            "idle": {
                "label": "Aguardando comando...",
                "dot": COLOR_SUCCESS,
                "status": "● PRONTO",
                "status_color": COLOR_SUCCESS,
            },
            "listening": {
                "label": "🎤 Ouvindo...",
                "dot": COLOR_CYAN,
                "status": "● OUVINDO",
                "status_color": COLOR_CYAN,
            },
            "processing": {
                "label": "⚙ Processando comando...",
                "dot": COLOR_WARNING,
                "status": "● PROCESSANDO",
                "status_color": COLOR_WARNING,
            },
            "speaking": {
                "label": "🔊 Jarvis falando...",
                "dot": COLOR_ACCENT,
                "status": "● FALANDO",
                "status_color": COLOR_ACCENT,
            },
        }
        
        config = state_config.get(new_state, state_config["idle"])
        self.state_label.configure(text=config["label"])
        self.status_dot.configure(text_color=config["dot"])
        self.bottom_status.configure(text=config["status"], text_color=config["status_color"])
    
    def _log_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        
        tag_map = {
            "user": ("🗣️ Você", "user"),
            "jarvis": ("🤖 Jarvis", "jarvis"),
            "error": ("❌ Erro", "error"),
            "success": ("✅", "success"),
            "system": ("⚙️ Sistema", "system"),
        }
        prefix, tag = tag_map.get(sender, ("⚙️ Sistema", "system"))
        
        self.log_text._textbox.insert("end", f"[{timestamp}] ", "timestamp")
        self.log_text._textbox.insert("end", f"{prefix}: {message}\n", tag)
        self.log_text._textbox.see("end")
        self.log_text.configure(state="disabled")
    
    def log_user(self, msg): self._log_message("user", f'"{msg}"')
    def log_jarvis(self, msg): self._log_message("jarvis", msg)
    def log_system(self, msg): self._log_message("system", msg)
    def log_error(self, msg): self._log_message("error", msg)
    def log_success(self, msg): self._log_message("success", msg)
    
    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text._textbox.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._log_message("system", "Log reiniciado.")
    
    def queue_message(self, msg_type, data):
        self.message_queue.put((msg_type, data))
    
    def _check_message_queue(self):
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                if msg_type == "user_said":
                    self.log_user(data)
                elif msg_type == "jarvis_response":
                    self.log_jarvis(data)
                elif msg_type == "state_change":
                    self.set_state(data)
                elif msg_type == "error":
                    self.log_error(data)
                elif msg_type == "log_detail":
                    self.log_system(data)
                elif msg_type == "log_success":
                    self.log_success(data)
                elif msg_type == "voice_stopped":
                    self.is_listening = False
                    self.mic_button.configure(text="🎤  Ativar Voz", fg_color=COLOR_BLUE)
                    self.set_state("idle")
        except queue.Empty:
            pass
        
        self.root.after(80, self._check_message_queue)
    
    def _update_system_info(self):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory().percent
            info_parts = [f"CPU: {cpu}%", f"RAM: {ram}%"]
            
            try:
                battery = psutil.sensors_battery()
                if battery:
                    plugged_icon = "⚡" if battery.power_plugged else "🔋"
                    info_parts.append(f"{plugged_icon} Bateria: {battery.percent:.0f}%")
            except Exception:
                pass
            
            self.system_info_label.configure(text="   |   ".join(info_parts))
        except Exception:
            pass
        
        self.root.after(3000, self._update_system_info)
