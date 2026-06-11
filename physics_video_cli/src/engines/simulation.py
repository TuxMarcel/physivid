import pymunk
from src.engines.audio import AudioEngine
from src.engines.rendering import RenderingEngine

class SimulationEngine:
    """Der generische Runner für die Physik-Simulation."""
    def __init__(self, scene, audio_engine, rendering_engine):
        self.scene = scene
        self.audio_engine = audio_engine
        self.rendering_engine = rendering_engine
        self.space = scene.space
        self.current_time = 0.0

        # Kollisions-Hook registrieren
        self.space.on_collision(post_solve=self._on_collision)

    def _on_collision(self, arbiter, space, data):
        # Delegiert die Kollision an die Szene
        self.scene.handle_collisions(arbiter, self.current_time, self.audio_engine)

    def run(self, duration, fps, output_dir):
        num_frames = int(duration * fps)
        dt = 1.0 / fps

        for frame in range(num_frames):
            self.current_time = frame * dt
            
            # Szenen-Update (Spawning, etc.)
            self.scene.update(frame, dt)

            # Physik-Schritt
            self.space.step(dt)
            
            # Rendering
            self.rendering_engine.render(self.space, frame, output_dir)

        # Audio finalisieren
        self.audio_engine.write_to_file()
