import random
import math
from src.audio_profiles.base import BaseAudioProfile

class LiquidProfile(BaseAudioProfile):
    """Sound-Profil für flüssige/weiche Sounds (Lava Lamp)."""
    def __init__(self, seed):
        super().__init__(seed)
        # Tiefe, blubbernde Frequenzen
        self.base_freq = self.rng.uniform(60.0, 150.0)
        self.freq_var = self.rng.uniform(40.0, 100.0)
        self.body_decay = self.rng.uniform(4.0, 10.0)
        self.volume_scale = self.rng.uniform(0.7, 1.0)

    def get_params(self, impulse):
        # Weichere Zuordnung: Lava Lamp braucht Sounds bei niedrigeren Impulsen
        volume = min(0.8, max(0.05, impulse / 150.0)) * self.volume_scale
        t_imp = min(1.0, impulse / 200.0)
        
        # Tiefere Sounds bei größeren Impulsen (Verschmelzung)
        freq = self.base_freq + (1.0 - t_imp) * self.freq_var
        dur = 0.15 + t_imp * 0.25
        
        return {
            "volume": volume,
            "freq": freq,
            "duration": dur,
            "noise_level": 0.05, # Sehr wenig Noise für Flüssigkeiten
            "noise_dur_ms": 15.0,
            "pitch_drop": 0.2, # Starker Pitch-Drop für "Bloop"-Effekt
            "body_decay": self.body_decay,
            "inharmonicity": self.inharmonicity
        }
