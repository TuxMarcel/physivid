import math
import random
from audio.profiles.impact_profile import ImpactProfile

class Synthesizer:
    def __init__(self, sample_rate: int = 44100, seed: int = 0, duration: float = 60.0):
        self.sample_rate = sample_rate
        self.seed = seed
        self.total_samples = int(duration * sample_rate)
        self.buffer = [0.0] * self.total_samples
        self._noise_rng = random.Random(seed ^ 0x904312)
        self.default_profile = ImpactProfile(seed)
        
        # Pentatonische Frequenzen (A-Moll Pentatonik: A3 bis A5)
        self.pentatonic_scale = [
            220.0, 261.63, 293.66, 329.63, 392.0,
            440.0, 523.25, 587.33, 659.25, 783.99,
            880.0
        ]

    def _snap_to_pentatonic(self, freq: float) -> float:
        """Rundet eine Frequenz auf den nächsten pentatonischen Ton für wohlklingende Harmonien."""
        return min(self.pentatonic_scale, key=lambda f: abs(f - freq))

    def play_sound(self, t: float, params: dict) -> None:
        """Synthetisiert einen Sound basierend auf den übergebenen Parametern."""
        start_sample = int(t * self.sample_rate)
        num_samples = int(self.sample_rate * params["duration"])
        noise_samples = int(self.sample_rate * params["noise_dur_ms"] / 1000.0)
        
        phase = 0.0
        dt = 1.0 / self.sample_rate

        # Snap to pentatonic for harmonic correctness
        freq = self._snap_to_pentatonic(params["freq"])

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
            current_freq = freq * (1.0 - params["pitch_drop"] * t_norm)
            phase += 2.0 * math.pi * current_freq * dt

            body_env = math.exp(-params["body_decay"] * t_norm)
            body = math.sin(phase) * body_env
            # Inharmonischer Oberton
            body += 0.18 * math.sin(phase * params.get("inharmonicity", 1.01) * 2.0) * body_env * 0.5

            body_level = 1.0 - params["noise_level"] * 0.5
            sample_val = (click + body * body_level) * params["volume"]

            self.buffer[idx] += sample_val

    def play_collision_sound(self, t: float, impulse: float) -> None:
        """Legacy-Kompatibilität für Tests."""
        params = self.default_profile.get_params(impulse)
        self.play_sound(t, params)

    def add_pad_layer(self, duration: float) -> None:
        """Fügt einen dezenten, tieferen Ambient-Grundton hinzu (Pad Layer)."""
        dt = 1.0 / self.sample_rate
        freq = self.pentatonic_scale[self.seed % 5] * 0.5  # Oktavierung nach unten
        
        for i in range(self.total_samples):
            # Sanftes Anwachsen und Abfallen des Pad-Volumens
            t = i * dt
            envelope = 0.05 * math.sin(math.pi * t / duration)
            self.buffer[i] += math.sin(2.0 * math.pi * freq * t) * envelope
