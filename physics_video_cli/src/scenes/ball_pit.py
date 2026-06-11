import pymunk
import math
from src.scenes.base_scene import BaseScene


# ---------------------------------------------------------------------------
# WORLD LAYOUT DEFINITIONS
# Each layout is a dict describing how the room is built.
# The one universal rule: balls spawn top/upper-sides, exit bottom hole.
# ---------------------------------------------------------------------------

def _build_classic_plinko(scene, w, h):
    """Rectangular room, staggered peg rows, 2 central spinners."""
    # Walls
    wall_l = pymunk.Segment(scene.space.static_body, (-w, -h * 0.65), (-w, h), 14)
    wall_r = pymunk.Segment(scene.space.static_body, (w, -h * 0.65), (w, h), 14)
    funnel_l = pymunk.Segment(scene.space.static_body, (-w, -h * 0.65), (-scene.hole_w, -h), 14)
    funnel_r = pymunk.Segment(scene.space.static_body, (w, -h * 0.65), (scene.hole_w, -h), 14)
    top_l = pymunk.Segment(scene.space.static_body, (-w, h), (-scene.hole_w, h), 14)
    top_r = pymunk.Segment(scene.space.static_body, (w, h), (scene.hole_w, h), 14)
    for seg in [wall_l, wall_r, funnel_l, funnel_r, top_l, top_r]:
        seg.elasticity = 0.75
        seg.friction = 0.3
        seg.color = (60, 72, 90)
        seg.is_dynamic = False
        scene.space.add(seg)

    # Staggered peg rows
    rows = scene.rng.randint(5, 9)
    for r in range(rows):
        y = h * 0.7 - r * (h * 1.4 / rows)
        pegs = 6 if r % 2 == 0 else 5
        spacing = w * 1.6 / (pegs + 1)
        for i in range(pegs):
            x = -w * 0.8 + spacing * (i + 1) + scene.rng.uniform(-18, 18)
            yo = scene.rng.uniform(-12, 12)
            _add_peg(scene, x, y + yo, scene.rng.randint(10, 16))

    # 2 spinners at mid-lower area
    spinner_count = scene.rng.randint(2, 3)
    xs = [w * scene.rng.uniform(-0.45, -0.1), w * scene.rng.uniform(0.1, 0.45)]
    if spinner_count == 3:
        xs.append(0)
    for i, sx in enumerate(xs[:spinner_count]):
        sy = scene.rng.uniform(-h * 0.5, -h * 0.1)
        _add_spinner(scene, sx, sy,
                     arm_length=scene.rng.randint(90, 150),
                     arm_count=scene.rng.randint(2, 4),
                     speed=scene.rng.uniform(1.0, 2.5) * (1 if i % 2 == 0 else -1))

    scene.spawn_points = _top_entry_points(scene, w)


def _build_arena(scene, w, h):
    """Hexagonal arena (angled walls), circular peg clusters, 3 spinners."""
    # Hex-ish walls: 6-sided polygon approximation
    angles = [i * math.pi / 3 for i in range(6)]
    radius = w * 1.1
    verts = [(math.cos(a) * radius, math.sin(a) * radius) for a in angles]

    # Build wall segments but skip the bottom-center gap (hole)
    for i in range(len(verts)):
        a = verts[i]
        b = verts[(i + 1) % len(verts)]
        # Skip bottom segment to leave hole
        if a[1] < -h * 0.7 and b[1] < -h * 0.7:
            # Add angled funnel to hole instead
            funnel_l = pymunk.Segment(scene.space.static_body, a, (-scene.hole_w, -h), 14)
            funnel_r = pymunk.Segment(scene.space.static_body, b, (scene.hole_w, -h), 14)
            for seg in [funnel_l, funnel_r]:
                seg.elasticity = 0.75
                seg.friction = 0.3
                seg.color = (55, 68, 88)
                seg.is_dynamic = False
                scene.space.add(seg)
        else:
            seg = pymunk.Segment(scene.space.static_body, a, b, 14)
            seg.elasticity = 0.8
            seg.friction = 0.25
            seg.color = (55, 68, 88)
            seg.is_dynamic = False
            scene.space.add(seg)

    # Circular peg clusters
    cluster_count = scene.rng.randint(3, 5)
    for _ in range(cluster_count):
        cx = scene.rng.uniform(-w * 0.5, w * 0.5)
        cy = scene.rng.uniform(-h * 0.4, h * 0.5)
        cluster_r = scene.rng.uniform(80, 160)
        peg_count = scene.rng.randint(5, 9)
        for j in range(peg_count):
            angle = j * 2 * math.pi / peg_count
            px = cx + math.cos(angle) * cluster_r
            py = cy + math.sin(angle) * cluster_r
            _add_peg(scene, px, py, scene.rng.randint(8, 16))

    # 3 spinners spread around the arena
    for i in range(3):
        angle = i * 2 * math.pi / 3 + scene.rng.uniform(-0.3, 0.3)
        dist = scene.rng.uniform(w * 0.15, w * 0.45)
        sx, sy = math.cos(angle) * dist, math.sin(angle) * dist * 0.7
        _add_spinner(scene, sx, sy,
                     arm_length=scene.rng.randint(80, 130),
                     arm_count=2,
                     speed=scene.rng.uniform(1.2, 2.8) * (1 if i % 2 == 0 else -1))

    scene.spawn_points = _top_side_entry_points(scene, w, h)


def _build_chaos_chamber(scene, w, h):
    """Wide room, random scattered pins, 4 fast edge-mounted spinners."""
    # Wide angled walls
    wall_l = pymunk.Segment(scene.space.static_body, (-w * 1.1, -h * 0.6), (-w * 0.9, h), 14)
    wall_r = pymunk.Segment(scene.space.static_body, (w * 1.1, -h * 0.6), (w * 0.9, h), 14)
    funnel_l = pymunk.Segment(scene.space.static_body, (-w * 1.1, -h * 0.6), (-scene.hole_w, -h), 14)
    funnel_r = pymunk.Segment(scene.space.static_body, (w * 1.1, -h * 0.6), (scene.hole_w, -h), 14)
    top_l = pymunk.Segment(scene.space.static_body, (-w * 0.9, h), (-scene.hole_w, h), 14)
    top_r = pymunk.Segment(scene.space.static_body, (w * 0.9, h), (scene.hole_w, h), 14)
    for seg in [wall_l, wall_r, funnel_l, funnel_r, top_l, top_r]:
        seg.elasticity = 0.85
        seg.friction = 0.2
        seg.color = (65, 58, 90)
        seg.is_dynamic = False
        scene.space.add(seg)

    # Random scattered pegs
    peg_count = scene.rng.randint(18, 30)
    for _ in range(peg_count):
        px = scene.rng.uniform(-w * 0.85, w * 0.85)
        py = scene.rng.uniform(-h * 0.5, h * 0.75)
        _add_peg(scene, px, py, scene.rng.randint(8, 20))

    # 4 fast spinners mounted near the walls
    positions = [
        (-w * 0.65, h * 0.3), (w * 0.65, h * 0.3),
        (-w * 0.65, -h * 0.2), (w * 0.65, -h * 0.2)
    ]
    for i, (sx, sy) in enumerate(positions):
        sy += scene.rng.uniform(-30, 30)
        _add_spinner(scene, sx, sy,
                     arm_length=scene.rng.randint(60, 100),
                     arm_count=scene.rng.randint(2, 3),
                     speed=scene.rng.uniform(2.0, 3.5) * (1 if i % 2 == 0 else -1))

    scene.spawn_points = _top_side_entry_points(scene, w, h)


def _build_cathedral(scene, w, h):
    """Narrow, tall room, arched peg formations, 1 large central spinner."""
    nw = w * 0.65  # Narrow width
    wall_l = pymunk.Segment(scene.space.static_body, (-nw, -h * 0.65), (-nw, h), 14)
    wall_r = pymunk.Segment(scene.space.static_body, (nw, -h * 0.65), (nw, h), 14)
    funnel_l = pymunk.Segment(scene.space.static_body, (-nw, -h * 0.65), (-scene.hole_w * 0.6, -h), 14)
    funnel_r = pymunk.Segment(scene.space.static_body, (nw, -h * 0.65), (scene.hole_w * 0.6, -h), 14)
    top_l = pymunk.Segment(scene.space.static_body, (-nw, h), (-scene.hole_w * 0.5, h), 14)
    top_r = pymunk.Segment(scene.space.static_body, (nw, h), (scene.hole_w * 0.5, h), 14)
    for seg in [wall_l, wall_r, funnel_l, funnel_r, top_l, top_r]:
        seg.elasticity = 0.72
        seg.friction = 0.35
        seg.color = (70, 60, 55)
        seg.is_dynamic = False
        scene.space.add(seg)

    # Arched peg formations
    arch_count = scene.rng.randint(3, 5)
    for arc in range(arch_count):
        cy = h * 0.65 - arc * (h * 1.2 / arch_count)
        peg_count = scene.rng.randint(4, 7)
        arch_radius = scene.rng.uniform(nw * 0.3, nw * 0.75)
        for j in range(peg_count):
            angle = math.pi + j * math.pi / (peg_count - 1)
            px = math.cos(angle) * arch_radius + scene.rng.uniform(-15, 15)
            py = cy + math.sin(angle) * arch_radius * 0.5 + scene.rng.uniform(-10, 10)
            _add_peg(scene, px, py, scene.rng.randint(10, 18))

    # 1 large central spinner
    _add_spinner(scene, 0, scene.rng.uniform(-h * 0.3, h * 0.1),
                 arm_length=scene.rng.randint(130, 200),
                 arm_count=scene.rng.randint(3, 6),
                 speed=scene.rng.uniform(0.8, 1.6) * scene.rng.choice([-1, 1]))

    scene.spawn_points = _top_entry_points(scene, nw)


def _build_pinball(scene, w, h):
    """Angled bumper walls inside, many pegs, mixed-size spinners."""
    wall_l = pymunk.Segment(scene.space.static_body, (-w, -h * 0.6), (-w, h), 14)
    wall_r = pymunk.Segment(scene.space.static_body, (w, -h * 0.6), (w, h), 14)
    funnel_l = pymunk.Segment(scene.space.static_body, (-w, -h * 0.6), (-scene.hole_w, -h), 14)
    funnel_r = pymunk.Segment(scene.space.static_body, (w, -h * 0.6), (scene.hole_w, -h), 14)
    top_l = pymunk.Segment(scene.space.static_body, (-w, h), (-scene.hole_w, h), 14)
    top_r = pymunk.Segment(scene.space.static_body, (w, h), (scene.hole_w, h), 14)
    for seg in [wall_l, wall_r, funnel_l, funnel_r, top_l, top_r]:
        seg.elasticity = 0.9
        seg.friction = 0.15
        seg.color = (55, 80, 65)
        seg.is_dynamic = False
        scene.space.add(seg)

    # Angled internal bumper platforms (like pinball flippers as static geometry)
    bumper_count = scene.rng.randint(3, 5)
    for i in range(bumper_count):
        side = scene.rng.choice([-1, 1])
        bx = side * scene.rng.uniform(w * 0.1, w * 0.6)
        by = scene.rng.uniform(-h * 0.3, h * 0.6)
        length = scene.rng.uniform(100, 220)
        angle = scene.rng.uniform(-0.6, 0.6)
        x1 = bx - math.cos(angle) * length / 2
        y1 = by - math.sin(angle) * length / 2
        x2 = bx + math.cos(angle) * length / 2
        y2 = by + math.sin(angle) * length / 2
        seg = pymunk.Segment(scene.space.static_body, (x1, y1), (x2, y2), 12)
        seg.elasticity = 0.85
        seg.friction = 0.2
        seg.color = (100, 160, 100)
        seg.is_dynamic = False
        scene.space.add(seg)

    # Mixed-size pegs
    for _ in range(scene.rng.randint(12, 22)):
        px = scene.rng.uniform(-w * 0.8, w * 0.8)
        py = scene.rng.uniform(-h * 0.45, h * 0.7)
        _add_peg(scene, px, py, scene.rng.randint(8, 22))

    # Mixed-size spinners
    spinner_count = scene.rng.randint(2, 4)
    for i in range(spinner_count):
        sx = scene.rng.uniform(-w * 0.55, w * 0.55)
        sy = scene.rng.uniform(-h * 0.45, h * 0.35)
        _add_spinner(scene, sx, sy,
                     arm_length=scene.rng.randint(50, 160),
                     arm_count=scene.rng.randint(2, 4),
                     speed=scene.rng.uniform(1.0, 3.0) * scene.rng.choice([-1, 1]))

    scene.spawn_points = _top_side_entry_points(scene, w, h)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _add_peg(scene, x, y, radius):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = (x, y)
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.9
    shape.friction = 0.1
    shape.color = (120, 138, 160)
    shape.is_dynamic = False
    scene.space.add(body, shape)


def _add_spinner(scene, x, y, arm_length, arm_count, speed):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = (x, y)
    body.angular_velocity = speed
    scene.space.add(body)
    scene.spinners.append(body)

    for i in range(arm_count):
        angle = i * math.pi / (arm_count / 2)
        dx = arm_length * math.cos(angle)
        dy = arm_length * math.sin(angle)
        seg = pymunk.Segment(body, (-dx, -dy), (dx, dy), 9)
        seg.elasticity = 0.75
        seg.friction = 0.2
        seg.color = (200, 130, 60)
        seg.is_dynamic = False
        scene.space.add(seg)


def _top_entry_points(scene, w):
    """Ball entry from top center gap."""
    return [{"x_range": (-min(w * 0.5, 200), min(w * 0.5, 200)), "y": 860, "vx": (-60, 60), "vy": (-180, -120)}]


def _top_side_entry_points(scene, w, h):
    """Ball entry from top-left and top-right."""
    return [
        {"x_range": (-w * 0.9, -w * 0.4), "y": 830, "vx": (30, 100), "vy": (-150, -80)},
        {"x_range": (w * 0.4, w * 0.9), "y": 830, "vx": (-100, -30), "vy": (-150, -80)},
    ]


# Layout registry keyed by index
LAYOUTS = [
    _build_classic_plinko,
    _build_arena,
    _build_chaos_chamber,
    _build_cathedral,
    _build_pinball,
]


# ---------------------------------------------------------------------------
# BallPitScene
# ---------------------------------------------------------------------------

class BallPitScene(BaseScene):
    def setup(self):
        self.spinners = []

        # Hole half-width (balls exit through center bottom)
        self.hole_w = self.rng.randint(80, 150)

        # Select a layout deterministically from the seed
        layout_index = self.rng.randint(0, len(LAYOUTS) - 1)
        layout_fn = LAYOUTS[layout_index]

        # World dimensions (fixed logical space)
        self.W = 520   # half-width
        self.H = 920   # half-height

        layout_fn(self, self.W, self.H)

        # Spawn initial balls
        for _ in range(self.rng.randint(8, 14)):
            self.spawn_ball()

    def spawn_ball(self):
        radius = self.rng.randint(14, 26)
        mass = 1.0
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)

        # Pick a random spawn point from the layout's defined entry points
        point = self.rng.choice(self.spawn_points)
        spawn_x = self.rng.uniform(*point["x_range"])
        spawn_y = point["y"] + self.rng.uniform(-30, 30)
        vx = self.rng.uniform(*point["vx"])
        vy = self.rng.uniform(*point["vy"])

        body.position = (spawn_x, spawn_y)
        body.velocity = (vx, vy)

        shape = pymunk.Circle(body, radius)
        shape.elasticity = self.rng.uniform(0.5, 0.85)
        shape.friction = self.rng.uniform(0.1, 0.4)
        shape.color = self.rng.choice(self.palette)
        shape.is_dynamic = True

        self.space.add(body, shape)

    def update(self, frame, dt):
        # Recycle balls that exit through the bottom hole
        for body in list(self.space.bodies):
            if body.body_type == pymunk.Body.DYNAMIC:
                if body.position.y < -(self.H + 60):
                    point = self.rng.choice(self.spawn_points)
                    spawn_x = self.rng.uniform(*point["x_range"])
                    body.position = (spawn_x, point["y"])
                    body.velocity = (self.rng.uniform(*point["vx"]),
                                     self.rng.uniform(*point["vy"]))
                    body.angular_velocity = 0.0

        # Top up balls gradually to a target count
        dynamic = [b for b in self.space.bodies if b.body_type == pymunk.Body.DYNAMIC]
        target = self.rng.randint(25, 40)
        if len(dynamic) < target and frame % 35 == 0:
            self.spawn_ball()
