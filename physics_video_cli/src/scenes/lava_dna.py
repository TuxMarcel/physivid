import pymunk
from src.scenes.base_scene import BaseScene

class LavaDNAScene(BaseScene):
    def setup(self):
        # 1. Container Boundaries (Fitted to 1080x1920 space)
        floor = pymunk.Segment(self.space.static_body, (-520, -920), (520, -920), 20)
        ceiling = pymunk.Segment(self.space.static_body, (-520, 920), (520, 920), 20)
        wall_l = pymunk.Segment(self.space.static_body, (-520, -920), (-520, 920), 20)
        wall_r = pymunk.Segment(self.space.static_body, (520, -920), (520, 920), 20)
        
        for wall in [floor, ceiling, wall_l, wall_r]:
            wall.elasticity = 0.9
            wall.friction = 0.1
            wall.color = (40, 45, 60)
            wall.is_dynamic = False
            self.space.add(wall)

        # 2. Large Static Deflectors (bubbles flow around them)
        deflector_positions = [
            (0, 400), (-250, 100), (250, 100), 
            (-150, -200), (150, -200), (0, -450)
        ]
        for pos in deflector_positions:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = pos
            radius = self.rng.randint(60, 90)
            shape = pymunk.Circle(body, radius)
            shape.elasticity = 0.9
            shape.friction = 0.1
            shape.color = (65, 75, 95)
            shape.is_dynamic = False
            self.space.add(body, shape)

        # 3. Dynamic Lava Blobs (30 bubbles)
        for _ in range(30):
            radius = self.rng.randint(25, 50)
            mass = radius * 0.05
            inertia = pymunk.moment_for_circle(mass, 0, radius)
            
            body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
            body.position = (self.rng.randint(-400, 400), self.rng.randint(-750, 750))
            
            # Custom state properties
            body.warm = self.rng.choice([True, False])
            body.velocity_func = self.lava_velocity_update
            
            shape = pymunk.Circle(body, radius)
            shape.elasticity = 0.8
            shape.friction = 0.1
            shape.is_dynamic = True
            shape.color = (255, 0, 128) if body.warm else (0, 128, 255)
            
            self.space.add(body, shape)

    def lava_velocity_update(self, body, gravity, damping, dt):
        y = body.position.y
        
        # Thermoregulation simulation: warm bubbles rise, cool bubbles sink
        if body.warm:
            buoyancy = 380.0
            body.velocity = (body.velocity.x, body.velocity.y + buoyancy * dt)
            if y > 780:
                body.warm = False
        else:
            sinking = -380.0
            body.velocity = (body.velocity.x, body.velocity.y + sinking * dt)
            if y < -780:
                body.warm = True
        
        # Lateral organic drift
        drift_x = self.rng.uniform(-80, 80)
        body.velocity = (body.velocity.x + drift_x * dt, body.velocity.y)
        
        # Apply velocity and standard damping
        pymunk.Body.update_velocity(body, (0, 0), damping, dt)
