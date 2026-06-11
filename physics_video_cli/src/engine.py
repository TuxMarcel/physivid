import pymunk
from src.world_generator import WorldGenerator
from src.renderer import Renderer
from src.audio_synth import AudioSynthesizer
import os

class SimulationEngine:
    def __init__(self, seed, profile, resolution, output_dir, duration):
        self.wg = WorldGenerator(seed, profile)
        self.space = self.wg.generate()
        self.renderer = Renderer(resolution)
        self.audio = AudioSynthesizer(os.path.join(output_dir, "audio.wav"), duration, seed)
        self.output_dir = output_dir
        self.current_time = 0.0
        
        # Register collision callback for all shapes
        self.space.on_collision(post_solve=self._on_collision)

    def _on_collision(self, arbiter, space, data):
        # Determine the strength of collision from total impulse applied
        impulse = arbiter.total_impulse.length
        # Only play sound if it's a significant collision to avoid noisy hiss
        if impulse > 10.0:
            self.audio.play_collision_sound(self.current_time, impulse)

    def run(self, duration, fps):
        num_frames = int(duration * fps)
        dt = 1.0 / fps
        
        for frame in range(num_frames):
            self.current_time = frame * dt
            # Delegate scene-specific updates (like spawning) to the WorldGenerator
            self.wg.update(frame, dt)
            
            self.space.step(dt)
            self.renderer.render(self.space, frame, self.output_dir)
        
        self.audio.write_to_file()
