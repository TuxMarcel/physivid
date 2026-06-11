import pymunk
import math
from src.scenes.scene_base import BaseScene
from src.entities.ball_pit import (
    try_add_wall, try_add_peg, try_add_spinner, is_segment_valid,
    spawn_ball, recycle_balls, remove_exited_balls,
)


def _build_classic_plinko(scene):
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y = H * 0.95
    bot_y = -H * 0.95

    segs = [
        ((-W, bot_y * 0.6), (-W, top_y)),
        ((W, bot_y * 0.6), (W, top_y)),
        ((-W, bot_y * 0.6), (-hw, bot_y)),
        ((W, bot_y * 0.6), (hw, bot_y)),
        ((-W, top_y), (-hw * 1.6, top_y)),
        ((W, top_y), (hw * 1.6, top_y)),
    ]
    for a, b in segs:
        try_add_wall(scene, a, b, (58, 70, 88))

    count = scene.rng.randint(2, 3)
    xs = [scene.rng.uniform(-W * 0.4, -W * 0.1),
          scene.rng.uniform(W * 0.1, W * 0.4)]
    if count == 3:
        xs.append(0)
    for i, sx in enumerate(xs[:count]):
        sy = scene.rng.uniform(-H * 0.45, -H * 0.05)
        try_add_spinner(scene, sx, sy,
                        scene.rng.randint(90, 140),
                        scene.rng.randint(2, 4),
                        scene.rng.uniform(1.0, 2.5) * (1 if i % 2 == 0 else -1))

    rows = scene.rng.randint(5, 9)
    y_top = H * 0.75
    y_bot = -H * 0.35
    for r in range(rows):
        y = y_top - r * ((y_top - y_bot) / max(rows - 1, 1))
        pegs = 6 if r % 2 == 0 else 5
        spacing = W * 1.6 / (pegs + 1)
        for i in range(pegs):
            x = -W * 0.8 + spacing * (i + 1)
            try_add_peg(scene, x, y, scene.rng.randint(10, 16), max_attempts=15)

    scene.spawn_points = [{"x_range": (-hw * 1.3, hw * 1.3),
                           "y": top_y - 25, "vx": (-60, 60), "vy": (-200, -120)}]


def _build_arena(scene):
    W, H, hw = scene.W, scene.H, scene.hole_w
    aw = W * 0.88
    ah = H * 0.85
    mw = aw * 0.55
    top_y = ah
    bot_y = -ah
    entry_hw = hw * 1.8

    segs = [
        ((-aw, -ah * 0.45), (-aw, ah * 0.45)),
        ((-aw, ah * 0.45), (-mw, top_y)),
        ((-aw, -ah * 0.45), (-mw, bot_y)),
        ((aw, -ah * 0.45), (aw, ah * 0.45)),
        ((aw, ah * 0.45), (mw, top_y)),
        ((aw, -ah * 0.45), (mw, bot_y)),
        ((-mw, top_y), (-entry_hw, top_y)),
        ((mw, top_y), (entry_hw, top_y)),
        ((-mw, bot_y), (-hw, bot_y - H * 0.08)),
        ((mw, bot_y), (hw, bot_y - H * 0.08)),
    ]
    for a, b in segs:
        try_add_wall(scene, a, b, (55, 68, 88))

    for i in range(3):
        angle = i * 2 * math.pi / 3 + scene.rng.uniform(-0.3, 0.3)
        dist = scene.rng.uniform(aw * 0.15, aw * 0.4)
        sx = math.cos(angle) * dist
        sy = math.sin(angle) * dist * 0.6
        try_add_spinner(scene, sx, sy,
                        scene.rng.randint(80, 120), 2,
                        scene.rng.uniform(1.2, 2.8) * (1 if i % 2 == 0 else -1))

    for _ in range(scene.rng.randint(3, 5)):
        cx = scene.rng.uniform(-aw * 0.4, aw * 0.4)
        cy = scene.rng.uniform(-ah * 0.3, ah * 0.5)
        cr = scene.rng.uniform(70, 130)
        pc = scene.rng.randint(4, 8)
        max_pc = max(3, int(2 * math.pi * cr / 70))
        pc = min(pc, max_pc)
        for j in range(pc):
            angle = j * 2 * math.pi / pc
            px = cx + math.cos(angle) * cr
            py = cy + math.sin(angle) * cr
            try_add_peg(scene, px, py, scene.rng.randint(8, 14), max_attempts=5)

    scene.spawn_points = [{"x_range": (-entry_hw * 0.9, entry_hw * 0.9),
                           "y": top_y - 25, "vx": (-50, 50), "vy": (-200, -100)}]


def _build_chaos_chamber(scene):
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y = H * 0.9
    bot_y = -H * 0.75
    entry_hw = hw * 1.5
    wl = W * 1.05

    segs = [
        ((-wl * 0.95, bot_y * 0.6), (-wl, top_y)),
        ((wl * 0.95, bot_y * 0.6), (wl, top_y)),
        ((-wl * 0.95, bot_y * 0.6), (-hw, bot_y)),
        ((wl * 0.95, bot_y * 0.6), (hw, bot_y)),
        ((-wl, top_y), (-entry_hw, top_y)),
        ((wl, top_y), (entry_hw, top_y)),
    ]
    for a, b in segs:
        try_add_wall(scene, a, b, (65, 58, 90))

    for i, (sx, sy_base) in enumerate([
        (-wl * 0.62, H * 0.3), (wl * 0.62, H * 0.3),
        (-wl * 0.62, -H * 0.2), (wl * 0.62, -H * 0.2),
    ]):
        try_add_spinner(scene, sx, sy_base,
                        scene.rng.randint(60, 95),
                        scene.rng.randint(2, 3),
                        scene.rng.uniform(2.0, 3.5) * (1 if i % 2 == 0 else -1))

    pegs_to_place = scene.rng.randint(15, 25)
    placed = 0
    for _ in range(120):
        if placed >= pegs_to_place:
            break
        px = scene.rng.uniform(-wl * 0.8, wl * 0.8)
        py = scene.rng.uniform(-H * 0.45, H * 0.7)
        r = scene.rng.randint(8, 18)
        if try_add_peg(scene, px, py, r, max_attempts=1):
            placed += 1

    scene.spawn_points = [
        {"x_range": (-wl * 0.85, -wl * 0.35), "y": top_y - 35, "vx": (20, 80), "vy": (-180, -100)},
        {"x_range": (wl * 0.35, wl * 0.85), "y": top_y - 35, "vx": (-80, -20), "vy": (-180, -100)},
    ]


def _build_cathedral(scene):
    W, H, hw = scene.W, scene.H, scene.hole_w
    nw = W * 0.62
    top_y = H * 0.95
    bot_y = -H * 0.92
    entry_hw = hw * 0.9

    segs = [
        ((-nw, -H * 0.62), (-nw, top_y)),
        ((nw, -H * 0.62), (nw, top_y)),
        ((-nw, -H * 0.62), (-hw * 0.7, bot_y)),
        ((nw, -H * 0.62), (hw * 0.7, bot_y)),
        ((-nw, top_y), (-entry_hw, top_y)),
        ((nw, top_y), (entry_hw, top_y)),
    ]
    for a, b in segs:
        try_add_wall(scene, a, b, (70, 60, 55))

    try_add_spinner(scene, 0, scene.rng.uniform(-H * 0.28, H * 0.1),
                    scene.rng.randint(120, 170),
                    scene.rng.randint(3, 5),
                    scene.rng.uniform(0.8, 1.6) * scene.rng.choice([-1, 1]))

    for arc in range(scene.rng.randint(3, 5)):
        cy = H * 0.65 - arc * (H * 1.1 / 4)
        pc = scene.rng.randint(4, 7)
        ar = scene.rng.uniform(nw * 0.35, nw * 0.7)
        max_pc = max(3, int(math.pi * ar / 70))
        pc = min(pc, max_pc)
        for j in range(pc):
            angle = math.pi + j * math.pi / max(pc - 1, 1)
            px = math.cos(angle) * ar
            py = cy + math.sin(angle) * ar * 0.5
            try_add_peg(scene, px, py, scene.rng.randint(10, 16), max_attempts=5)

    scene.spawn_points = [{"x_range": (-entry_hw * 0.9, entry_hw * 0.9),
                           "y": top_y - 25, "vx": (-40, 40), "vy": (-200, -130)}]


def _build_pinball(scene):
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y = H * 0.92
    bot_y = -H * 0.9
    entry_hw = hw * 1.6

    segs = [
        ((-W, -H * 0.58), (-W, top_y)),
        ((W, -H * 0.58), (W, top_y)),
        ((-W, -H * 0.58), (-hw, bot_y)),
        ((W, -H * 0.58), (hw, bot_y)),
        ((-W, top_y), (-entry_hw, top_y)),
        ((W, top_y), (entry_hw, top_y)),
    ]
    for a, b in segs:
        try_add_wall(scene, a, b, (55, 80, 65))

    bumpers_to_place = scene.rng.randint(3, 5)
    placed_bumpers = 0
    for _ in range(50):
        if placed_bumpers >= bumpers_to_place:
            break
        side = scene.rng.choice([-1, 1])
        bx = side * scene.rng.uniform(W * 0.1, W * 0.6)
        by = scene.rng.uniform(-H * 0.3, H * 0.62)
        length = scene.rng.uniform(100, 200)
        angle = scene.rng.uniform(-0.6, 0.6)
        x1 = bx - math.cos(angle) * length / 2
        y1 = by - math.sin(angle) * length / 2
        x2 = bx + math.cos(angle) * length / 2
        y2 = by + math.sin(angle) * length / 2

        if is_segment_valid(scene, (x1, y1), (x2, y2), 12):
            seg = pymunk.Segment(scene.space.static_body, (x1, y1), (x2, y2), 12)
            seg.elasticity = 0.85
            seg.friction = 0.2
            seg.color = (90, 150, 90)
            seg.is_dynamic = False
            scene.space.add(seg)
            scene.walls.append({"a": (x1, y1), "b": (x2, y2), "radius": 12})
            placed_bumpers += 1

    spinners_to_place = scene.rng.randint(2, 3)
    placed_spinners = 0
    for _ in range(30):
        if placed_spinners >= spinners_to_place:
            break
        sx = scene.rng.uniform(-W * 0.5, W * 0.5)
        sy = scene.rng.uniform(-H * 0.4, H * 0.35)
        arm = scene.rng.randint(50, 130)
        if try_add_spinner(scene, sx, sy, arm,
                           scene.rng.randint(2, 4),
                           scene.rng.uniform(1.0, 3.0) * scene.rng.choice([-1, 1])):
            placed_spinners += 1

    pegs_to_place = scene.rng.randint(10, 16)
    placed_pegs = 0
    for _ in range(80):
        if placed_pegs >= pegs_to_place:
            break
        px = scene.rng.uniform(-W * 0.8, W * 0.8)
        py = scene.rng.uniform(-H * 0.45, H * 0.7)
        r = scene.rng.randint(8, 20)
        if try_add_peg(scene, px, py, r, max_attempts=1):
            placed_pegs += 1

    scene.spawn_points = [
        {"x_range": (-W * 0.8, -entry_hw * 1.1), "y": top_y - 25, "vx": (20, 90), "vy": (-180, -90)},
        {"x_range": (entry_hw * 1.1, W * 0.8), "y": top_y - 25, "vx": (-90, -20), "vy": (-180, -90)},
    ]


LAYOUTS = [
    _build_classic_plinko,
    _build_arena,
    _build_chaos_chamber,
    _build_cathedral,
    _build_pinball,
]


class BallPitScene(BaseScene):
    def setup(self):
        self.spinners = []
        self.walls = []
        self.pegs_registry = []
        self.spinners_registry = []
        self.pending_recycles = []

        self.W = 520
        self.H = 920
        self.hole_w = self.rng.randint(85, 155)

        layout_fn = LAYOUTS[self.rng.randint(0, len(LAYOUTS) - 1)]
        layout_fn(self)

        for _ in range(self.rng.randint(8, 14)):
            spawn_ball(self)

    def update(self, frame, dt):
        recycle_balls(self)
        remove_exited_balls(self)

        dynamic = [b for b in self.space.bodies if b.body_type == pymunk.Body.DYNAMIC]
        total_balls = len(dynamic) + len(self.pending_recycles)
        if total_balls < self.rng.randint(25, 38) and frame % 35 == 0:
            spawn_ball(self)
