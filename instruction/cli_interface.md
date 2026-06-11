# Command-Line Interface (CLI) Specification

This document details the command-line arguments that the Python CLI tool will accept. The `argparse` module is recommended for handling these arguments.

## 1. Expected CLI Arguments

The tool should be invoked with the following arguments:

-   **`--seed`**
    -   **Type:** Integer
    -   **Description:** A unique integer value that initializes the random number generator, ensuring deterministic world generation. The same seed will always produce an identical simulation and video output.
    -   **Example:** `--seed 12345`

-   **`--duration`**
    -   **Type:** Float
    -   **Description:** The total length of the output video in seconds.
    -   **Example:** `--duration 10.5` (for a 10.5-second video)

-   **`--fps`**
    -   **Type:** Integer
    -   **Description:** The desired frames per second (FPS) for the output video. This also dictates the simulation step rate for visual rendering.
    -   **Example:** `--fps 60`

-   **`--resolution`**
    -   **Type:** String
    -   **Description:** The resolution of the output video frames, specified as "WIDTHxHEIGHT".
    -   **Example:** `--resolution 1920x1080`

-   **`--output_name`**
    -   **Type:** String
    -   **Description:** The base name for the generated MP4 video file (e.g., if `my_video` is provided, the output could be `my_video.mp4`).
    -   **Example:** `--output_name "collision_simulation"`

-   **`--scene_profile`**
    -   **Type:** String
    -   **Description:** A identifier string that selects a specific pre-defined simulation scenario, world configuration, or set of initial physics parameters. This allows for varied video content using different "scenes".
    -   **Example:** `--scene_profile "bouncing_balls"` or `--scene_profile "domino_effect"`

## 2. Example CLI Invocation

A typical invocation of the CLI tool would look like this:

```bash
python main.py 
    --seed 789 
    --duration 15.0 
    --fps 30 
    --resolution 1280x720 
    --output_name "my_physics_clip" 
    --scene_profile "pendulum_swing"
```

## 3. Error Handling

The CLI parser should include basic error handling for invalid argument types or missing required arguments. Sensible default values should be considered where appropriate for optional arguments.
