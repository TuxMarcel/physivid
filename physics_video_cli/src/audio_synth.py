import wave
import struct
import math
import random


class SoundProfile:
    """
    Seed-driven sound profile: each video has a unique sonic character.
    Generated once per simulation run from the seed.
    """
    def __init__(self, seed):
        rng = random.Random(seed ^ 0xDEADBEEF)  # XOR to avoid same RNG state as world

        # Frequency range: maps impulse to pitch
        self.freq_min = rng.uniform(60.0, 200.0)    # lowest possible tone
        self.freq_max = rng.uniform(800.0, 2200.0)  # highest possible tone

        # Decay: how fast the sound fades
        self.decay_fast = rng.uniform(5.0, 14.0)

        # Harmonic content: 2nd and 3rd harmonic blend
        self.h2_ratio = rng.uniform(0.0, 0.45)
        self.h3_ratio = rng.uniform(0.0, 0.25)

        # Duration range (in seconds)
        self.dur_min = rng.uniform(0.02, 0.07)
        self.dur_max = rng.uniform(0.12, 0.45)

        # Waveform mix: blend between sine (smooth) and sawtooth (harsh/bright)
        self.saw_mix = rng.uniform(0.0, 0.6)

        # Global volume scale
        self.volume_scale = rng.uniform(0.55, 1.0)


class AudioSynthesizer:
    def __init__(self, output_path, duration, seed, sample_rate=44100):
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.duration = duration
        self.total_samples = int(duration * sample_rate)
        self.buffer = [0.0] * self.total_samples

        # Unique sound profile derived from the seed
        self.profile = SoundProfile(seed)

    def play_collision_sound(self, t, impulse):
        """
        Synthesizes a collision sound at time t with the session's sound profile.
        Impulse controls volume and pitch.
        """
        if impulse < 8.0:
            return

        p = self.profile

        # Map impulse → volume
        volume = min(1.0, max(0.02, impulse / 700.0)) * p.volume_scale

        # Map impulse → frequency (inverse: bigger hit = lower pitch)
        freq_range = p.freq_max - p.freq_min
        freq = p.freq_max - min(1.0, impulse / 1000.0) * freq_range

        # Map impulse → sound duration
        dur_range = p.dur_max - p.dur_min
        sound_duration = p.dur_min + min(1.0, impulse / 900.0) * dur_range

        start_sample = int(t * self.sample_rate)
        num_samples = int(self.sample_rate * sound_duration)

        for i in range(num_samples):
            idx = start_sample + i
            if idx >= self.total_samples:
                break

            st = float(i) / self.sample_rate
            phase = 2.0 * math.pi * freq * st

            # Envelope: exponential decay
            envelope = math.exp(-p.decay_fast * st / sound_duration)

            # Sine wave (fundamental)
            sine = math.sin(phase)

            # Sawtooth wave (bright/metallic)
            saw = 2.0 * ((freq * st) % 1.0) - 1.0

            # Blend sine and saw
            wave = (1.0 - p.saw_mix) * sine + p.saw_mix * saw

            # Add harmonics
            if p.h2_ratio > 0.01:
                wave += p.h2_ratio * math.sin(2.0 * phase)
            if p.h3_ratio > 0.01:
                wave += p.h3_ratio * math.sin(3.0 * phase)

            # Normalize to account for harmonic addition
            norm = 1.0 + p.h2_ratio + p.h3_ratio
            sample_value = (wave / norm) * envelope * volume

            # Mix into buffer
            self.buffer[idx] += sample_value

    def write_to_file(self):
        """
        Writes the float buffer to a 16-bit PCM WAV file, clamping to avoid clipping.
        """
        with wave.open(self.output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)

            for sample in self.buffer:
                clamped = max(-1.0, min(1.0, sample))
                int_sample = int(clamped * 32767)
                wav_file.writeframes(struct.pack('h', int_sample))
