import wave
import struct
import math
import random

class AudioEngine:
    """Generische Audio-Engine für die WAV-Synthese."""
    def __init__(self, output_path, duration, sample_rate=44100):
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.total_samples = int(duration * sample_rate)
        self.buffer = [0.0] * self.total_samples
        self._noise_rng = random.Random(42) # Fester Seed für deterministisches Noise

    def play_sound(self, t, params):
        """Synthetisiert einen Sound basierend auf den übergebenen Parametern."""
        start_sample = int(t * self.sample_rate)
        num_samples = int(self.sample_rate * params["duration"])
        noise_samples = int(self.sample_rate * params["noise_dur_ms"] / 1000.0)
        
        phase = 0.0
        dt = 1.0 / self.sample_rate

        for i in range(num_samples):
            idx = start_sample + i
            if idx >= self.total_samples:
                break

            t_norm = i / max(num_samples - 1, 1)

            # Click/Noise Transient
            click = 0.0
            if i < noise_samples:
                noise_env = math.exp(-6.0 * i / max(noise_samples, 1))
                click = self._noise_rng.uniform(-1.0, 1.0) * noise_env * params["noise_level"]

            # Resonant Body
            current_freq = params["freq"] * (1.0 - params["pitch_drop"] * t_norm)
            phase += 2.0 * math.pi * current_freq * dt

            body_env = math.exp(-params["body_decay"] * t_norm)
            body = math.sin(phase) * body_env
            # Inharmonischer Oberton
            body += 0.18 * math.sin(phase * params["inharmonicity"] * 2.0) * body_env * 0.5

            body_level = 1.0 - params["noise_level"] * 0.5
            sample_val = (click + body * body_level) * params["volume"]

            self.buffer[idx] += sample_val

    def write_to_file(self):
        """Schreibt den Audio-Buffer in eine WAV-Datei."""
        with wave.open(self.output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)

            for sample in self.buffer:
                # Soft-Clipping
                saturated = math.tanh(sample * 1.5) / 1.5
                clamped = max(-1.0, min(1.0, saturated))
                int_sample = int(clamped * 32767)
                wav_file.writeframes(struct.pack('h', int_sample))
