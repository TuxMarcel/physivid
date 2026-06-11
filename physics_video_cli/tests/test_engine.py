import unittest
import pymunk
import os
import shutil
from src.engine_world import WorldGenerator
from src.engine_sim import SimulationEngine
from src.engine_audio import AudioSynthesizer

class TestEngineDeterminism(unittest.TestCase):
    def test_world_generator_determinism(self):
        """
        Verify that WorldGenerator produces identical starting states for the same seed.
        """
        seed = 42
        profile = "ball_pit"
        
        wg1 = WorldGenerator(seed, profile)
        space1 = wg1.generate()
        
        wg2 = WorldGenerator(seed, profile)
        space2 = wg2.generate()
        
        self.assertEqual(len(space1.bodies), len(space2.bodies))
        self.assertEqual(len(space1.shapes), len(space2.shapes))
        
        # Check that starting positions match exactly
        for b1, b2 in zip(space1.bodies, space2.bodies):
            self.assertAlmostEqual(b1.position.x, b2.position.x, places=5)
            self.assertAlmostEqual(b1.position.y, b2.position.y, places=5)
            self.assertAlmostEqual(b1.angle, b2.angle, places=5)

    def test_simulation_determinism(self):
        """
        Verify that running the simulation twice with the same seed results in the exact same state.
        """
        seed = 99
        profile = "lava_lamp"
        temp_dir1 = "temp_test_1"
        temp_dir2 = "temp_test_2"
        
        os.makedirs(temp_dir1, exist_ok=True)
        os.makedirs(temp_dir2, exist_ok=True)
        
        try:
            engine1 = SimulationEngine(seed, profile, "640x480", temp_dir1, duration=1.0)
            engine1.run(duration=1.0, fps=10)
            
            engine2 = SimulationEngine(seed, profile, "640x480", temp_dir2, duration=1.0)
            engine2.run(duration=1.0, fps=10)
            
            # Verify body positions at the end of simulation
            for b1, b2 in zip(engine1.space.bodies, engine2.space.bodies):
                self.assertAlmostEqual(b1.position.x, b2.position.x, places=5)
                self.assertAlmostEqual(b1.position.y, b2.position.y, places=5)
                self.assertAlmostEqual(b1.angle, b2.angle, places=5)
                
            # Verify that both audio buffers are identical
            self.assertEqual(engine1.audio.buffer, engine2.audio.buffer)
            
        finally:
            if os.path.exists(temp_dir1):
                shutil.rmtree(temp_dir1)
            if os.path.exists(temp_dir2):
                shutil.rmtree(temp_dir2)

    def test_audio_sound_mixing(self):
        """
        Test that AudioSynthesizer successfully mixes sound into the buffer.
        """
        synth = AudioSynthesizer("dummy.wav", duration=1.0, seed=42, sample_rate=1000)
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
