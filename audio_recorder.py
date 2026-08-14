"""
J.A.R.V.I.S. — Módulo de Gravação de Áudio via SoundDevice

Captura áudio do microfone em tempo real usando sounddevice e numpy,
detectando início de fala e pausas de silêncio para conversão direta
em speech_recognition.AudioData sem necessidade de PyAudio ou C++ Build Tools.
"""

import time
import numpy as np
import sounddevice as sd
import speech_recognition as sr


class SoundDeviceMicrophone:
    """Captura de áudio do microfone com detecção inteligente de fala e silêncio."""

    def __init__(self, sample_rate=16000, block_duration=0.05):
        self.sample_rate = sample_rate
        self.block_duration = block_duration
        self.block_size = int(sample_rate * block_duration)
        self.energy_threshold = 400
        self.dynamic_energy_threshold = True

    def adjust_for_ambient_noise(self, duration=1.0):
        """Mede o ruído ambiente para calibrar o limiar de fala."""
        energies = []
        num_blocks = int(duration / self.block_duration)
        
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
            for _ in range(num_blocks):
                data, _ = stream.read(self.block_size)
                # Calcula RMS
                data_np = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                rms = np.sqrt(np.mean(data_np ** 2)) if len(data_np) > 0 else 0
                energies.append(rms)
        
        if energies:
            avg_energy = float(np.mean(energies))
            self.energy_threshold = max(250.0, avg_energy * 1.6)
        return self.energy_threshold

    def listen_phrase(self, timeout=8.0, phrase_time_limit=12.0, silence_limit=1.2, stop_event=None, on_audio_level=None):
        """
        Escuta o microfone até detectar uma frase completa com silêncio no final.
        
        Args:
            timeout: Tempo máximo esperando início da fala (segundos)
            phrase_time_limit: Duração máxima da fala gravada (segundos)
            silence_limit: Duração de silêncio após a fala para considerar final da frase (segundos)
            stop_event: threading.Event para cancelar escuta
            on_audio_level: callback(level: float) para visualizador de áudio
            
        Returns:
            sr.AudioData ou None se timeout/cancelado
        """
        recorded_frames = []
        speaking = False
        silence_start_time = None
        listen_start_time = time.time()
        speech_start_time = None

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16') as stream:
            while True:
                if stop_event and stop_event.is_set():
                    return None

                data, _ = stream.read(self.block_size)
                raw_bytes = bytes(data)
                
                # Calcular intensidade (RMS)
                data_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
                rms = np.sqrt(np.mean(data_np ** 2)) if len(data_np) > 0 else 0.0

                if on_audio_level:
                    # Normalizar nível de 0.0 a 1.0 para UI
                    normalized_level = min(1.0, rms / (self.energy_threshold * 3 + 1e-5))
                    on_audio_level(normalized_level)

                now = time.time()

                if not speaking:
                    # Verifica se o usuário começou a falar
                    if rms > self.energy_threshold:
                        speaking = True
                        speech_start_time = now
                        recorded_frames.append(raw_bytes)
                    else:
                        # Verifica timeout sem início de fala
                        if (now - listen_start_time) > timeout:
                            return None
                else:
                    recorded_frames.append(raw_bytes)

                    # Verifica limite de tempo total de frase
                    if (now - speech_start_time) > phrase_time_limit:
                        break

                    # Verifica silêncio após fala
                    if rms < (self.energy_threshold * 0.75):
                        if silence_start_time is None:
                            silence_start_time = now
                        elif (now - silence_start_time) >= silence_limit:
                            # Silêncio suficiente detectado: fim do comando
                            break
                    else:
                        silence_start_time = None

        if recorded_frames:
            all_bytes = b"".join(recorded_frames)
            # sample_width = 2 (16 bits)
            return sr.AudioData(all_bytes, self.sample_rate, 2)

        return None
