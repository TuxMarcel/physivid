import pymunk
import random
import math
from src.scenes.base import BaseScene
from src.entities.ball_pit_entities import Ball, Peg, Spinner
from src.audio_profiles.impact_profile import ImpactProfile

class BallPitScene(BaseScene):
    def __init__(self, space, rng, palette, seed):
        super().__init__(space, rng, palette)
        self.audio_profile = ImpactProfile(seed)
        self.balls = []
        self.spinners = []

    def setup(self):
        # Szene setzt ihre eigene Gravity
        self.space.gravity = (0, -900)
        
        # Seed-basierte Layout-Wahl
        layout_choice = self.rng.randint(0, 2)
        if layout_choice == 0:
            print("[DEBUG] Wähle Layout: Classic Plinko")
            self._build_classic_plinko()
        elif layout_choice == 1:
            print("[DEBUG] Wähle Layout: Asymmetric Chaos")
            self._build_asymmetric_chaos()
        else:
            print("[DEBUG] Wähle Layout: Funnel Layout")
            self._build_funnel_layout()

    def _build_classic_plinko(self):
        # Wände
        self._add_wall((-500, -800), (-500, 800))
        self._add_wall((500, -800), (500, 800))
        # Pegs in einem Grid
        for r in range(8):
            y = 600 - r * 150
            pegs = 6 if r % 2 == 0 else 5
            spacing = 800 / (pegs + 1)
            for i in range(pegs):
                x = -400 + spacing * (i + 1)
                Peg(self.space, self.rng, (x, y), self.rng.randint(10, 16))

    def _build_asymmetric_chaos(self):
        # Strukturierte Asymmetrie: 'Spiral-Flow' Design
        self._add_wall((-400, -900), (-400, 900))
        self._add_wall((400, -900), (400, 900))
        
        # Spirale von Pegs erzeugen, um den Flow zu leiten
        for i in range(50):
            angle = i * 0.5
            dist = i * 6
            x = math.cos(angle) * dist
            y = math.sin(angle) * dist
            # Nur innerhalb der Wände
            if -350 < x < 350:
                Peg(self.space, self.rng, (x, y), self.rng.randint(8, 14))
                
        # Spinner als "Bottlenecks" strategisch platzieren
        spinner_positions = [(-200, 400), (200, 0), (-200, -400)]
        for pos in spinner_positions:
            Spinner(self.space, self.rng, pos, 80, 4, self.rng.uniform(2, 4))

    def _build_funnel_layout(self):
        # Trichter-Form
        self._add_wall((-450, 800), (-100, -800))  #linke wand
        self._add_wall((450, 800), (100, -800))   #rechte wand
        # Pegs unten
        for _ in range(20):
            x = self.rng.uniform(-300, 300)
            y = self.rng.uniform(-800, +400)
            Peg(self.space, self.rng, (x, y), 15)

    def _add_wall(self, a, b):
        seg = pymunk.Segment(self.space.static_body, a, b, 10)
        seg.elasticity = 0.5
        seg.friction = 0.5
        seg.color = (58, 70, 88)
        self.space.add(seg)

    def update(self, frame, dt):
        # Recycling / Respawning
        for ball in list(self.balls):
            if ball.body.position.y < -950:
                # Oben neu spawnen
                x = self.rng.uniform(-100, 100)
                ball.body.position = (x, 950)
                ball.body.velocity = (self.rng.uniform(-50, 50), -100)
            
        if frame % 40 == 0 and len(self.balls) < 20:
            x = self.rng.uniform(-100, 100)
            ball = Ball(self.space, self.rng, (x, 850), self.rng.choice(self.palette))
            self.balls.append(ball)

    def get_impulse_threshold(self):
        return 12.0

    def handle_collisions(self, arbiter, current_time, audio_engine):
        """Behandelt Kollisionen: Nur Sounds bei Ball-Kollisionen."""
        # Prüfen, ob einer der Kollisionspartner ein Ball ist (hat trail_len)
        shapes = arbiter.shapes
        is_ball_collision = any(hasattr(shape.body, 'trail_len') for shape in shapes)
        
        if not is_ball_collision:
            return

        impulse = arbiter.total_impulse.length
        if impulse > self.get_impulse_threshold():
            params = self.audio_profile.get_params(impulse)
            audio_engine.play_sound(current_time, params)
