import pymunk
import math
from src.scenes.base_scene import BaseScene


# ---------------------------------------------------------------------------
# DESIGN & VALIDATION CONSTANTS
# ---------------------------------------------------------------------------
BALLS_MAX_DIAMETER = 40  # Assuming maximum ball radius is 20 (diameter 40)


# ---------------------------------------------------------------------------
# GEOMETRY HELPERS
# ---------------------------------------------------------------------------
def dist_point_to_segment(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx*abx + aby*aby
    if ab2 == 0:
        return math.hypot(apx, apy)
    t = (apx*abx + apy*aby) / ab2
    t = max(0.0, min(1.0, t))
    proj_x = ax + t * abx
    proj_y = ay + t * aby
    return math.hypot(px - proj_x, py - proj_y)


def dist_segment_to_segment(p1, p2, q1, q2):
    # Check if segments intersect
    if segments_intersect(p1, p2, q1, q2):
        return 0.0
    return min(
        dist_point_to_segment(p1, q1, q2),
        dist_point_to_segment(p2, q1, q2),
        dist_point_to_segment(q1, p1, p2),
        dist_point_to_segment(q2, p1, p2)
    )


def segments_intersect(p1, p2, q1, q2):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)


def dist_to_wall(p, wall):
    return dist_point_to_segment(p, wall['a'], wall['b']) - wall.get('radius', 14)


# ---------------------------------------------------------------------------
# VALIDATION LOGIC
# ---------------------------------------------------------------------------
def _is_peg_position_valid(scene, x, y, radius):
    # 1. Check boundary limits
    if abs(x) > scene.W - radius - 15:
        return False
    if y > scene.H * 0.8:  # Too high, might block spawn
        return False
    if y < -scene.H * 0.55:  # Too low, might block exit funnel
        return False
        
    # 2. Check distance to all walls/bumpers
    for wall in scene.walls:
        if dist_to_wall((x, y), wall) < radius + BALLS_MAX_DIAMETER + 10:
            return False
            
    # 3. Check distance to all existing pegs
    for px, py, pr in scene.pegs_registry:
        if math.hypot(x - px, y - py) < radius + pr + BALLS_MAX_DIAMETER + 10:
            return False
            
    # 4. Check distance to spinner centers (must not overlap with the spinner pivot)
    for sx, sy, sl in scene.spinners_registry:
        if math.hypot(x - sx, y - sy) < radius + 30:
            return False
            
    return True


def _is_spinner_position_valid(scene, x, y, arm_length):
    # 1. Spinners shouldn't be too close to walls (must not clip walls)
    for wall in scene.walls:
        if dist_to_wall((x, y), wall) < arm_length + 25:
            return False
            
    # 2. Spinners shouldn't overlap with other spinners
    for sx, sy, sl in scene.spinners_registry:
        if math.hypot(x - sx, y - sy) < arm_length + sl + 35:
            return False
            
    # 3. Spinners shouldn't block the exit or spawn area
    if y > scene.H * 0.75:
        return False
    if y < -scene.H * 0.6:
        return False
        
    return True


def _is_segment_valid(scene, p1, p2, thickness):
    W, H = scene.W, scene.H
    # Check boundaries
    for x, y in (p1, p2):
        if abs(x) > W - 30:
            return False
        if y > H * 0.75 or y < -H * 0.6:
            return False
            
    # Check distance to all existing walls
    for wall in scene.walls:
        if dist_segment_to_segment(p1, p2, wall['a'], wall['b']) < thickness + wall['radius'] + BALLS_MAX_DIAMETER + 10:
            return False
            
    return True


# ---------------------------------------------------------------------------
# SAFE CREATION HELPERS
# ---------------------------------------------------------------------------
def try_add_peg(scene, x, y, radius, max_attempts=15):
    for _ in range(max_attempts):
        jx = x + scene.rng.uniform(-15, 15) if max_attempts > 1 else x
        jy = y + scene.rng.uniform(-10, 10) if max_attempts > 1 else y
        if _is_peg_position_valid(scene, jx, jy, radius):
            _add_peg(scene, jx, jy, radius)
            return True
    return False


def try_add_spinner(scene, x, y, arm_length, arm_count, speed, max_attempts=20):
    for _ in range(max_attempts):
        jx = x + scene.rng.uniform(-30, 30) if max_attempts > 1 else x
        jy = y + scene.rng.uniform(-30, 30) if max_attempts > 1 else y
        if _is_spinner_position_valid(scene, jx, jy, arm_length):
            _add_spinner(scene, jx, jy, arm_length, arm_count, speed)
            return True
    return False


# ---------------------------------------------------------------------------
# WORLD LAYOUT DEFINITIONS
# ---------------------------------------------------------------------------
def _build_classic_plinko(scene):
    """Rectangular room, staggered peg rows, 2–3 central spinners."""
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y   =  H * 0.95
    bot_y   = -H * 0.95

    # Explicit walls: left, right, bottom-funnel, top-funnel (with gap)
    segs = [
        ((-W, bot_y * 0.6), (-W, top_y)),          # left wall
        (( W, bot_y * 0.6), ( W, top_y)),          # right wall
        ((-W, bot_y * 0.6), (-hw, bot_y)),          # funnel left
        (( W, bot_y * 0.6), ( hw, bot_y)),          # funnel right
        # Top with entry gap (left + right blocks, center open)
        ((-W, top_y), (-hw * 1.6, top_y)),          # top-left block
        (( W, top_y), ( hw * 1.6, top_y)),          # top-right block
    ]
    _add_walls(scene, segs, (58, 70, 88))

    # Spinners first (so pegs can avoid them)
    count = scene.rng.randint(2, 3)
    xs = [scene.rng.uniform(-W * 0.4, -W * 0.1),
          scene.rng.uniform( W * 0.1,  W * 0.4)]
    if count == 3:
        xs.append(0)
    for i, sx in enumerate(xs[:count]):
        sy = scene.rng.uniform(-H * 0.45, -H * 0.05)
        try_add_spinner(scene, sx, sy,
                        scene.rng.randint(90, 140),
                        scene.rng.randint(2, 4),
                        scene.rng.uniform(1.0, 2.5) * (1 if i % 2 == 0 else -1))

    # Staggered peg rows
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
    """Octagonal arena, circular peg clusters, 3 spinners."""
    W, H, hw = scene.W, scene.H, scene.hole_w
    aw = W * 0.88     # arena half-width
    ah = H * 0.85     # arena half-height
    mw = aw * 0.55    # mid-width (diagonal cut point)

    top_y    =  ah
    bot_y    = -ah
    entry_hw =  hw * 1.8   # width of top opening

    # 8 segments: skip top-center (entry) and add bottom funnel
    segs = [
        # Left side
        ((-aw, -ah * 0.45), (-aw,  ah * 0.45)),      # left vertical
        ((-aw,  ah * 0.45), (-mw,  top_y)),           # upper-left diagonal
        ((-aw, -ah * 0.45), (-mw,  bot_y)),           # lower-left diagonal
        # Right side
        (( aw, -ah * 0.45), ( aw,  ah * 0.45)),      # right vertical
        (( aw,  ah * 0.45), ( mw,  top_y)),           # upper-right diagonal
        (( aw, -ah * 0.45), ( mw,  bot_y)),           # lower-right diagonal
        # Top: two blocks leaving central gap
        ((-mw, top_y), (-entry_hw, top_y)),
        (( mw, top_y), ( entry_hw, top_y)),
        # Bottom funnel converging to hole
        ((-mw, bot_y), (-hw, bot_y - H * 0.08)),
        (( mw, bot_y), ( hw, bot_y - H * 0.08)),
    ]
    _add_walls(scene, segs, (55, 68, 88))

    # 3 spinners spread inside arena first
    for i in range(3):
        angle = i * 2 * math.pi / 3 + scene.rng.uniform(-0.3, 0.3)
        dist  = scene.rng.uniform(aw * 0.15, aw * 0.4)
        sx = math.cos(angle) * dist
        sy = math.sin(angle) * dist * 0.6
        try_add_spinner(scene, sx, sy,
                        scene.rng.randint(80, 120), 2,
                        scene.rng.uniform(1.2, 2.8) * (1 if i % 2 == 0 else -1))

    # Circular peg clusters inside the arena
    for _ in range(scene.rng.randint(3, 5)):
        cx = scene.rng.uniform(-aw * 0.4, aw * 0.4)
        cy = scene.rng.uniform(-ah * 0.3, ah * 0.5)
        cr = scene.rng.uniform(70, 130)
        # Limit pc to avoid packing pegs too closely on the circle
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
    """Wide angled walls, many random pegs, 4 fast edge spinners."""
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y  =  H * 0.9
    bot_y  = -H * 0.75
    entry_hw = hw * 1.5

    # Slightly angled wide walls
    wl = W * 1.05
    segs = [
        ((-wl * 0.95, bot_y * 0.6), (-wl, top_y)),
        (( wl * 0.95, bot_y * 0.6), ( wl, top_y)),
        ((-wl * 0.95, bot_y * 0.6), (-hw, bot_y)),
        (( wl * 0.95, bot_y * 0.6), ( hw, bot_y)),
        ((-wl, top_y), (-entry_hw, top_y)),
        (( wl, top_y), ( entry_hw, top_y)),
    ]
    _add_walls(scene, segs, (65, 58, 90))

    # 4 fast spinners near the walls first
    for i, (sx, sy_base) in enumerate([
        (-wl * 0.62, H * 0.3), (wl * 0.62, H * 0.3),
        (-wl * 0.62, -H * 0.2), (wl * 0.62, -H * 0.2)
    ]):
        try_add_spinner(scene, sx, sy_base,
                        scene.rng.randint(60, 95),
                        scene.rng.randint(2, 3),
                        scene.rng.uniform(2.0, 3.5) * (1 if i % 2 == 0 else -1))

    # Lots of random scattered pegs (validating each)
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

    # Two side entry points plus top
    scene.spawn_points = [
        {"x_range": (-wl * 0.85, -wl * 0.35), "y": top_y - 35, "vx": (20, 80),  "vy": (-180, -100)},
        {"x_range": ( wl * 0.35,  wl * 0.85), "y": top_y - 35, "vx": (-80, -20), "vy": (-180, -100)},
    ]


def _build_cathedral(scene):
    """Narrow tall room, arched peg formations, 1 large central spinner."""
    W, H, hw = scene.W, scene.H, scene.hole_w
    nw      = W * 0.62   # narrow half-width
    top_y   =  H * 0.95
    bot_y   = -H * 0.92
    entry_hw = hw * 0.9

    segs = [
        ((-nw, -H * 0.62), (-nw, top_y)),
        (( nw, -H * 0.62), ( nw, top_y)),
        ((-nw, -H * 0.62), (-hw * 0.7, bot_y)),
        (( nw, -H * 0.62), ( hw * 0.7, bot_y)),
        ((-nw, top_y), (-entry_hw, top_y)),
        (( nw, top_y), ( entry_hw, top_y)),
    ]
    _add_walls(scene, segs, (70, 60, 55))

    # 1 big central spinner first
    try_add_spinner(scene, 0, scene.rng.uniform(-H * 0.28, H * 0.1),
                    scene.rng.randint(120, 170),
                    scene.rng.randint(3, 5),
                    scene.rng.uniform(0.8, 1.6) * scene.rng.choice([-1, 1]))

    # Arched peg formations
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
    """Angled bumper walls inside, mixed pegs, mixed-size spinners."""
    W, H, hw = scene.W, scene.H, scene.hole_w
    top_y    =  H * 0.92
    bot_y    = -H * 0.9
    entry_hw =  hw * 1.6

    segs = [
        ((-W, -H * 0.58), (-W, top_y)),
        (( W, -H * 0.58), ( W, top_y)),
        ((-W, -H * 0.58), (-hw, bot_y)),
        (( W, -H * 0.58), ( hw, bot_y)),
        ((-W, top_y), (-entry_hw, top_y)),
        (( W, top_y), ( entry_hw, top_y)),
    ]
    _add_walls(scene, segs, (55, 80, 65))

    # Angled internal bumper platforms (validating each)
    bumpers_to_place = scene.rng.randint(3, 5)
    placed_bumpers = 0
    for _ in range(50):
        if placed_bumpers >= bumpers_to_place:
            break
        side   = scene.rng.choice([-1, 1])
        bx     = side * scene.rng.uniform(W * 0.1, W * 0.6)
        by     = scene.rng.uniform(-H * 0.3, H * 0.62)
        length = scene.rng.uniform(100, 200)
        angle  = scene.rng.uniform(-0.6, 0.6)
        x1 = bx - math.cos(angle) * length / 2
        y1 = by - math.sin(angle) * length / 2
        x2 = bx + math.cos(angle) * length / 2
        y2 = by + math.sin(angle) * length / 2
        
        if _is_segment_valid(scene, (x1, y1), (x2, y2), 12):
            seg = pymunk.Segment(scene.space.static_body, (x1, y1), (x2, y2), 12)
            seg.elasticity = 0.85
            seg.friction   = 0.2
            seg.color      = (90, 150, 90)
            seg.is_dynamic = False
            scene.space.add(seg)
            scene.walls.append({'a': (x1, y1), 'b': (x2, y2), 'radius': 12})
            placed_bumpers += 1

    # Mixed spinners first (so pegs avoid them)
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

    # Mixed pegs
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
        {"x_range": (-W * 0.8, -entry_hw * 1.1), "y": top_y - 25, "vx": (20, 90),  "vy": (-180, -90)},
        {"x_range": ( entry_hw * 1.1,  W * 0.8), "y": top_y - 25, "vx": (-90, -20), "vy": (-180, -90)},
    ]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _add_walls(scene, segments, color):
    for a, b in segments:
        seg = pymunk.Segment(scene.space.static_body, a, b, 14)
        seg.elasticity = 0.78
        seg.friction   = 0.28
        seg.color      = color
        seg.is_dynamic = False
        scene.space.add(seg)
        scene.walls.append({'a': a, 'b': b, 'radius': 14})


def _add_peg(scene, x, y, radius):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = (x, y)
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.92
    shape.friction   = 0.1
    shape.color      = (120, 138, 160)
    shape.is_dynamic = False
    scene.space.add(body, shape)
    scene.pegs_registry.append((x, y, radius))


def _add_spinner(scene, x, y, arm_length, arm_count, speed):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position        = (x, y)
    body.angular_velocity = speed
    scene.space.add(body)
    scene.spinners.append(body)
    for i in range(arm_count):
        angle = i * math.pi / (arm_count / 2)
        dx = arm_length * math.cos(angle)
        dy = arm_length * math.sin(angle)
        seg = pymunk.Segment(body, (-dx, -dy), (dx, dy), 9)
        seg.elasticity = 0.75
        seg.friction   = 0.2
        seg.color      = (200, 130, 60)
        seg.is_dynamic = False
        scene.space.add(seg)
    scene.spinners_registry.append((x, y, arm_length))


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
        self.walls = []
        self.pegs_registry = []
        self.spinners_registry = []
        self.pending_recycles = []

        # Consistent logical space
        self.W = 520
        self.H = 920
        # Hole half-width (varies by seed but is always reasonable)
        self.hole_w = self.rng.randint(85, 155)

        # Pick a layout
        layout_fn = LAYOUTS[self.rng.randint(0, len(LAYOUTS) - 1)]
        layout_fn(self)

        # Spawn initial balls
        for _ in range(self.rng.randint(8, 14)):
            self.spawn_ball()

    def spawn_ball(self):
        radius = self.rng.randint(12, 20)
        pos = self.get_safe_spawn_position(radius)
        if not pos:
            return  # Skip if no safe space is currently available
            
        mass   = 1.0
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        body   = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
        body.position = pos

        point  = self.rng.choice(self.spawn_points)
        body.velocity = (self.rng.uniform(*point["vx"]),
                         self.rng.uniform(*point["vy"]))

        shape = pymunk.Circle(body, radius)
        shape.elasticity = self.rng.uniform(0.5, 0.85)
        shape.friction   = self.rng.uniform(0.1, 0.4)
        shape.color      = self.rng.choice(self.palette)
        shape.is_dynamic = True
        self.space.add(body, shape)

    def get_safe_spawn_position(self, radius):
        # Find a spawn position that doesn't overlap with any scene objects or other balls
        for _ in range(100):
            point = self.rng.choice(self.spawn_points)
            x = self.rng.uniform(*point["x_range"])
            y = point["y"] + self.rng.uniform(-15, 15)
            
            overlapping = False
            for wall in self.walls:
                if dist_to_wall((x, y), wall) < radius + 5:
                    overlapping = True
                    break
            if overlapping:
                continue
                
            for px, py, pr in self.pegs_registry:
                if math.hypot(x - px, y - py) < radius + pr + 5:
                    overlapping = True
                    break
            if overlapping:
                continue
                
            for sx, sy, sl in self.spinners_registry:
                if math.hypot(x - sx, y - sy) < radius + sl + 10:
                    overlapping = True
                    break
            if overlapping:
                continue
                
            for body in self.space.bodies:
                if body.body_type == pymunk.Body.DYNAMIC:
                    for shape in body.shapes:
                        if isinstance(shape, pymunk.Circle):
                            bx, by = body.position
                            br = shape.radius
                            if math.hypot(x - bx, y - by) < radius + br + 5:
                                overlapping = True
                                break
                    if overlapping:
                        break
            if overlapping:
                continue
                
            return x, y
        return None

    def update(self, frame, dt):
        # 1. Process pending recycles
        still_pending = []
        for body, radius in self.pending_recycles:
            pos = self.get_safe_spawn_position(radius)
            if pos:
                body.position = pos
                point = self.rng.choice(self.spawn_points)
                body.velocity = (self.rng.uniform(*point["vx"]),
                                 self.rng.uniform(*point["vy"]))
                body.angular_velocity = 0.0
                self.space.add(body, *body.shapes)
            else:
                still_pending.append((body, radius))
        self.pending_recycles = still_pending

        # 2. Recycle / remove exiting balls
        recycle_y = -(self.H + 50)
        for body in list(self.space.bodies):
            if body.body_type == pymunk.Body.DYNAMIC:
                # Recycle balls that exit through the bottom hole
                if body.position.y < recycle_y:
                    radius = 16
                    for s in body.shapes:
                        if isinstance(s, pymunk.Circle):
                            radius = s.radius
                            break
                    self.space.remove(body, *body.shapes)
                    self.pending_recycles.append((body, radius))
                # Remove balls that escape through the sides (shouldn't happen, but safety net)
                elif abs(body.position.x) > self.W * 1.4:
                    self.space.remove(body, *body.shapes)

        # 3. Top up balls to target count
        dynamic = [b for b in self.space.bodies if b.body_type == pymunk.Body.DYNAMIC]
        total_balls = len(dynamic) + len(self.pending_recycles)
        if total_balls < self.rng.randint(25, 38) and frame % 35 == 0:
            self.spawn_ball()
