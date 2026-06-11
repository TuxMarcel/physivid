# Command-Line Interface Specification

## 1. Implementation (`cli_handler.py`)

Uses Python `argparse`. Two entry modes:

### CLI Mode
```bash
python main.py \
    --seed 789 \
    --duration 15.0 \
    --fps 30 \
    --resolution 1280x720 \
    --output_name "my_clip" \
    --scene_profile lava_lamp
```

### Interactive Mode
```bash
python main.py   # no args → interactive menu
```
Or via wrapper:
```bash
~/bin/physivid --seed 42 --scene_profile ball_pit --duration 60
```

## 2. Arguments

| Argument | Type | Default | Choices | Description |
|---|---|---|---|---|
| `--seed` | int | random | any int | Determinism seed |
| `--duration` | float | 60.0 | > 0 | Video length (seconds) |
| `--fps` | int | 60 | > 0 | Frames per second |
| `--resolution` | str | "1080x1920" | "WxH" format | Output resolution |
| `--output_name` | str | "output" | any string | Base MP4 filename |
| `--scene_profile` | str | "ball_pit" | ball_pit, lava_lamp | World to simulate |

## 3. Scene Profiles Available

| Profile | Description | Interactive Menu |
|---|---|---|
| `ball_pit` | Bälle-Parcours (Plinko) | Option 1 |
| `lava_lamp` | Lava-Lampe | Option 2 |
| (future) `dna_helix` | DNA-Doppelhelix | Option 3 (not implemented) |
| (future) `domino_effect` | Domino-Effekt | Option 4 (not implemented) |

## 4. Output File Naming

- If `--output_name` is "output" (default): `output/{name}_{seed}_{profile}.mp4`
- If custom name: `output/{name}_{seed}.mp4`
- Example: `output/videos/my_clip_789_lava_lamp.mp4`
