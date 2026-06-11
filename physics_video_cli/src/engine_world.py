import pymunk
import random
from src.scenes.ball_pit import BallPitScene
from src.scenes.lava_lamp import LavaLampScene
from src.scenes.dna_helix import DNAHelixScene

class WorldGenerator:
    """Eine dynamische Factory zum Erstellen von Szenen."""
    def __init__(self, seed, profile):
        self.seed = seed
        self.profile = profile
        self.rng = random.Random(seed)
        
        # Paletten-Auswahl (generisch für alle Szenen)
        self.palettes = [
            [(255, 0, 128), (0, 240, 255), (255, 230, 0), (140, 0, 255)],
            [(255, 100, 0), (220, 20, 60), (255, 215, 0), (46, 139, 87)],
            [(0, 128, 128), (0, 206, 209), (30, 144, 255), (102, 205, 170)],
        ]
        self.palette = self.palettes[self.seed % len(self.palettes)]

        # Dynamisches Mapping
        self.scenes_registry = {
            "ball_pit": BallPitScene,
            "lava_lamp": LavaLampScene,
            "dna_helix": DNAHelixScene,
        }

    def generate(self):
        """Erzeugt die angeforderte Szene."""
        scene_class = self.scenes_registry.get(self.profile)
        if not scene_class:
            raise ValueError(f"Unbekannte Szene: {self.profile}")

        space = pymunk.Space()
        # Die Szene entscheidet selbst über ihre Gravity (wird in scene.setup() gesetzt)
        scene = scene_class(space, self.rng, self.palette, self.seed)
        scene.setup()
        return scene
