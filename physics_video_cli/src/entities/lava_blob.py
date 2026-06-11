import pymunk
import math


BLOB_FILTER = pymunk.ShapeFilter(group=1)

def create_blob(space, rng, x=None, y=None, temp=None, radius=None, phase=None, speed=None, amp=None):
    radius = radius if radius else rng.randint(18, 40)
    mass = radius * 0.06
    inertia = pymunk.moment_for_circle(mass, 0, radius)

    body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
    body.position = (
        x if x is not None else rng.randint(-100, 100),
        y if y is not None else rng.randint(-600, 600),
    )
    body.temp = temp if temp is not None else rng.uniform(0.3, 0.7)
    body.lateral_phase = phase if phase is not None else rng.uniform(0, 2 * math.pi)
    body.lateral_speed = speed if speed is not None else rng.uniform(0.3, 0.8)
    body.lateral_amp = amp if amp is not None else rng.uniform(8, 25)
    body.trail_len = 5
    body.velocity_func = _lava_velocity_update

    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.02
    shape.friction = 0.02
    shape.is_dynamic = True
    shape.filter = BLOB_FILTER

    space.add(body, shape)
    return body


def _lava_velocity_update(body, gravity, damping, dt):
    y = body.position.y

    if y < -200:
        target = 1.0
        rate = 1.5
    elif y > 200:
        target = 0.0
        rate = 1.5
    else:
        t = (y + 200) / 400.0
        target = 1.0 - t
        rate = 0.6

    body.temp += (target - body.temp) * rate * dt
    body.temp = max(0.0, min(1.0, body.temp))

    buoyancy = body.temp * 320.0
    body.velocity = (body.velocity.x, body.velocity.y + buoyancy * dt)

    if body.velocity.y > 120:
        body.velocity = (body.velocity.x, 120)
    if body.velocity.y < -80:
        body.velocity = (body.velocity.x, -80)

    body.lateral_phase += body.lateral_speed * dt
    amp = body.lateral_amp * (0.3 + 0.7 * body.temp)
    drift_x = math.sin(body.lateral_phase) * amp * dt
    body.velocity = (body.velocity.x + drift_x, body.velocity.y)

    pymunk.Body.update_velocity(body, gravity, damping, dt)


def get_radius(body):
    for s in body.shapes:
        if isinstance(s, pymunk.Circle):
            return s.radius
    return 0


def merge_blobs(space, b1, b2):
    r1 = get_radius(b1)
    r2 = get_radius(b2)

    new_r = math.sqrt(r1 * r1 + r2 * r2)
    mass = new_r * 0.06
    inertia = pymunk.moment_for_circle(mass, 0, new_r)

    w = r1 + r2
    cx = (b1.position.x * r1 + b2.position.x * r2) / w
    cy = (b1.position.y * r1 + b2.position.y * r2) / w
    temp = (b1.temp * r1 + b2.temp * r2) / w
    vx = (b1.velocity.x * r1 + b2.velocity.x * r2) / w
    vy = (b1.velocity.y * r1 + b2.velocity.y * r2) / w

    for s in list(b1.shapes):
        space.remove(s)
    space.remove(b1)
    for s in list(b2.shapes):
        space.remove(s)
    space.remove(b2)

    body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
    body.position = (cx, cy)
    body.velocity = (vx, vy)
    body.temp = temp
    body.lateral_phase = getattr(b1, "lateral_phase", 0)
    body.lateral_speed = getattr(b1, "lateral_speed", 0.5)
    body.lateral_amp = min(getattr(b1, "lateral_amp", 15) * 1.2, 40)
    body.trail_len = 5
    body.velocity_func = _lava_velocity_update

    shape = pymunk.Circle(body, new_r)
    shape.elasticity = 0.02
    shape.friction = 0.02
    shape.is_dynamic = True
    shape.filter = BLOB_FILTER

    space.add(body, shape)
    return body


def split_blob(space, rng, body):
    r = get_radius(body)
    if r == 0:
        return []

    new_r = math.sqrt(r * r / 2)
    mass = new_r * 0.06
    inertia = pymunk.moment_for_circle(mass, 0, new_r)

    perp_x = -body.velocity.y
    perp_y = body.velocity.x
    perp_len = math.hypot(perp_x, perp_y)
    if perp_len < 1:
        perp_x, perp_y = 1, 0
    else:
        perp_x /= perp_len
        perp_y /= perp_len
    offset = new_r * 0.8

    for s in list(body.shapes):
        space.remove(s)
    space.remove(body)

    results = []
    for sign in [-1, 1]:
        b = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
        b.position = (body.position.x + perp_x * offset * sign,
                      body.position.y + perp_y * offset * sign)
        b.velocity = (body.velocity.x + perp_x * 20 * sign,
                      body.velocity.y + perp_y * 20 * sign)
        b.temp = body.temp
        b.lateral_phase = (getattr(body, "lateral_phase", 0) + sign * 0.5)
        b.lateral_speed = (getattr(body, "lateral_speed", 0.5) * rng.uniform(0.8, 1.2))
        b.lateral_amp = (getattr(body, "lateral_amp", 15) * rng.uniform(0.8, 0.95))
        b.trail_len = 5
        b.velocity_func = _lava_velocity_update

        shape = pymunk.Circle(b, new_r)
        shape.elasticity = 0.02
        shape.friction = 0.02
        shape.is_dynamic = True
        shape.filter = BLOB_FILTER

        space.add(b, shape)
        results.append(b)
    return results


def get_blobs(space):
    return [b for b in space.bodies
            if b.body_type == pymunk.Body.DYNAMIC and hasattr(b, "temp")]
