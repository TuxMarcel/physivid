import pymunk
import math
from src.entities.base import BaseEntity

class Ball(BaseEntity):
    def __init__(self, space, rng, position, color, radius=15):
        super().__init__(space, rng)
        mass = 1.0
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, inertia)
        self.body.position = position
        self.body.trail_len = 10
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.7
        self.shape.friction = 0.3
        self.shape.color = color
        self.shape.is_dynamic = True
        
        self.shapes.append(self.shape)
        self.space.add(self.body, self.shape)

class Peg(BaseEntity):
    def __init__(self, space, rng, position, radius):
        super().__init__(space, rng)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.9
        self.shape.friction = 0.1
        self.shape.color = (100, 115, 135)
        self.shape.is_dynamic = False
        
        self.shapes.append(self.shape)
        self.space.add(self.body, self.shape)

class Spinner(BaseEntity):
    def __init__(self, space, rng, position, arm_length, num_arms, motor_speed):
        super().__init__(space, rng)
        self.body = pymunk.Body(10, 1000)
        self.body.position = position
        
        for i in range(num_arms):
            angle = i * (2 * math.pi / num_arms)
            a = (0, 0)
            b = (math.cos(angle) * arm_length, math.sin(angle) * arm_length)
            seg = pymunk.Segment(self.body, a, b, 6)
            seg.elasticity = 0.8
            seg.friction = 0.2
            seg.color = (80, 100, 120)
            self.shapes.append(seg)
        
        # Motor
        self.pivot = pymunk.PivotJoint(space.static_body, self.body, position)
        self.motor = pymunk.SimpleMotor(space.static_body, self.body, motor_speed)
        
        self.space.add(self.body, *self.shapes, self.pivot, self.motor)
