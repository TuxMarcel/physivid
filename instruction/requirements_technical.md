# Technical Requirements and Constraints

## 1. Python Version

Python 3.13+ (tested). Virtual environment: `~/qwen/physivid/venv/`.

## 2. Libraries

### Required (all installed in venv)

| Library | Version | Purpose |
|---|---|---|
| `pymunk` | latest | 2D physics engine |
| `pygame` | 2.6.1 | Headless frame rendering |
| `ffmpeg` | 8.1.1 (system) | Video encoding (via subprocess) |

### To Avoid

- No web frameworks (Flask, Django, FastAPI)
- No GUI frameworks for app control
- No databases (SQL/NoSQL) for core data
- No additional image libraries (Pygame handles save)

## 3. Data Handling

### 3.1 Input

CLI arguments (via `argparse` in `cli_handler.py`):

| Argument | Type | Default | Description |
|---|---|---|---|
| `--seed` | int | random | RNG seed for determinism |
| `--duration` | float | 60.0 | Video length in seconds |
| `--fps` | int | 60 | Frames per second |
| `--resolution` | str | "1080x1920" | WxH format |
| `--output_name` | str | "output" | Base name for MP4 |
| `--scene_profile` | str | "ball_pit" | `ball_pit` or `lava_lamp` |

### 3.2 Processing Pipeline

```
main.py
  → cli_handler.parse_args() or interactive_menu()
  → SimulationEngine(seed, profile, resolution, temp_dir, duration)
    → WorldGenerator(seed, profile).generate()
      → SceneClass(space, rng, palette).setup()   # builds the world
    → for each frame:
        → scene.update(frame, dt)                   # per-frame logic
        → space.step(dt)                            # physics step
        → renderer.render(space, frame, output_dir) # save PNG
    → audio.write_to_file()                         # finalize WAV
  → Utils.create_video(output_path, fps, resolution)  # FFmpeg mux
  → Utils.cleanup()                                  # remove temp files
```

### 3.3 Storage

- **Temp:** `temp_frames/` — PNG frames (`frame_%05d.png`) + `audio.wav`, cleaned after success
- **Output:** `output/videos/` — final MP4 files

### 3.4 Output

- MP4 (H.264 video + AAC audio) in `output/videos/`
- Naming: `{output_name}_{seed}_{scene_profile}.mp4` (or `{output_name}_{seed}.mp4` if name != "output")
