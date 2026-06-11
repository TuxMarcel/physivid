import pymunk
import random
import math
from src.scenes.base import BaseScene
from src.entities.lava_entities import LavaBlob
from src.audio_profiles.liquid_profile import LiquidProfile

class LavaLampScene(BaseScene):
    def __init__(self, space, rng, palette, seed):
        super().__init__(space, rng, palette)
        self.audio_profile = LiquidProfile(seed)
        self.blobs = []

    def setup(self):
        # Szene setzt ihre eigene Gravity (Lava Lamp braucht weniger Gravity)
        self.space.gravity = (0, -180)
        self._build_vessel()
        
        for _ in range(15):
            self._spawn_blob()

    def _build_vessel(self):
        thick = 16
        pts = [
            (-300, -800), (-300, -400),
            (-80, -100), (-80, 200),
            (-280, 500), (-280, 800),
            (280, 800), (280, 500),
            (80, 200), (80, -100),
            (300, -400), (300, -800),
        ]
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            seg = pymunk.Segment(self.space.static_body, a, b, thick)
            seg.elasticity = 0.1
            seg.friction = 0.05
            seg.color = (30, 35, 50)
            self.space.add(seg)

    def _spawn_blob(self, position=None, radius=None, temp=None):
        blob = LavaBlob(self.space, self.rng, position, radius, temp)
        self.blobs.append(blob)

    def update(self, frame, dt):
        if frame % 5 != 0: return

        # Verschmelzungs-Logik
        merged = set()
        for i, b1 in enumerate(self.blobs):
            if b1 in merged: continue
            for j in range(i + 1, len(self.blobs)):
                b2 = self.blobs[j]
                if b2 in merged: continue
                
                dist = b1.body.position.get_distance(b2.body.position)
                if dist < (b1.radius + b2.radius) * 0.85:
                    # Merge Logic (vereinfacht für Prototyp)
                    new_radius = math.sqrt(b1.radius**2 + b2.radius**2)
                    new_pos = (b1.body.position + b2.body.position) / 2
                    new_temp = (b1.body.temp + b2.body.temp) / 2
                    
                    b1.remove()
                    b2.remove()
                    merged.add(b1)
                    merged.add(b2)
                    
                    self._spawn_blob(new_pos, new_radius, new_temp)
                    break
        
        # Split Logic (wenn zu groß)
        for b in list(self.blobs):
            if b not in merged and b.radius > 70:
                # Split...
                pass

        # Aufräumen der Liste
        self.blobs = [b for b in self.blobs if b not in merged]

    def get_impulse_threshold(self):
        return 5.0 # Sensiblere Sounds für Flüssigkeiten
