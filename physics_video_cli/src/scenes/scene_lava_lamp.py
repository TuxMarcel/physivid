import pymunk
import math
from src.scenes.scene_base import BaseScene
from src.entities.lava_blob import create_blob, get_blobs, merge_blobs, split_blob


def _build_classic_vessel(scene):
    """The standard tall lava lamp shape."""
    thick = 16
    neck_w = scene.rng.randint(50, 80)
    bot_w = scene.rng.randint(280, 340)
    top_w = scene.rng.randint(250, 310)
    
    bot_y = -820
    bot_curve = -480
    neck_bot = -180
    neck_top = 220
    top_curve = 500
    top_y = 820

    pts = [
        (-bot_w, bot_y), (-bot_w, bot_curve),
        (-neck_w, neck_bot), (-neck_w, neck_top),
        (-top_w, top_curve), (-top_w, top_y),
        (top_w, top_y), (top_w, top_curve),
        (neck_w, neck_top), (neck_w, neck_bot),
        (bot_w, bot_curve), (bot_w, bot_y),
    ]
    return pts, thick


def _build_flask_vessel(scene):
    """A wide-bottomed laboratory flask shape."""
    thick = 16
    bot_w = scene.rng.randint(350, 450)
    neck_w = scene.rng.randint(60, 100)
    
    bot_y = -850
    shoulder_y = -300
    top_y = 850
    
    pts = [
        (-bot_w, bot_y), (-bot_w, shoulder_y),
        (-neck_w, shoulder_y + 100), (-neck_w, top_y),
        (neck_w, top_y), (neck_w, shoulder_y + 100),
        (bot_w, shoulder_y), (bot_w, bot_y),
    ]
    return pts, thick


def _build_hourglass_vessel(scene):
    """An hourglass shape with a narrow waist."""
    thick = 16
    end_w = scene.rng.randint(300, 400)
    waist_w = scene.rng.randint(40, 70)
    
    top_y = 820
    bot_y = -820
    
    pts = [
        (-end_w, bot_y), (-end_w, -500),
        (-waist_w, 0), (-end_w, 500),
        (-end_w, top_y), (end_w, top_y),
        (end_w, 500), (waist_w, 0),
        (end_w, -500), (end_w, bot_y),
    ]
    return pts, thick


LAVA_LAYOUTS = [
    _build_classic_vessel,
    _build_flask_vessel,
    _build_hourglass_vessel,
]


class LavaLampScene(BaseScene):
    def setup(self):
        # Seed-driven gravity
        grav_y = self.rng.randint(-220, -140)
        self.space.gravity = (0, grav_y)
        
        # Pick a vessel layout based on seed
        layout_fn = LAVA_LAYOUTS[self.rng.randint(0, len(LAVA_LAYOUTS) - 1)]
        pts, thick = layout_fn(self)
        
        self._build_vessel_from_pts(pts, thick)
        self._build_deflectors()

        # Seed-driven blob count
        num_blobs = self.rng.randint(12, 22)
        for _ in range(num_blobs):
            create_blob(self.space, self.rng)

    def _build_vessel_from_pts(self, pts, thick):
        for i in range(len(pts)):
            a = pts[i]
            b = pts[(i + 1) % len(pts)]
            seg = pymunk.Segment(self.space.static_body, a, b, thick)
            seg.elasticity = 0.1
            seg.friction = 0.05
            seg.color = (30, 35, 50)
            seg.is_dynamic = False
            self.space.add(seg)

    def _build_deflectors(self):
        # Randomize deflector positions slightly
        dy1 = self.rng.randint(380, 460)
        dy2 = self.rng.randint(-480, -400)
        for x, y, r in [(0, dy1, 40), (0, dy2, 40)]:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (x, y)
            shape = pymunk.Circle(body, r)
            shape.elasticity = 0.2
            shape.friction = 0.05
            shape.color = (40, 46, 64)
            shape.is_dynamic = False
            self.space.add(body, shape)

    def update(self, frame, dt):
        if frame % 3 != 0:
            return

        blobs = get_blobs(self.space)

        merged = set()
        for i in range(len(blobs)):
            b1 = blobs[i]
            if b1 in merged or b1 not in self.space.bodies:
                continue
            r1 = max((s.radius for s in b1.shapes if isinstance(s, pymunk.Circle)), default=0)
            if r1 == 0:
                continue

            for j in range(i + 1, len(blobs)):
                b2 = blobs[j]
                if b2 in merged or b2 not in self.space.bodies:
                    continue
                r2 = max((s.radius for s in b2.shapes if isinstance(s, pymunk.Circle)), default=0)
                if r2 == 0:
                    continue

                # Improved merge distance: closer blobs merge more easily
                dist = b1.position.get_distance(b2.position)
                if dist < (r1 + r2) * 0.85:
                    merge_blobs(self.space, b1, b2)
                    merged.add(b2)
                    break

        for body in list(self.space.bodies):
            if hasattr(body, "temp") and body.body_type == pymunk.Body.DYNAMIC:
                for s in body.shapes:
                    # Randomize max size slightly per seed
                    max_size = self.rng.randint(55, 75)
                    if isinstance(s, pymunk.Circle) and s.radius > max_size:
                        split_blob(self.space, self.rng, body)
                        break

        current = get_blobs(self.space)
        if len(current) < 8 and frame % 60 == 0:
            create_blob(self.space, self.rng)
