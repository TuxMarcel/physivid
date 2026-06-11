# Headless Rendering Pipeline

This document details the process for generating visual frames from the physics simulation in a headless (off-screen) manner, preparing them for final video encoding.

## 1. Renderer Choice and Configuration

-   **Recommended Renderer:** `Pygame` is the recommended library for rendering due to its capabilities for off-screen surface manipulation and deterministic drawing operations. Alternatives must also support headless rendering.
-   **Headless Operation:** The renderer must be configured to operate without displaying any graphical windows. For Pygame, this typically involves setting the `SDL_VIDEODRIVER` environment variable to `dummy` or creating a `NOFRAME` display surface.
-   **Surface Initialization:** Initialize a Pygame display surface (or equivalent in another library) with the `--resolution` specified in the CLI arguments (e.g., "1920x1080"). This surface will serve as the canvas for drawing each frame.

## 2. Frame Generation Process

For each simulation step (corresponding to a video frame):

1.  **Clear Canvas:** The rendering surface should be cleared (e.g., filled with a background color) at the beginning of each frame's rendering cycle.
2.  **Draw Scene Elements:** Based on the current state of physics objects obtained from the `SimulationEngine` (positions, rotations, types, etc.), draw corresponding visual elements onto the off-screen surface.
    -   **Visual Mapping:** Define a clear mapping between Pymunk shapes (e.g., `Circle`, `Segment`, `Poly`) and their graphical representations (e.g., Pygame `circle()`, `line()`, `polygon()`).
    -   **Colors and Properties:** Colors and other visual properties (e.g., line thickness) can be determined based on object types, their state, or other simulation parameters, ensuring determinism.
3.  **Capture Frame:** After all elements for the current frame have been drawn, the entire off-screen surface is captured.

## 3. Output Format for Frames

-   **Image Files:** Each captured frame should be saved as an individual image file. **PNG** format is highly recommended due to its lossless compression, which is crucial for maintaining visual quality before video encoding.
-   **Naming Convention:** Images should be named with a consistent, zero-padded sequential number for easy processing by FFmpeg.
    -   **Example:** `frame_00001.png`, `frame_00002.png`, ..., `frame_N.png`
-   **Temporary Directory:** All generated frame images must be stored in a dedicated temporary directory. This directory will be managed by the application for cleanup after video export.

## 4. Visual Elements Mapping (Example)

-   **Pymunk Circle:** Render as a filled circle in Pygame.
-   **Pymunk Segment:** Render as a line in Pygame.
-   **Pymunk Poly:** Render as a filled polygon in Pygame.
-   **Dynamic Coloring:** Consider assigning colors to objects based on their `body.id` (if deterministic) or `body.mass` or `body.velocity` magnitude to add visual interest, but ensure this logic is also deterministic.
-   **Coordinate Systems:** Pay attention to the transformation between Pymunk's coordinate system (typically y-up) and Pygame's (typically y-down, with origin at top-left). Necessary transformations (flipping y-axis, offsetting origin) must be applied consistently.
