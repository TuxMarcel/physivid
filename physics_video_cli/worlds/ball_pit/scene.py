import pymunk
import math
import random
from core.experiment import Experiment
from core.registry import register
from worlds.ball_pit.components import (
    try_add_wall, try_add_peg, try_add_spinner, spawn_ball, recycle_balls
)
from audio.profiles.impact_profile import ImpactProfile
from utils.colors import get_palette

def _build_classic_plinko(scene):
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y, bot_y = H * 0.95, -H * 0.95
    segs = [((-W, bot_y * 0.6), (-W, top_y)), ((W, bot_y * 0.6), (W, top_y)),
            ((-W, bot_y * 0.6), (-hw, bot_y)), ((W, bot_y * 0.6), (hw, bot_y)),
            ((-W, top_y), (-hw * 1.6, top_y)), ((W, top_y), (hw * 1.6, top_y))]
    for a, b in segs: try_add_wall(scene, a, b, (58, 70, 88))
    xs = [scene.rng.uniform(-W * 0.4, -W * 0.1), scene.rng.uniform(W * 0.1, W * 0.4)]
    if scene.rng.random() > 0.5: xs.append(0)
    for i, sx in enumerate(xs):
        try_add_spinner(scene, sx, scene.rng.uniform(-H * 0.45, -H * 0.05),
                        scene.rng.randint(90, 140), scene.rng.randint(2, 4),
                        scene.rng.uniform(1.0, 2.5) * (1 if i % 2 == 0 else -1))
    rows = scene.rng.randint(5, 9)
    y_top, y_bot = H * 0.75, -H * 0.35
    for r in range(rows):
        y = y_top - r * ((y_top - y_bot) / max(rows - 1, 1))
        pegs, spacing = (6 if r % 2 == 0 else 5), (W * 1.6 / (7 if r % 2 == 0 else 6))
        for i in range(pegs):
            try_add_peg(scene, -W * 0.8 + spacing * (i + 1), y, scene.rng.randint(10, 16))
    scene.spawn_points = [{"x_range": (-hw * 1.3, hw * 1.3), "y": top_y - 25, "vx": (-60, 60), "vy": (-200, -120)}]

def _build_arena(scene):
    aw, ah, hw = scene.W * 0.88, scene.H * 0.85, scene.hole_w
    mw, top_y, bot_y, entry_hw = aw * 0.55, ah, -ah, scene.hole_w * 1.8
    segs = [((-aw, -ah * 0.45), (-aw, ah * 0.45)), ((-aw, ah * 0.45), (-mw, top_y)), ((-aw, -ah * 0.45), (-mw, bot_y)),
            ((aw, -ah * 0.45), (aw, ah * 0.45)), ((aw, ah * 0.45), (mw, top_y)), ((aw, -ah * 0.45), (mw, bot_y)),
            ((-mw, top_y), (-entry_hw, top_y)), ((mw, top_y), (entry_hw, top_y)),
            ((-mw, bot_y), (-hw, bot_y - scene.H * 0.08)), ((mw, bot_y), (hw, bot_y - scene.H * 0.08))]
    for a, b in segs: try_add_wall(scene, a, b, (55, 68, 88))
    for i in range(3):
        angle, dist = i * 2 * math.pi / 3 + scene.rng.uniform(-0.3, 0.3), scene.rng.uniform(aw * 0.15, aw * 0.4)
        try_add_spinner(scene, math.cos(angle) * dist, math.sin(angle) * dist * 0.6,
                        scene.rng.randint(80, 120), 2, scene.rng.uniform(1.2, 2.8) * (1 if i % 2 == 0 else -1))
    scene.spawn_points = [{"x_range": (-entry_hw * 0.9, entry_hw * 0.9), "y": top_y - 25, "vx": (-50, 50), "vy": (-200, -100)}]

LAYOUTS = [_build_classic_plinko, _build_arena]

class BallPitExperiment(Experiment):
    name, description = "ball_pit", "Bälle-Parcours (Plinko) - Dynamisches Hindernislayout"
    def setup(self) -> None:
        self.space.gravity = (0, -900)
        self.rng = random.Random(self.seed)
        self.palette = get_palette(self.rng)
        self.audio_profile = ImpactProfile(self.seed)
        self.spinners, self.walls, self.pegs_registry, self.spinners_registry = [], [], [], []
        self.W, self.H, self.hole_w = 520, 920, self.rng.randint(85, 155)
        LAYOUTS[self.rng.randint(0, len(LAYOUTS) - 1)](self)
        for _ in range(self.rng.randint(8, 14)): spawn_ball(self)
    def get_duration(self) -> float: return 60.0
    def post_step(self, dt: float) -> None:
        super().post_step(dt)
        recycle_balls(self)
        if len([e for e in self.entities if hasattr(e, "body") and e.body.body_type == pymunk.Body.DYNAMIC]) < 30:
            if getattr(self, "_step", 0) % 40 == 0: spawn_ball(self)
        self._step = getattr(self, "_step", 0) + 1
    def get_impulse_threshold(self) -> float: return 12.0

register("ball_pit", BallPitExperiment)
