import wave
import struct
import math
import random


class SoundProfile:
    def __init__(self, seed):
        rng = random.Random(seed ^ 0xAC0057C)

        self.material = rng.randint(0, 2)

        if self.material == 0:
            self.body_freq_min   = rng.uniform(1800.0, 2800.0)
            self.body_freq_max   = rng.uniform(3000.0, 4500.0)
            self.body_decay      = rng.uniform(18.0,  30.0)
            self.noise_level     = rng.uniform(0.05,  0.25)
            self.noise_dur_ms    = rng.uniform(2.0,   6.0)
            self.dur_min         = 0.012
            self.dur_max         = rng.uniform(0.04,  0.10)
            self.pitch_drop      = rng.uniform(0.02,  0.08)
            self.volume_scale    = rng.uniform(0.55,  0.90)

        elif self.material == 1:
            self.body_freq_min   = rng.uniform(180.0,  380.0)
            self.body_freq_max   = rng.uniform(450.0,  900.0)
            self.body_decay      = rng.uniform(8.0,   16.0)
            self.noise_level     = rng.uniform(0.35,   0.65)
            self.noise_dur_ms    = rng.uniform(6.0,   18.0)
            self.dur_min         = 0.030
            self.dur_max         = rng.uniform(0.10,   0.30)
            self.pitch_drop      = rng.uniform(0.08,   0.20)
            self.volume_scale    = rng.uniform(0.60,   1.00)

        else:
            self.body_freq_min   = rng.uniform(400.0,  750.0)
            self.body_freq_max   = rng.uniform(900.0, 1800.0)
            self.body_decay      = rng.uniform(10.0,  22.0)
            self.noise_level     = rng.uniform(0.15,   0.45)
            self.noise_dur_ms    = rng.uniform(4.0,   12.0)
            self.dur_min         = 0.020
            self.dur_max         = rng.uniform(0.07,   0.20)
            self.pitch_drop      = rng.uniform(0.05,   0.15)
            self.volume_scale    = rng.uniform(0.55,   0.90)

        self.inharmonicity = rng.uniform(1.003, 1.025)


class AudioSynthesizer:
    def __init__(self, output_path, duration, seed, sample_rate=44100):
        self.output_path   = output_path
        self.sample_rate   = sample_rate
        self.duration      = duration
        self.total_samples = int(duration * sample_rate)
        self.buffer        = [0.0] * self.total_samples
        self.profile = SoundProfile(seed)
        self._noise_rng = random.Random(seed ^ 0xB00F)

    def play_collision_sound(self, t, impulse):
        if impulse < 6.0:
            return

        p = self.profile

        volume = min(1.0, max(0.02, impulse / 650.0)) * p.volume_scale

        t_imp = min(1.0, impulse / 900.0)
        if p.material == 0:
            freq = p.body_freq_min + t_imp * (p.body_freq_max - p.body_freq_min)
        else:
            freq = p.body_freq_max - t_imp * (p.body_freq_max - p.body_freq_min)

        dur = p.dur_min + t_imp * (p.dur_max - p.dur_min)

        start_sample   = int(t * self.sample_rate)
        num_samples    = int(self.sample_rate * dur)
        noise_samples  = int(self.sample_rate * p.noise_dur_ms / 1000.0)

        phase = 0.0
        dt    = 1.0 / self.sample_rate

        for i in range(num_samples):
            idx = start_sample + i
            if idx >= self.total_samples:
                break

            t_norm = i / max(num_samples - 1, 1)

            click = 0.0
            if i < noise_samples:
                noise_env = math.exp(-6.0 * i / max(noise_samples, 1))
                click = self._noise_rng.uniform(-1.0, 1.0) * noise_env * p.noise_level

            current_freq = freq * (1.0 - p.pitch_drop * t_norm)

            phase += 2.0 * math.pi * current_freq * dt

            body_env  = math.exp(-p.body_decay * t_norm)
            body = math.sin(phase) * body_env
            body += 0.18 * math.sin(phase * p.inharmonicity * 2.0) * body_env * 0.5

            body_level = 1.0 - p.noise_level * 0.5
            sample_val = (click + body * body_level) * volume

            self.buffer[idx] += sample_val

    def write_to_file(self):
        with wave.open(self.output_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)

            for sample in self.buffer:
                saturated  = math.tanh(sample * 1.5) / 1.5
                clamped    = max(-1.0, min(1.0, saturated))
                int_sample = int(clamped * 32767)
                wav_file.writeframes(struct.pack('h', int_sample))
