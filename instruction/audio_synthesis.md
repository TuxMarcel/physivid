# Integrated Audio Synthesis and Synchronization

## 1. Implementation (`engine_audio.py`)

Pure Python WAV synthesis — no external audio libraries.

### SoundProfile (`SoundProfile` class)

Seed-driven acoustic material model. Each seed produces a consistent material type:

| Material | Sound Character | Frequency Range | Decay |
|---|---|---|---|
| Plastic/Ping-Pong | Bright, short click | 1800–4500 Hz | Fast (18–30) |
| Wood/Xylophone | Warm mid thud | 180–900 Hz | Medium (8–16) |
| Ceramic/Stone | Medium, slightly inharmonic | 400–1800 Hz | Medium (10–22) |

Properties derived from seed: body frequency min/max, decay rate, noise level, duration, pitch drop, volume scale, inharmonicity.

### AudioSynthesizer

- Buffer: float array of `duration * sample_rate` (default 44.1 kHz mono)
- `play_collision_sound(t, impulse)`: generate impact at time `t` with volume + pitch mapped from impulse
  - Impulse < 6.0 → silent (filters out micro-collisions)
  - Impulse range 6–900 → maps to volume 0.02–1.0
  - Material affects pitch: plastic gets brighter with force, wood/ceramic get deeper
- Sound structure: noise attack transient (click) + resonant body (sine with inharmonic overtone) + pitch drop over duration
- `write_to_file()`: soft-clamp via `tanh()`, save as 16-bit PCM WAV

## 2. Synchronization

- `play_collision_sound(self.current_time, impulse)` called from `SimulationEngine._on_collision()` during each frame's physics step
- `current_time = frame * dt` — frame-accurate timing
- Multiple simultaneous sounds mix additively in the buffer

## 3. Output

- Temporary file: `{temp_dir}/audio.wav`
- 44.1 kHz, 16-bit mono PCM WAV
- Muxed into final MP4 by FFmpeg (converted to AAC audio stream)

## 4. Known Limitations

- Only collision sounds are implemented (no movement/whoosh or ambient tones)
- No volume mixing control per sound type (all sounds summed at same level)
- Deterministic noise RNG seeded separately from simulation seed
