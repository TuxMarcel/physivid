import pymunk
import math
import random
from core.experiment import Experiment
from core.registry import register
from entities.shapes import CircleEntity
from audio.profiles.impact_profile import ImpactProfile
from utils.colors import get_palette

class DNAHelixExperiment(Experiment):
    name, description = "dna_helix", "DNA-Helix - Rotierende Helix mit herabfallenden Bällen"
    def setup(self) -> None:
        self.space.gravity = (0, -600)
        self.rng = random.Random(self.seed)
        self.palette = get_palette(self.rng)
        self.audio_profile = ImpactProfile(self.seed)
        self.helix_radius, self.rotation_speed = self.rng.uniform(150, 250), self.rng.uniform(0.5, 1.5)
        self.num_base_pairs = self.rng.randint(20, 35)
        self.vertical_spacing, self.twist_factor = 1600 / self.num_base_pairs, self.rng.uniform(0.005, 0.015)
        self.helix_bodies = []
        for i in range(self.num_base_pairs):
            y, angle = -800 + i * self.vertical_spacing, i * self.twist_factor * 100
            self.helix_bodies.append((self._add_node(angle, y, self.palette[0]), self._add_node(angle + math.pi, y, self.palette[1]), angle, y))
    def _add_node(self, angle, y, color):
        node = CircleEntity(math.cos(angle) * self.helix_radius, y, 25, is_static=True, color=color)
        node.body.body_type = pymunk.Body.KINEMATIC
        node.shape.elasticity, node.shape.friction = 0.8, 0.5
        node.add_to_space(self.space)
        return node.body
    def get_duration(self) -> float: return 60.0
    def pre_step(self, dt: float) -> None:
        self._frame = getattr(self, "_frame", 0) + 1
        rot = self._frame * dt * self.rotation_speed
        for b1, b2, base_angle, y in self.helix_bodies:
            b1.position = (math.cos(base_angle + rot) * self.helix_radius, y)
            b2.position = (math.cos(base_angle + math.pi + rot) * self.helix_radius, y)
        if self._frame % 40 == 0: self._spawn_ball()
    def post_step(self, dt: float) -> None:
        super().post_step(dt)
        for e in list(self.entities):
            if hasattr(e, "body") and e.body.position.y < -1000:
                e.remove_from_space(self.space); self.entities.remove(e)
    def _spawn_ball(self):
        ball = CircleEntity(self.rng.uniform(-100, 100), 900, 15, color=self.rng.choice(self.palette), trail=True, trail_len=12)
        ball.body.velocity = (self.rng.uniform(-50, 50), -100)
        ball.shape.elasticity, ball.shape.friction = 0.7, 0.3
        ball.add_to_space(self.space); self.entities.append(ball)

register("dna_helix", DNAHelixExperiment)
