import pymunk
import random
from src.scenes.ball_pit import BallPitScene
from src.scenes.lava_dna import LavaDNAScene

class WorldGenerator:
    def __init__(self, seed, profile):
        self.seed = seed
        self.profile = profile
        self.rng = random.Random(seed)
        self.space = pymunk.Space()
        
        # Predefined color palettes
        self.palettes = [
            [(255, 0, 128), (0, 240, 255), (255, 230, 0), (140, 0, 255)], # Neon Lights
            [(255, 100, 0), (220, 20, 60), (255, 215, 0), (46, 139, 87)], # Autumn Forest
            [(0, 128, 128), (0, 206, 209), (30, 144, 255), (102, 205, 170)], # Ocean Breeze
            [(255, 20, 147), (255, 69, 0), (138, 43, 226), (0, 0, 255)], # Retro Future
            [(178, 34, 34), (255, 127, 80), (218, 165, 32), (75, 0, 130)] # Sunset Glow
        ]
        self.palette = self.palettes[self.seed % len(self.palettes)]
        
        # Central Registry of available scenes
        self.scenes_registry = {
            "ball_pit": BallPitScene,
            "lava_dna": LavaDNAScene
        }
        
        # World physics properties based on profile
        if self.profile == "ball_pit":
            self.space.gravity = (0, -900)
        else:
            self.space.gravity = (0, 0)
            
        self.scene = None

    def generate(self):
        scene_class = self.scenes_registry.get(self.profile)
        if scene_class is None:
            raise ValueError(f"Unknown scene profile: {self.profile}")
        
        self.scene = scene_class(self.space, self.rng, self.palette)
        self.scene.setup()
        return self.space

    def update(self, frame, dt):
        """
        Forwards frame-by-frame updates (like spawning new items) to the active scene class.
        """
        if self.scene is not None:
            self.scene.update(frame, dt)
