import pymunk
import math
import random
from core.experiment import Experiment
from core.registry import register
from entities.lava_blob import LavaBlob, get_blobs, merge_blobs, split_blob
from audio.profiles.liquid_profile import LiquidProfile
from utils.colors import get_palette

def _build_classic_vessel(scene):
    thick = 16
    neck_w, bot_w, top_w = scene.rng.randint(50, 80), scene.rng.randint(280, 340), scene.rng.randint(250, 310)
    bot_y, bot_curve, neck_bot, neck_top, top_curve, top_y = -820, -480, -180, 220, 500, 820
    pts = [(-bot_w, bot_y), (-bot_w, bot_curve), (-neck_w, neck_bot), (-neck_w, neck_top),
           (-top_w, top_curve), (-top_w, top_y), (top_w, top_y), (top_w, top_curve),
           (neck_w, neck_top), (neck_w, neck_bot), (bot_w, bot_curve), (bot_w, bot_y)]
    return pts, thick

def _build_flask_vessel(scene):
    thick = 16
    bot_w, neck_w = scene.rng.randint(350, 450), scene.rng.randint(60, 100)
    bot_y, shoulder_y, top_y = -850, -300, 850
    pts = [(-bot_w, bot_y), (-bot_w, shoulder_y), (-neck_w, shoulder_y + 100), (-neck_w, top_y),
           (neck_w, top_y), (neck_w, shoulder_y + 100), (bot_w, shoulder_y), (bot_w, bot_y)]
    return pts, thick

LAVA_LAYOUTS = [_build_classic_vessel, _build_flask_vessel]

class LavaLampExperiment(Experiment):
    name, description = "lava_lamp", "Lava-Lampe - Sanft auf- und absteigende Blobs"
    def setup(self) -> None:
        self.rng = random.Random(self.seed)
        self.palette = get_palette(self.rng)
        self.audio_profile = LiquidProfile(self.seed)
        self.space.gravity = (0, self.rng.randint(-220, -140))
        pts, thick = LAVA_LAYOUTS[self.rng.randint(0, len(LAVA_LAYOUTS) - 1)](self)
        self._build_vessel_from_pts(pts, thick)
        for _ in range(self.rng.randint(12, 22)):
            blob = LavaBlob(self.rng)
            blob.add_to_space(self.space)
            self.entities.append(blob)
    def _build_vessel_from_pts(self, pts, thick):
        for i in range(len(pts)):
            seg = pymunk.Segment(self.space.static_body, pts[i], pts[(i + 1) % len(pts)], thick)
            seg.elasticity, seg.friction, seg.color, seg.is_dynamic = 0.1, 0.05, (30, 35, 50), False
            self.space.add(seg)
    def get_duration(self) -> float: return 60.0
    def post_step(self, dt: float) -> None:
        super().post_step(dt)
        if getattr(self, "_step", 0) % 3 != 0: 
            self._step = getattr(self, "_step", 0) + 1
            return
        blobs = [e for e in self.entities if isinstance(e, LavaBlob)]
        merged = set()
        for i, b1 in enumerate(blobs):
            if b1 in merged or b1.body not in self.space.bodies: continue
            for j in range(i + 1, len(blobs)):
                b2 = blobs[j]
                if b2 in merged or b2.body not in self.space.bodies: continue
                if b1.body.position.get_distance(b2.body.position) < (b1.radius + b2.radius) * 0.85:
                    new_blob = merge_blobs(self.space, b1.body, b2.body)
                    self.entities.remove(b1); self.entities.remove(b2)
                    self.entities.append(new_blob); merged.add(b2); break
        for e in list(self.entities):
            if isinstance(e, LavaBlob) and e.radius > self.rng.randint(55, 75):
                new_blobs = split_blob(self.space, self.rng, e.body)
                self.entities.remove(e); self.entities.extend(new_blobs)
        if len([e for e in self.entities if isinstance(e, LavaBlob)]) < 8 and getattr(self, "_step", 0) % 60 == 0:
            nb = LavaBlob(self.rng); nb.add_to_space(self.space); self.entities.append(nb)
        self._step = getattr(self, "_step", 0) + 1

register("lava_lamp", LavaLampExperiment)
