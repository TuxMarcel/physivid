import pymunk
import random
from src.scenes.scene_ball_pit import BallPitScene
from src.scenes.scene_lava_lamp import LavaLampScene

class WorldGenerator:
    def __init__(self, seed, profile):
        self.seed = seed
        self.profile = profile
        self.rng = random.Random(seed)
        self.space = pymunk.Space()

        self.palettes = [
            [(255, 0, 128), (0, 240, 255), (255, 230, 0), (140, 0, 255)],
            [(255, 100, 0), (220, 20, 60), (255, 215, 0), (46, 139, 87)],
            [(0, 128, 128), (0, 206, 209), (30, 144, 255), (102, 205, 170)],
            [(255, 20, 147), (255, 69, 0), (138, 43, 226), (0, 0, 255)],
            [(178, 34, 34), (255, 127, 80), (218, 165, 32), (75, 0, 130)],
        ]
        self.palette = self.palettes[self.seed % len(self.palettes)]

        self.scenes_registry = {
            "ball_pit": BallPitScene,
            "lava_lamp": LavaLampScene,
        }

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
        if self.scene is not None:
            self.scene.update(frame, dt)
