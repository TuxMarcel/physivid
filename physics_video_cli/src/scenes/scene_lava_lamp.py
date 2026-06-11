import pymunk
from src.scenes.scene_base import BaseScene
from src.entities.lava_blob import create_blob, get_blobs, merge_blobs, split_blob


class LavaLampScene(BaseScene):
    def setup(self):
        self.space.gravity = (0, -180)
        self._build_vessel()
        self._build_deflectors()

        for _ in range(18):
            create_blob(self.space, self.rng)

    def _build_vessel(self):
        thick = 16
        neck_w = 60
        bot_w = 300
        top_w = 280
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
        for x, y, r in [(0, 420, 40), (0, -440, 40)]:
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

                if b1.position.get_distance(b2.position) < max(r1, r2) * 1.1:
                    merge_blobs(self.space, b1, b2)
                    merged.add(b2)
                    break

        for body in list(self.space.bodies):
            if hasattr(body, "temp") and body.body_type == pymunk.Body.DYNAMIC:
                for s in body.shapes:
                    if isinstance(s, pymunk.Circle) and s.radius > 52:
                        split_blob(self.space, self.rng, body)
                        break

        current = get_blobs(self.space)
        if len(current) < 10 and frame % 60 == 0:
            create_blob(self.space, self.rng)
