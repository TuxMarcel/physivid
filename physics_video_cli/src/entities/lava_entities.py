import pymunk
import math
from src.entities.base import BaseEntity

BLOB_FILTER = pymunk.ShapeFilter(group=1)

class LavaBlob(BaseEntity):
    def __init__(self, space, rng, position=None, radius=None, temp=None):
        super().__init__(space, rng)
        radius = radius if radius else rng.randint(18, 40)
        mass = radius * 0.06
        inertia = pymunk.moment_for_circle(mass, 0, radius)

        self.body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
        self.body.position = position if position else (rng.randint(-120, 120), rng.randint(-700, 700))
        
        # Physik-Parameter
        self.body.temp = temp if temp is not None else rng.uniform(0.2, 0.8)
        self.body.lateral_phase = rng.uniform(0, 2 * math.pi)
        self.body.lateral_speed = rng.uniform(0.2, 1.0)
        self.body.lateral_amp = rng.uniform(5, 30)
        self.body.buoyancy_force = rng.uniform(280.0, 420.0)
        self.body.heat_rate = rng.uniform(0.5, 2.0)
        self.body.cool_rate = rng.uniform(0.4, 1.8)
        self.body.trail_len = 5
        
        self.body.velocity_func = self._velocity_update

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.05
        self.shape.friction = 0.05
        self.shape.is_dynamic = True
        self.shape.filter = BLOB_FILTER

        self.shapes.append(self.shape)
        self.space.add(self.body, self.shape)

    @property
    def radius(self):
        return self.shape.radius

    def _velocity_update(self, body, gravity, damping, dt):
        y = body.position.y
        bottom_threshold = -300
        top_threshold = 300

        if y < bottom_threshold:
            target, rate = 1.0, body.heat_rate
        elif y > top_threshold:
            target, rate = 0.0, body.cool_rate
        else:
            t = (y - bottom_threshold) / (top_threshold - bottom_threshold)
            target, rate = 1.0 - t, (body.heat_rate + body.cool_rate) / 2.0

        body.temp += (target - body.temp) * rate * dt
        body.temp = max(0.0, min(1.0, body.temp))

        buoyancy = body.temp * body.buoyancy_force
        body.velocity = (body.velocity.x, body.velocity.y + buoyancy * dt)

        # Speed limits
        if body.velocity.y > 150: body.velocity = (body.velocity.x, 150)
        if body.velocity.y < -100: body.velocity = (body.velocity.x, -100)

        # Lateral drift
        body.lateral_phase += body.lateral_speed * dt
        amp = body.lateral_amp * (0.2 + 0.8 * body.temp)
        drift_x = math.sin(body.lateral_phase) * amp * dt
        body.velocity = (body.velocity.x + drift_x, body.velocity.y)

        pymunk.Body.update_velocity(body, gravity, damping, dt)
