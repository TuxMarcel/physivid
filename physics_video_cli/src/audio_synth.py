import wave
import struct
import math

class AudioSynthesizer:
    def __init__(self, output_path, duration, sample_rate=44100):
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.duration = duration
        self.total_samples = int(duration * sample_rate)
        # Pre-allocate buffer with zeros (floats to allow mixing without distortion)
        self.buffer = [0.0] * self.total_samples

    def play_collision_sound(self, t, impulse):
        """
        Synthesizes a percussive collision sound and mixes it into the audio buffer at time t.
        Higher impulses produce louder, deeper, and longer sounds.
        """
        # Map impulse to volume [0.02, 1.0]
        # Standard pymunk impulses can be large; clamp to standard scale
        volume = min(1.0, max(0.02, impulse / 800.0))
        
        # Map impulse to frequency (higher impulse = lower pitch)
        # Low impulse (e.g., 50) -> ~1000Hz (high-pitched ping)
        # High impulse (e.g., 1000) -> ~150Hz (low-pitched thud)
        freq = max(100.0, min(1200.0, 1000.0 - (impulse * 0.8)))
        
        # Decay duration based on impulse strength
        sound_duration = max(0.03, min(0.35, 0.05 + (impulse / 4000.0)))
        
        start_sample = int(t * self.sample_rate)
        num_samples = int(self.sample_rate * sound_duration)
        
        for i in range(num_samples):
            idx = start_sample + i
            if idx >= self.total_samples:
                break
            
            st = float(i) / self.sample_rate
            
            # Percussive envelope: rapid attack (exponential decay)
            envelope = math.exp(-8.0 * st / sound_duration)
            
            # Synthesize sound with a fundamental frequency and a subtle second harmonic
            fundamental = math.sin(2 * math.pi * freq * st)
            harmonic = 0.25 * math.sin(4 * math.pi * freq * st)
            
            sample_value = (fundamental + harmonic) * envelope * volume
            
            # Mix (add) into the buffer
            self.buffer[idx] += sample_value

    def write_to_file(self):
        """
        Converts the float buffer to 16-bit PCM WAV format, applying clamping to prevent clipping.
        """
        with wave.open(self.output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            
            for sample in self.buffer:
                # Clamp sample to [-1.0, 1.0] to prevent clipping/distortion
                clamped = max(-1.0, min(1.0, sample))
                int_sample = int(clamped * 32767)
                wav_file.writeframes(struct.pack('h', int_sample))
