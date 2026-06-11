# Core Engine Architecture

## 1. Deterministic Design Principle

All simulation output is entirely determined by the `seed`. Same seed + same args = identical video, audio, and physics state. Key rules:
- **RNG is seeded once** in `WorldGenerator.__init__` via `random.Random(seed)`
- **RNG is NEVER called** inside velocity functions, collision callbacks, or hot loops
- Velocity functions and updates use deterministic math only (no `random` calls)
- The shared `self.rng` is only used during `scene.setup()` and `scene.update()`

## 2. File Structure

```
physics_video_cli/
├── main.py                    ← Entry point (CLI args or interactive menu)
├── src/
│   ├── engine_sim.py          ← SimulationEngine: main loop
│   ├── engine_world.py        ← WorldGenerator: picks scene, builds space
│   ├── engine_render.py       ← Renderer: headless Pygame drawing
│   ├── engine_audio.py        ← AudioSynthesizer: collision sound synthesis
│   ├── cli_handler.py         ← CLI argument parsing (argparse)
│   ├── utils_ffmpeg.py        ← FFmpeg muxing + temp file management
│   ├── scenes/
│   │   ├── scene_base.py      ← BaseScene (abstract)
│   │   ├── scene_ball_pit.py  ← BallPitScene (5 layouts)
│   │   └── scene_lava_lamp.py ← LavaLampScene (ampoule + blobs)
│   └── entities/
│       ├── lava_blob.py       ← Blob creation, merge, split, velocity
│       └── ball_pit.py        ← Wall, peg, spinner, ball helpers
├── tests/
│   └── test_engine.py         ← Determinism + audio tests
└── output/videos/             ← Final MP4 files
```

## 3. Engine Components

### 3.1 WorldGenerator (`engine_world.py`)

- Takes `seed` (int) and `profile` (str)
- Creates Pymunk `Space`, seeds RNG, selects scene class from registry
- Sets gravity: `(0, -900)` for ball_pit, `(0, 0)` for others (individual scenes may override)
- Calls `scene.setup()` which populates the space

### 3.2 SimulationEngine (`engine_sim.py`)

- Orchestrates the full pipeline
- Per frame: `scene.update() → space.step() → renderer.render()`
- Collision callback: `post_solve` → measures impulse → triggers audio if > 10.0
- After loop: finalizes audio WAV

### 3.3 BaseScene (`scenes/scene_base.py`)

- Constructor receives: `space`, `rng` (seeded Random), `palette` (color list)
- `setup()` — builds world geometry and entities
- `update(frame, dt)` — per-frame logic (spawning, recycling, merge/split)

## 4. Per-Frame Loop

Each frame (dt = 1/fps):
1. `scene.update(frame, dt)` — spawn/recycle/merge/split logic
2. `space.step(dt)` — Pymunk physics (gravity, collisions, velocity funcs)
3. `renderer.render(space, frame, temp_dir)` — draw + save PNG
4. Collision callbacks queue audio events during physics step

## 5. What Was Removed from Original Spec

- **EventScheduler** — never implemented; scenes handle timing via `update()`
- **Separate Renderer class in dedicated file** — moved to `entities/` pattern instead
