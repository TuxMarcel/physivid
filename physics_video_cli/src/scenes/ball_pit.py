import pymunk
import math
from src.scenes.base_scene import BaseScene

class BallPitScene(BaseScene):
    def setup(self):
        # Side walls (ending at y=-600 to transition into the bottom funnel)
        wall_l = pymunk.Segment(self.space.static_body, (-520, -600), (-520, 920), 15)
        wall_r = pymunk.Segment(self.space.static_body, (520, -600), (520, 920), 15)
        
        # Bottom funnel guides leading to a central escape hole
        bottom_funnel_l = pymunk.Segment(self.space.static_body, (-520, -600), (-100, -920), 15)
        bottom_funnel_r = pymunk.Segment(self.space.static_body, (520, -600), (100, -920), 15)
        
        # Top funnel guides at the top to channel balls
        funnel_l = pymunk.Segment(self.space.static_body, (-520, 920), (-200, 800), 15)
        funnel_r = pymunk.Segment(self.space.static_body, (520, 920), (200, 800), 15)
        
        for wall in [wall_l, wall_r, bottom_funnel_l, bottom_funnel_r, funnel_l, funnel_r]:
            wall.elasticity = 0.8
            wall.friction = 0.3
            wall.color = (60, 70, 85)
            wall.is_dynamic = False
            self.space.add(wall)
            
        # 2. Static Obstacles (Plinko-style peg board)
        rows = 7
        for r in range(rows):
            y = 600 - r * 160
            pegs_in_row = 6 if r % 2 == 0 else 5
            x_spacing = 800 / (pegs_in_row + 1)
            
            for i in range(pegs_in_row):
                x = -400 + x_spacing * (i + 1)
                # Deterministic offset based on seed
                x += self.rng.uniform(-15, 15)
                y_offset = self.rng.uniform(-10, 10)
                
                peg_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                peg_body.position = (x, y + y_offset)
                
                peg_shape = pymunk.Circle(peg_body, 12)
                peg_shape.elasticity = 0.95
                peg_shape.friction = 0.1
                peg_shape.color = (130, 145, 165)
                peg_shape.is_dynamic = False
                
                self.space.add(peg_body, peg_shape)

        # 3. Rotating Kinematic Spinners
        spinner_positions = [(-200, -350), (200, -350)]
        self.spinners = []
        
        for idx, pos in enumerate(spinner_positions):
            body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            body.position = pos
            body.angular_velocity = -1.5 if idx == 0 else 1.5
            self.space.add(body)
            self.spinners.append(body)
            
            for angle in [0, math.pi / 2]:
                length = 120
                dx = length * math.cos(angle)
                dy = length * math.sin(angle)
                shape = pymunk.Segment(body, (-dx, -dy), (dx, dy), 10)
                shape.elasticity = 0.7
                shape.friction = 0.2
                shape.color = (180, 110, 50)
                shape.is_dynamic = False
                self.space.add(shape)

        # Spawn a few initial balls to start the simulation with action
        for _ in range(12):
            self.spawn_ball(initial=True)

    def spawn_ball(self, initial=False):
        radius = self.rng.randint(15, 25)
        mass = 1.0
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        
        body = pymunk.Body(mass, inertia, body_type=pymunk.Body.DYNAMIC)
        
        if initial:
            # Random position anywhere in the middle-top area
            body.position = (self.rng.randint(-300, 300), self.rng.randint(200, 750))
        else:
            # Spawn at the funnel mouth
            spawn_x = self.rng.randint(-150, 150)
            body.position = (spawn_x, 850)
            body.velocity = (self.rng.uniform(-50, 50), -200)
        
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.6
        shape.friction = 0.2
        shape.color = self.rng.choice(self.palette)
        shape.is_dynamic = True
        
        self.space.add(body, shape)

    def update(self, frame, dt):
        # 1. Teleport balls that fall through the bottom hole back to the top
        for body in list(self.space.bodies):
            if body.body_type == pymunk.Body.DYNAMIC:
                if body.position.y < -950:
                    spawn_x = self.rng.randint(-150, 150)
                    body.position = (spawn_x, 850)
                    body.velocity = (self.rng.uniform(-30, 30), -150)
                    body.angular_velocity = 0.0

        # 2. Continuous spawning up to a maximum of 35 balls
        dynamic_balls = [b for b in self.space.bodies if b.body_type == pymunk.Body.DYNAMIC]
        if len(dynamic_balls) < 35 and frame > 0 and frame % 40 == 0:
            self.spawn_ball(initial=False)
