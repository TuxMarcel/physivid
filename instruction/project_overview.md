# Project Overview: Deterministic Audiovisual Physics CLI Tool

## 1. Project Goal

A Python CLI tool that generates deterministic audiovisual physics videos in a headless rendering pipeline. A user-provided seed guarantees a unique yet reproducible world, with synchronized visuals and sound rendered into MP4 video.

## 2. Current Status (June 2026)

The project is functional with two complete scenes:

| Scene | Status | Description |
|---|---|---|
| `ball_pit` | ✅ Production-ready | Plinko-style ball drop with pegs, spinners, bumpers (5 layouts) |
| `lava_lamp` | ✅ Production-ready | Ampoule-shaped vessel, organic blobs with merge/split + temp-driven convection |
| `dna_helix` | ❌ Not started | Planned double-helix visualization |
| `domino_effect` | ❌ Not started | Planned domino chain reaction |

## 3. Key Features (all implemented)

- **Seed-based determinism:** Same seed → identical video every time
- **Modular architecture:** Engine, worlds (scenes), entities (reusable components)
- **Headless rendering:** Pygame off-screen surface, no GUI
- **MP4 export:** FFmpeg muxes PNG frames + WAV audio
- **Integrated audio:** Collision-based synthesized sound (material profiles: plastic, wood, ceramic)
- **Shared output folder:** `output/videos/`

## 4. User Interaction

Two modes:
- **CLI args:** `python main.py --seed 42 --scene_profile lava_lamp --duration 30 --fps 60`
- **Interactive menu:** Run `python main.py` without args → prompts for world, seed, duration

Wrapper script: `~/bin/physivid` (calls main.py with venv Python, passes all args through).

## 5. Known Limitations

- `EventScheduler` (from original architecture spec) was never implemented — scene updates handle per-frame logic directly
- No metadata JSON output per render
- No FFmpeg availability check (assumes `h264_nvenc` in PATH)
- PNG save via `pygame.image.save()` is the main performance bottleneck
