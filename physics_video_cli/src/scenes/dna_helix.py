import pymunk
import random
import math
from src.scenes.base import BaseScene
from src.audio_profiles.impact_profile import ImpactProfile

class DNAHelixScene(BaseScene):
    def __init__(self, space, rng, palette, seed):
        super().__init__(space, rng, palette)
        self.audio_profile = ImpactProfile(seed) # DNA nutzt auch Impacts für die Balls

    def setup(self):
        self.space.gravity = (0, -600)
        # DNA Struktur Setup...
        pass

    def update(self, frame, dt):
        # Helix Rotation & Ball Spawning...
        pass
