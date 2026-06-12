import math
import pymunk
from core.entity import Entity

class CircleEntity(Entity):
    def __init__(self, x: float, y: float, radius: float, mass: float = 1.0, color: tuple = (255, 255, 255), is_static: bool = False, trail: bool = False, trail_len: int = 10):
        if is_static:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (x, y)
            shape = pymunk.Circle(body, radius)
        else:
            inertia = pymunk.moment_for_circle(mass, 0, radius)
            body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
            body.position = (x, y)
            shape = pymunk.Circle(body, radius)
            shape.elasticity = 0.7
            shape.friction = 0.3
            
        super().__init__(body, shape, color, trail, trail_len)

class PolygonEntity(Entity):
    def __init__(self, x: float, y: float, num_sides: int, radius: float, mass: float = 1.0, color: tuple = (255, 255, 255), is_static: bool = False, trail: bool = False, trail_len: int = 10):
        vertices = []
        for i in range(num_sides):
            angle = i * 2 * math.pi / num_sides
            vertices.append((radius * math.cos(angle), radius * math.sin(angle)))
            
        if is_static:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (x, y)
            shape = pymunk.Poly(body, vertices)
        else:
            inertia = pymunk.moment_for_poly(mass, vertices)
            body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
            body.position = (x, y)
            shape = pymunk.Poly(body, vertices)
            shape.elasticity = 0.7
            shape.friction = 0.3
            
        super().__init__(body, shape, color, trail, trail_len)

class SegmentEntity(Entity):
    def __init__(self, a: tuple, b: tuple, radius: float = 10.0, color: tuple = (255, 255, 255)):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, a, b, radius)
        shape.elasticity = 0.5
        shape.friction = 0.5
        super().__init__(body, shape, color, trail=False)
