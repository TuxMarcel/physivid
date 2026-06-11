import random

class BaseAudioProfile:
    """Basisklasse für alle Sound-Profile."""
    def __init__(self, seed):
        self.rng = random.Random(seed ^ 0xAC0057C)
        self.inharmonicity = self.rng.uniform(1.003, 1.025)

    def get_params(self, impulse):
        """Gibt die Synthese-Parameter basierend auf dem Impuls zurück."""
        raise NotImplementedError("Subclasses must implement get_params")
