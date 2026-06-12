import wave
import struct
import math
import tempfile
import os

def write_wav(path: str, samples, sample_rate: int = 44100) -> None:
    """Schreibt Float32-Samples als 16-bit PCM WAV."""
    with wave.open(path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for sample in samples:
            # Soft-Clipping
            saturated = math.tanh(sample * 1.5) / 1.5
            clamped = max(-1.0, min(1.0, saturated))
            int_sample = int(clamped * 32767)
            wav_file.writeframes(struct.pack('h', int_sample))

def create_temp_wav(samples, sample_rate: int = 44100) -> str:
    """Erzeugt eine temporäre WAV-Datei und gibt den Pfad zurück."""
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    write_wav(temp_path, samples, sample_rate)
    return temp_path
