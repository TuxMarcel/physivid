import unittest
import pymunk
import os
import shutil
import random
from core.registry import get, list_all
import main
from audio.synthesizer import Synthesizer

class TestEngineDeterminism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Discover experiments so they are registered
        main._discover()

    def test_world_generator_determinism(self):
        """
        Verify that setting up the experiment twice with the same seed produces identical starting states.
        """
        seed = 42
        profile = "ball_pit"
        
        exp_cls = get(profile)
        exp1 = exp_cls(seed)
        exp1.setup()
        
        exp2 = exp_cls(seed)
        exp2.setup()
        
        self.assertEqual(len(exp1.space.bodies), len(exp2.space.bodies))
        self.assertEqual(len(exp1.space.shapes), len(exp2.space.shapes))
        
        for b1, b2 in zip(exp1.space.bodies, exp2.space.bodies):
            self.assertAlmostEqual(b1.position.x, b2.position.x, places=5)
            self.assertAlmostEqual(b1.position.y, b2.position.y, places=5)
            self.assertAlmostEqual(b1.angle, b2.angle, places=5)

    def test_simulation_determinism(self):
        """
        Verify that running the simulation step-by-step results in identical state and audio buffers.
        """
        seed = 99
        profile = "lava_lamp"
        duration = 1.0
        fps = 10
        dt = 1.0 / fps
        num_frames = int(duration * fps)
        
        # Run first simulation
        exp1 = get(profile)(seed)
        exp1.setup()
        synth1 = Synthesizer(44100, seed, duration)
        
        def collision_hook1(arbiter, space, data):
            exp1.handle_collisions(arbiter, synth1.time, synth1)
        exp1.space.on_collision(post_solve=collision_hook1)
        
        for frame in range(num_frames):
            current_time = frame * dt
            synth1.time = current_time
            exp1.pre_step(dt)
            exp1.space.step(dt)
            exp1.post_step(dt)
            
        # Run second simulation
        exp2 = get(profile)(seed)
        exp2.setup()
        synth2 = Synthesizer(44100, seed, duration)
        
        def collision_hook2(arbiter, space, data):
            exp2.handle_collisions(arbiter, synth2.time, synth2)
        exp2.space.on_collision(post_solve=collision_hook2)
        
        for frame in range(num_frames):
            current_time = frame * dt
            synth2.time = current_time
            exp2.pre_step(dt)
            exp2.space.step(dt)
            exp2.post_step(dt)
            
        # Verify body positions at the end of simulation
        for b1, b2 in zip(exp1.space.bodies, exp2.space.bodies):
            self.assertAlmostEqual(b1.position.x, b2.position.x, places=5)
            self.assertAlmostEqual(b1.position.y, b2.position.y, places=5)
            self.assertAlmostEqual(b1.angle, b2.angle, places=5)
            
        # Verify that both audio buffers are identical
        self.assertEqual(synth1.buffer, synth2.buffer)

    def test_audio_sound_mixing(self):
        """
        Test that Synthesizer successfully mixes sound into the buffer.
        """
        synth = Synthesizer(sample_rate=1000, seed=42, duration=1.0)
        self.assertEqual(sum(synth.buffer), 0.0)
        
        # Synthesize a sound at t=0.5
        synth.play_collision_sound(0.5, impulse=500.0)
        
        # Verify that the buffer is no longer completely silent
        self.assertNotEqual(sum(synth.buffer), 0.0)
        
        # Verify that samples before t=0.5 are still zero
        start_idx = int(0.5 * 1000)
        self.assertEqual(sum(synth.buffer[:start_idx]), 0.0)
        self.assertNotEqual(sum(synth.buffer[start_idx:]), 0.0)

if __name__ == "__main__":
    unittest.main()
