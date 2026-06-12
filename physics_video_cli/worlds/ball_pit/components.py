import math
import pymunk
from entities.shapes import CircleEntity, SegmentEntity

BALLS_MAX_DIAMETER = 40

def dist_point_to_segment(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx*abx + aby*aby
    if ab2 == 0: return math.hypot(apx, apy)
    t = max(0.0, min(1.0, (apx*abx + apy*aby) / ab2))
    return math.hypot(px - (ax + t * abx), py - (ay + t * aby))

def dist_segment_to_segment(p1, p2, q1, q2):
    def ccw(A, B, C): return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    intersect = ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
    if intersect: return 0.0
    return min(dist_point_to_segment(p1, q1, q2), dist_point_to_segment(p2, q1, q2),
               dist_point_to_segment(q1, p1, p2), dist_point_to_segment(q2, p1, p2))

def is_peg_valid(scene, x, y, radius):
    if abs(x) > scene.W - radius - 15 or y > scene.H * 0.8 or y < -scene.H * 0.55: return False
    for wall in scene.walls:
        if dist_point_to_segment((x, y), wall["a"], wall["b"]) - wall.get("radius", 14) < radius + BALLS_MAX_DIAMETER + 10: return False
    for px, py, pr in scene.pegs_registry:
        if math.hypot(x - px, y - py) < radius + pr + BALLS_MAX_DIAMETER + 10: return False
    for sx, sy, sl in scene.spinners_registry:
        if math.hypot(x - sx, y - sy) < radius + 30: return False
    return True

def try_add_wall(scene, a, b, color):
    wall = SegmentEntity(a, b, radius=14, color=color)
    wall.shape.elasticity = 0.78
    wall.shape.friction = 0.28
    wall.add_to_space(scene.space)
    scene.walls.append({"a": a, "b": b, "radius": 14})
    scene.entities.append(wall)

def try_add_peg(scene, x, y, radius, max_attempts=15):
    for _ in range(max_attempts):
        jx = x + scene.rng.uniform(-15, 15) if max_attempts > 1 else x
        jy = y + scene.rng.uniform(-10, 10) if max_attempts > 1 else y
        if is_peg_valid(scene, jx, jy, radius):
            peg = CircleEntity(jx, jy, radius, is_static=True, color=(120, 138, 160))
            peg.shape.elasticity = 0.92
            peg.shape.friction = 0.1
            peg.add_to_space(scene.space)
            scene.pegs_registry.append((jx, jy, radius))
            scene.entities.append(peg)
            return True
    return False

def try_add_spinner(scene, x, y, arm_length, arm_count, speed, max_attempts=20):
    for _ in range(max_attempts):
        jx = x + scene.rng.uniform(-30, 30) if max_attempts > 1 else x
        jy = y + scene.rng.uniform(-30, 30) if max_attempts > 1 else y
        # Simple validation for now
        if y > scene.H * 0.75 or y < -scene.H * 0.6: continue
        
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        body.position = (jx, jy)
        body.angular_velocity = speed
        scene.space.add(body)
        scene.spinners.append(body)
        for i in range(arm_count):
            angle = i * math.pi / (arm_count / 2)
            dx, dy = arm_length * math.cos(angle), arm_length * math.sin(angle)
            seg = pymunk.Segment(body, (-dx, -dy), (dx, dy), 9)
            seg.elasticity = 0.75
            seg.friction = 0.2
            seg.color = (200, 130, 60)
            seg.is_dynamic = False
            scene.space.add(seg)
        scene.spinners_registry.append((jx, jy, arm_length))
        return True
    return False

def spawn_ball(scene):
    radius = scene.rng.randint(12, 20)
    pos = _safe_spawn_pos(scene, radius)
    if not pos: return
    
    point = scene.rng.choice(scene.spawn_points)
    ball = CircleEntity(pos[0], pos[1], radius, color=scene.rng.choice(scene.palette), trail=True, trail_len=15)
    ball.body.velocity = (scene.rng.uniform(*point["vx"]), scene.rng.uniform(*point["vy"]))
    ball.shape.elasticity = scene.rng.uniform(0.5, 0.85)
    ball.shape.friction = scene.rng.uniform(0.1, 0.4)
    ball.add_to_space(scene.space)
    scene.entities.append(ball)

def _safe_spawn_pos(scene, radius):
    for _ in range(50):
        point = scene.rng.choice(scene.spawn_points)
        x = scene.rng.uniform(*point["x_range"])
        y = point["y"] + scene.rng.uniform(-15, 15)
        overlapping = False
        for px, py, pr in scene.pegs_registry:
            if math.hypot(x - px, y - py) < radius + pr + 5:
                overlapping = True; break
        if not overlapping: return x, y
    return None

def recycle_balls(scene):
    recycle_y = -(scene.H + 50)
    for entity in list(scene.entities):
        if hasattr(entity, "body") and entity.body.body_type == pymunk.Body.DYNAMIC:
            if entity.body.position.y < recycle_y:
                pos = _safe_spawn_pos(scene, entity.shape.radius)
                if pos:
                    entity.body.position = pos
                    point = scene.rng.choice(scene.spawn_points)
                    entity.body.velocity = (scene.rng.uniform(*point["vx"]), scene.rng.uniform(*point["vy"]))
                    entity.body.angular_velocity = 0.0
                else:
                    entity.remove_from_space(scene.space)
                    scene.entities.remove(entity)
