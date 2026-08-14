"""
PyAudio Compatibility Module for Python 3.14 on Windows.

Provides standard PyAudio API (PyAudio, Stream, paInt16, paFloat32, etc.)
backed by sounddevice for native, compiler-free execution with SpeechRecognition.
"""

import sounddevice as sd
import numpy as np

# Format constants
paFloat32 = 1
paInt32 = 2
paInt24 = 4
paInt16 = 8
paInt8 = 16
paUInt8 = 32
paCustomFormat = 65536

class Stream:
    def __init__(self, parent, rate=16000, channels=1, format=paInt16, input=True, frames_per_buffer=1024, input_device_index=None):
        self.parent = parent
        self.rate = rate
        self.channels = channels
        self.format = format
        self.frames_per_buffer = frames_per_buffer
        self.input_device_index = input_device_index
        self.is_active = True
        
        dtype = 'int16' if format == paInt16 else 'float32'
        self.stream = sd.InputStream(
            samplerate=rate,
            channels=channels,
            dtype=dtype,
            blocksize=frames_per_buffer,
            device=input_device_index
        )
        self.stream.start()

    def read(self, num_frames, exception_on_overflow=False):
        data, overflowed = self.stream.read(num_frames)
        return bytes(data)

    def stop_stream(self):
        if self.stream.active:
            self.stream.stop()
        self.is_active = False

    def close(self):
        if hasattr(self, 'stream') and self.stream:
            self.stream.close()
        self.is_active = False

    def is_stopped(self):
        return not self.is_active


def get_sample_size(format):
    if format == paInt16:
        return 2
    elif format in (paInt32, paFloat32):
        return 4
    elif format == paInt24:
        return 3
    elif format in (paInt8, paUInt8):
        return 1
    return 2


class PyAudio:
    paFloat32 = paFloat32
    paInt32 = paInt32
    paInt24 = paInt24
    paInt16 = paInt16
    paInt8 = paInt8
    paUInt8 = paUInt8

    def __init__(self):
        self._streams = []

    def get_sample_size(self, format):
        return get_sample_size(format)

    def get_default_input_device_info(self):
        try:
            device_info = sd.query_devices(kind='input')
            return {
                'index': device_info.get('index', 0),
                'name': device_info.get('name', 'Default Microphone'),
                'defaultSampleRate': device_info.get('default_samplerate', 16000),
                'maxInputChannels': device_info.get('max_input_channels', 2),
            }
        except Exception:
            return {
                'index': 0,
                'name': 'Default Microphone',
                'defaultSampleRate': 16000,
                'maxInputChannels': 1,
            }

    def get_device_count(self):
        try:
            return len(sd.query_devices())
        except Exception:
            return 1

    def get_device_info_by_index(self, index):
        try:
            info = sd.query_devices(index)
            return {
                'index': index,
                'name': info.get('name', f'Device {index}'),
                'defaultSampleRate': info.get('default_samplerate', 16000),
                'maxInputChannels': info.get('max_input_channels', 2),
                'maxOutputChannels': info.get('max_output_channels', 2),
            }
        except Exception:
            return {
                'index': index,
                'name': f'Device {index}',
                'defaultSampleRate': 16000,
                'maxInputChannels': 1,
                'maxOutputChannels': 0,
            }

    def open(self, *args, **kwargs):
        stream = Stream(self, **kwargs)
        self._streams.append(stream)
        return stream

    def terminate(self):
        for stream in self._streams:
            try:
                stream.close()
            except Exception:
                pass
        self._streams.clear()


def get_format_from_width(width, unsigned=False):
    if width == 1:
        return paUInt8 if unsigned else paInt8
    elif width == 2:
        return paInt16
    elif width == 3:
        return paInt24
    elif width == 4:
        return paInt32
    else:
        return paCustomFormat
