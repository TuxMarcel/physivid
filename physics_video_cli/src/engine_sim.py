import pymunk
from src.engine_world import WorldGenerator
from src.engine_render import Renderer
from src.engine_audio import AudioSynthesizer
import os

class SimulationEngine:
    def __init__(self, seed, profile, resolution, output_dir, duration):
        self.wg = WorldGenerator(seed, profile)
        self.space = self.wg.generate()
        self.renderer = Renderer(resolution)
        self.audio = AudioSynthesizer(os.path.join(output_dir, "audio.wav"), duration, seed)
        self.output_dir = output_dir
        self.current_time = 0.0

        self.space.on_collision(post_solve=self._on_collision)

    def _on_collision(self, arbiter, space, data):
        impulse = arbiter.total_impulse.length
        if impulse > 10.0:
            self.audio.play_collision_sound(self.current_time, impulse)

    def run(self, duration, fps):
        num_frames = int(duration * fps)
        dt = 1.0 / fps

        for frame in range(num_frames):
            self.current_time = frame * dt
            self.wg.update(frame, dt)

            self.space.step(dt)
            self.renderer.render(self.space, frame, self.output_dir)

        self.audio.write_to_file()
