import pymunk
import math
from core.entity import Entity

BLOB_FILTER = pymunk.ShapeFilter(group=1)

class LavaBlob(Entity):
    def __init__(self, rng, x=None, y=None, temp=None, radius=None, phase=None, speed=None, amp=None):
        radius = radius if radius else rng.randint(18, 40)
        mass = radius * 0.06
        inertia = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
        body.position = (
            x if x is not None else rng.randint(-120, 120),
            y if y is not None else rng.randint(-700, 700),
        )
        body.temp = temp if temp is not None else rng.uniform(0.2, 0.8)
        body.lateral_phase = phase if phase is not None else rng.uniform(0, 2 * math.pi)
        body.lateral_speed = speed if speed is not None else rng.uniform(0.2, 1.0)
        body.lateral_amp = amp if amp is not None else rng.uniform(5, 30)
        
        # Store dynamic physics parameters
        body.buoyancy_force = rng.uniform(280.0, 420.0)
        body.heat_rate = rng.uniform(0.5, 2.0)
        body.cool_rate = rng.uniform(0.4, 1.8)
        
        body.velocity_func = self._lava_velocity_update

        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.05
        shape.friction = 0.05
        shape.filter = BLOB_FILTER
        
        super().__init__(body, shape, color=(200, 80, 50), trail=True, trail_len=5)

    @staticmethod
    def _lava_velocity_update(body, gravity, damping, dt):
        y = body.position.y
        bottom_threshold = -300
        top_threshold = 300
        
        heat_rate = getattr(body, "heat_rate", 1.0)
        cool_rate = getattr(body, "cool_rate", 1.0)

        if y < bottom_threshold:
            target = 1.0
            rate = heat_rate
        elif y > top_threshold:
            target = 0.0
            rate = cool_rate
        else:
            t = (y - bottom_threshold) / (top_threshold - bottom_threshold)
            target = 1.0 - t
            rate = (heat_rate + cool_rate) / 2.0

        body.temp += (target - body.temp) * rate * dt
        body.temp = max(0.0, min(1.0, body.temp))

        buoyancy_force = getattr(body, "buoyancy_force", 320.0)
        buoyancy = body.temp * buoyancy_force
        body.velocity = (body.velocity.x, body.velocity.y + buoyancy * dt)

        # Speed limits
        max_up, max_down = 150, -100
        if body.velocity.y > max_up:
            body.velocity = (body.velocity.x, max_up)
        if body.velocity.y < max_down:
            body.velocity = (body.velocity.x, max_down)

        # Lateral drift
        body.lateral_phase += body.lateral_speed * dt
        amp = body.lateral_amp * (0.2 + 0.8 * body.temp)
        drift_x = math.sin(body.lateral_phase) * amp * dt
        body.velocity = (body.velocity.x + drift_x, body.velocity.y)

        pymunk.Body.update_velocity(body, gravity, damping, dt)

    @property
    def radius(self):
        return self.shape.radius

def merge_blobs(space, b1, b2):
    r1 = list(b1.shapes)[0].radius
    r2 = list(b2.shapes)[0].radius

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

    new_blob = LavaBlob.__new__(LavaBlob)
    body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
    body.position = (cx, cy)
    body.velocity = (vx, vy)
    body.temp = temp
    body.lateral_phase = getattr(b1, "lateral_phase", 0)
    body.lateral_speed = getattr(b1, "lateral_speed", 0.5)
    body.lateral_amp = min(getattr(b1, "lateral_amp", 15) * 1.2, 40)
    body.velocity_func = LavaBlob._lava_velocity_update

    shape = pymunk.Circle(body, new_r)
    shape.elasticity, shape.friction, shape.filter = 0.02, 0.02, BLOB_FILTER
    space.add(body, shape)
    
    # Manually initialize the Entity part of the object
    new_blob.body, new_blob.shape, new_blob.color = body, shape, (200, 80, 50)
    new_blob.trail, new_blob.trail_len, new_blob.trail_positions = True, 5, []
    
    return new_blob

def split_blob(space, rng, body):
    r = list(body.shapes)[0].radius
    new_r = math.sqrt(r * r / 2)
    mass = new_r * 0.06
    inertia = pymunk.moment_for_circle(mass, 0, new_r)

    perp_x, perp_y = -body.velocity.y, body.velocity.x
    perp_len = math.hypot(perp_x, perp_y)
    if perp_len < 1: perp_x, perp_y = 1, 0
    else: perp_x, perp_y = perp_x/perp_len, perp_y/perp_len
    
    offset = new_r * 0.8
    old_temp = body.temp
    old_vel = body.velocity
    old_pos = body.position

    for s in list(body.shapes):
        space.remove(s)
    space.remove(body)

    results = []
    for sign in [-1, 1]:
        nb = LavaBlob(rng, 
                      x=old_pos.x + perp_x * offset * sign,
                      y=old_pos.y + perp_y * offset * sign,
                      temp=old_temp,
                      radius=new_r)
        nb.body.velocity = (old_vel.x + perp_x * 20 * sign,
                            old_vel.y + perp_y * 20 * sign)
        nb.add_to_space(space)
        results.append(nb)
    return results

def get_blobs(space):
    return [b for b in space.bodies if b.body_type == pymunk.Body.DYNAMIC and hasattr(b, "temp")]
