# Coding Guidelines — Project State (June 2026)

## 1. Current Project Structure

```
physics_video_cli/
├── main.py                          ← Entry point
├── src/
│   ├── engine_sim.py                ← SimulationEngine
│   ├── engine_world.py              ← WorldGenerator
│   ├── engine_render.py             ← Renderer (Pygame headless)
│   ├── engine_audio.py              ← AudioSynthesizer
│   ├── cli_handler.py               ← CLI parser (argparse)
│   ├── utils_ffmpeg.py              ← FFmpeg + temp file mgmt
│   ├── scenes/
│   │   ├── scene_base.py            ← BaseScene
│   │   ├── scene_ball_pit.py        ← BallPitScene (production, 600→300 LOC)
│   │   └── scene_lava_lamp.py       ← LavaLampScene (production, ~100 LOC)
│   └── entities/
│       ├── lava_blob.py             ← Blob: create, merge, split, velocity
│       └── ball_pit.py              ← Wall, peg, spinner, ball helpers
├── tests/
│   └── test_engine.py              ← 3 determinism tests
└── output/videos/                   ← Final MP4s
```

## 2. Coding Conventions

- **PEP 8:** 4-space indent, snake_case for functions/variables, CamelCase for classes
- **Modules:** One concern per file. `engine_*` for pipeline, `scene_*` for world builders, `entities/*` for reusable physics components
- **Imports:** Always use absolute imports from `src.` (e.g., `from src.entities.lava_blob import create_blob`)
- **RNG discipline:** `self.rng` (from `BaseScene`) is seeded and used ONLY in `setup()` and `update()` — NEVER in velocity functions or collision callbacks
- **No comments in entity code** unless absolutely necessary for complex logic

## 3. How Scenes Work

Each scene:
1. Extends `BaseScene(space, rng, palette)`
2. `setup()` builds the Pymunk space (walls, entities, initial objects)
3. `update(frame, dt)` handles per-frame logic (spawning, recycling, merge/split)
4. Entities are imported from `src.entities.*` — no entity logic in scene files
5. Scene is registered in `engine_world.py`'s `scenes_registry` dict

## 4. How Entities Work

Entities are pure-function modules in `src/entities/`:
- They take a `space` and parameters, return Pymunk bodies/shapes
- They take a `rng` only during creation (not during runtime)
- Velocity functions are defined as module-level functions (not methods) to avoid reference issues
- Collision groups: same `ShapeFilter(group=N)` → no self-collision (used by lava blobs)

## 5. Adding a New Scene

1. Create `src/entities/new_scene.py` with entity helpers (if needed)
2. Create `src/scenes/scene_new_scene.py` with `NewScene(BaseScene)`
3. Register in `engine_world.py` `scenes_registry` dict
4. Add to `cli_handler.py` choices list
5. Add to `main.py` interactive menu
6. Add test case in `tests/test_engine.py`

## 6. Testing

```bash
cd physics_video_cli
source ~/qwen/physivid/venv/bin/activate
python -m unittest tests.test_engine -v
```

Current tests validate:
- World generator determinism (identical space for same seed)
- Full simulation determinism (identical state + audio after N frames)
- Audio synthesis (collision sound modifies buffer correctly)

## 7. What's NEXT for the Next Developer

### High Priority
- **DNA Helix scene** (Option 3): Two helical strands with cross-bars, slow rotation, particles
- **Domino Effect scene** (Option 4): Chain reaction of falling dominos
- **Metaball rendering** for lava lamp: smooth visual merging instead of overlapping circles

### Quality of Life
- FFmpeg availability check before encoding
- Metadata JSON per render (seed, params, duration)
- Per-scene audio profiles (lava lamp should have muffled, liquid sounds)
- Progress bar during rendering

### Performance
- Alternative to `pygame.image.save()` for faster PNG writes (e.g., `PIL/Image` or raw RGB → FFmpeg pipe)
- Configurable trail length per scene (currently hardcoded 5–10)
