import math
import pymunk


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
    if segments_intersect(p1, p2, q1, q2):
        return 0.0
    return min(
        dist_point_to_segment(p1, q1, q2),
        dist_point_to_segment(p2, q1, q2),
        dist_point_to_segment(q1, p1, p2),
        dist_point_to_segment(q2, p1, p2),
    )


def segments_intersect(p1, p2, q1, q2):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)


def dist_to_wall(p, wall):
    return dist_point_to_segment(p, wall["a"], wall["b"]) - wall.get("radius", 14)


BALLS_MAX_DIAMETER = 40


def is_peg_valid(scene, x, y, radius):
    if abs(x) > scene.W - radius - 15:
        return False
    if y > scene.H * 0.8:
        return False
    if y < -scene.H * 0.55:
        return False
    for wall in scene.walls:
        if dist_to_wall((x, y), wall) < radius + BALLS_MAX_DIAMETER + 10:
            return False
    for px, py, pr in scene.pegs_registry:
        if math.hypot(x - px, y - py) < radius + pr + BALLS_MAX_DIAMETER + 10:
            return False
    for sx, sy, sl in scene.spinners_registry:
        if math.hypot(x - sx, y - sy) < radius + 30:
            return False
    return True


def is_spinner_valid(scene, x, y, arm_length):
    for wall in scene.walls:
        if dist_to_wall((x, y), wall) < arm_length + 25:
            return False
    for sx, sy, sl in scene.spinners_registry:
        if math.hypot(x - sx, y - sy) < arm_length + sl + 35:
            return False
    if y > scene.H * 0.75:
        return False
    if y < -scene.H * 0.6:
        return False
    return True


def is_segment_valid(scene, p1, p2, thickness):
    W, H = scene.W, scene.H
    for x, y in (p1, p2):
        if abs(x) > W - 30:
            return False
        if y > H * 0.75 or y < -H * 0.6:
            return False
    for wall in scene.walls:
        if dist_segment_to_segment(p1, p2, wall["a"], wall["b"]) < thickness + wall["radius"] + BALLS_MAX_DIAMETER + 10:
            return False
    return True


def try_add_wall(scene, a, b, color):
    seg = pymunk.Segment(scene.space.static_body, a, b, 14)
    seg.elasticity = 0.78
    seg.friction = 0.28
    seg.color = color
    seg.is_dynamic = False
    scene.space.add(seg)
    scene.walls.append({"a": a, "b": b, "radius": 14})


def try_add_peg(scene, x, y, radius, max_attempts=15):
    for _ in range(max_attempts):
        jx = x + scene.rng.uniform(-15, 15) if max_attempts > 1 else x
        jy = y + scene.rng.uniform(-10, 10) if max_attempts > 1 else y
        if is_peg_valid(scene, jx, jy, radius):
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (jx, jy)
            shape = pymunk.Circle(body, radius)
            shape.elasticity = 0.92
            shape.friction = 0.1
            shape.color = (120, 138, 160)
            shape.is_dynamic = False
            scene.space.add(body, shape)
            scene.pegs_registry.append((jx, jy, radius))
            return True
    return False


def try_add_spinner(scene, x, y, arm_length, arm_count, speed, max_attempts=20):
    for _ in range(max_attempts):
        jx = x + scene.rng.uniform(-30, 30) if max_attempts > 1 else x
        jy = y + scene.rng.uniform(-30, 30) if max_attempts > 1 else y
        if is_spinner_valid(scene, jx, jy, arm_length):
            body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            body.position = (jx, jy)
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
            scene.spinners_registry.append((jx, jy, arm_length))
            return True
    return False


def spawn_ball(scene):
    radius = scene.rng.randint(12, 20)
    pos = _safe_spawn_pos(scene, radius)
    if not pos:
        return
    mass = 1.0
    inertia = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
    body.position = pos
    point = scene.rng.choice(scene.spawn_points)
    body.velocity = (scene.rng.uniform(*point["vx"]), scene.rng.uniform(*point["vy"]))
    shape = pymunk.Circle(body, radius)
    shape.elasticity = scene.rng.uniform(0.5, 0.85)
    shape.friction = scene.rng.uniform(0.1, 0.4)
    shape.color = scene.rng.choice(scene.palette)
    shape.is_dynamic = True
    scene.space.add(body, shape)


def _safe_spawn_pos(scene, radius):
    for _ in range(100):
        point = scene.rng.choice(scene.spawn_points)
        x = scene.rng.uniform(*point["x_range"])
        y = point["y"] + scene.rng.uniform(-15, 15)
        overlapping = False
        for wall in scene.walls:
            if dist_to_wall((x, y), wall) < radius + 5:
                overlapping = True
                break
        if overlapping:
            continue
        for px, py, pr in scene.pegs_registry:
            if math.hypot(x - px, y - py) < radius + pr + 5:
                overlapping = True
                break
        if overlapping:
            continue
        for sx, sy, sl in scene.spinners_registry:
            if math.hypot(x - sx, y - sy) < radius + sl + 10:
                overlapping = True
                break
        if overlapping:
            continue
        for body in scene.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                for s in body.shapes:
                    if isinstance(s, pymunk.Circle):
                        bx, by = body.position
                        br = s.radius
                        if math.hypot(x - bx, y - by) < radius + br + 5:
                            overlapping = True
                            break
                if overlapping:
                    break
        if overlapping:
            continue
        return x, y
    return None


def recycle_balls(scene):
    still_pending = []
    for body, radius in scene.pending_recycles:
        pos = _safe_spawn_pos(scene, radius)
        if pos:
            body.position = pos
            point = scene.rng.choice(scene.spawn_points)
            body.velocity = (scene.rng.uniform(*point["vx"]), scene.rng.uniform(*point["vy"]))
            body.angular_velocity = 0.0
            scene.space.add(body, *body.shapes)
        else:
            still_pending.append((body, radius))
    scene.pending_recycles = still_pending


def remove_exited_balls(scene):
    recycle_y = -(scene.H + 50)
    for body in list(scene.space.bodies):
        if body.body_type == pymunk.Body.DYNAMIC:
            if body.position.y < recycle_y:
                radius = 16
                for s in body.shapes:
                    if isinstance(s, pymunk.Circle):
                        radius = s.radius
                        break
                scene.space.remove(body, *body.shapes)
                scene.pending_recycles.append((body, radius))
            elif abs(body.position.x) > scene.W * 1.4:
                scene.space.remove(body, *body.shapes)
