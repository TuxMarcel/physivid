import pymunk
import math
from src.scenes.scene_base import BaseScene

class DNAHelixScene(BaseScene):
    def setup(self):
        self.space.gravity = (0, -600)
        self.balls = []
        
        # Seed-driven helix parameters
        self.helix_radius = self.rng.uniform(150, 250)
        self.twist_factor = self.rng.uniform(0.005, 0.015)
        self.rotation_speed = self.rng.uniform(0.5, 1.5)
        self.num_base_pairs = self.rng.randint(20, 35)
        self.vertical_spacing = 1600 / self.num_base_pairs
        
        self._build_helix()

    def _build_helix(self):
        # We create the helix as a series of static or kinematic objects
        # For simplicity and performance, we'll use static shapes that we rotate in update
        self.helix_bodies = []
        
        for i in range(self.num_base_pairs):
            y = -800 + i * self.vertical_spacing
            angle = i * self.twist_factor * 100
            
            # Strand 1
            b1 = self._add_node(angle, y, self.palette[0])
            # Strand 2 (180 degrees offset)
            b2 = self._add_node(angle + math.pi, y, self.palette[1])
            
            # Cross-bar
            self._add_bar(b1, b2, self.palette[2] if len(self.palette) > 2 else (200, 200, 200))
            
            self.helix_bodies.append((b1, b2, angle, y))

    def _add_node(self, angle, y, color):
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        x = math.cos(angle) * self.helix_radius
        body.position = (x, y)
        
        shape = pymunk.Circle(body, 25)
        shape.elasticity = 0.8
        shape.friction = 0.5
        shape.color = color
        shape.is_dynamic = False
        
        self.space.add(body, shape)
        return body

    def _add_bar(self, b1, b2, color):
        # We don't need a physical bar, just the nodes for collision
        # But we could add a segment if we want more collisions
        shape = pymunk.Segment(self.space.static_body, b1.position, b2.position, 8)
        shape.elasticity = 0.5
        shape.friction = 0.5
        shape.color = color
        shape.is_dynamic = False
        # Note: Static segments don't move, so we'll need to update them in update()
        # Actually, let's just use the nodes for now to keep it clean.
        pass

    def update(self, frame, dt):
        current_rotation = frame * dt * self.rotation_speed
        
        # Rotate the helix nodes
        for b1, b2, base_angle, y in self.helix_bodies:
            angle = base_angle + current_rotation
            
            b1.position = (math.cos(angle) * self.helix_radius, y)
            b2.position = (math.cos(angle + math.pi) * self.helix_radius, y)
            
        # Spawn balls at the top
        if frame % 40 == 0:
            self._spawn_ball()
            
        # Cleanup balls
        for ball in list(self.balls):
            if ball.position.y < -1000:
                self.space.remove(ball, *ball.shapes)
                self.balls.remove(ball)

    def _spawn_ball(self):
        mass = 1
        radius = 15
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, inertia)
        
        x = self.rng.uniform(-100, 100)
        body.position = (x, 900)
        body.velocity = (self.rng.uniform(-50, 50), -100)
        body.trail_len = 10
        
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.7
        shape.friction = 0.3
        shape.color = self.rng.choice(self.palette)
        shape.is_dynamic = True
        
        self.space.add(body, shape)
        self.balls.append(body)
