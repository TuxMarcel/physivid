import random
from audio.profiles.base import BaseAudioProfile

class ImpactProfile(BaseAudioProfile):
    """Sound-Profil für harte Aufpralle (Ball Pit)."""
    def __init__(self, seed):
        super().__init__(seed)
        # Ping-Pong-Bälle: Fokus auf kurze, helle, klare Klicks
        self.material = 0 # Nur Plastik/Ping-Pong für dieses Profil
        
        self.body_freq_min   = self.rng.uniform(2500.0, 3500.0)
        self.body_freq_max   = self.rng.uniform(3500.0, 5000.0)
        self.body_decay      = self.rng.uniform(25.0,  40.0) # Schnelleres Ausklingen
        self.noise_level     = self.rng.uniform(0.02,  0.08) # Viel weniger Noise
        self.noise_dur_ms    = self.rng.uniform(1.0,   3.0)  # Kürzerer Transienten-Click
        self.dur_min         = 0.005
        self.dur_max         = self.rng.uniform(0.01,  0.03) # Sehr kurz
        self.pitch_drop      = self.rng.uniform(0.01,  0.05)
        self.volume_scale    = self.rng.uniform(0.4,   0.8)

    def get_params(self, impulse):
        # Leisere Sounds bei schwachen Impulsen
        volume = min(1.0, max(0.05, impulse / 400.0)) * self.volume_scale
        t_imp = min(1.0, impulse / 800.0)
        
        # Frequenz korreliert mit Kraft
        freq = self.body_freq_min + t_imp * (self.body_freq_max - self.body_freq_min)
        dur = self.dur_min + t_imp * (self.dur_max - self.dur_min)
        
        return {
            "volume": volume,
            "freq": freq,
            "duration": dur,
            "noise_level": 0.005, # Extrem minimiert für sauberen Klang
            "noise_dur_ms": 1.0,  # Noch kürzer
            "pitch_drop": self.pitch_drop,
            "body_decay": self.body_decay,
            "inharmonicity": 1.000 # Keine Inharmonizität
        }
