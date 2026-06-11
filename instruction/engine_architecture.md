# Core Engine Architecture and Simulation

This document outlines the fundamental architecture of the physics simulation engine, emphasizing its deterministic nature and core components.

## 1. Deterministic Design Principle

A cornerstone of this project is **determinism**. Every aspect of the simulation, from world generation to physics updates and event scheduling, must be entirely predictable and reproducible based on the initial `seed` and `scene_profile`. This means that:

-   Given the same `seed` and CLI arguments, the simulation must produce the exact same sequence of physical states and events every time it is run.
-   Random number generation, if used, must be seeded consistently at the very beginning of the simulation setup phase.
-   Floating-point calculations and physics updates should be handled in a way that minimizes platform-dependent variations (though Pymunk itself is designed for determinism).

## 2. Main Components

The engine will consist of at least the following primary components, likely implemented as Python classes or modules:

### 2.1. `WorldGenerator`

-   **Purpose:** Responsible for creating the initial physical world setup within the Pymunk space.
-   **Inputs:** Takes the `seed` (integer) and `scene_profile` (string) as primary inputs.
-   **Functionality:**
    -   Initializes and seeds any internal random number generators based on the provided `seed`.
    -   Based on the `scene_profile`, it configures the Pymunk `Space` object.
    -   Generates and adds physics bodies, shapes, joints, and other constraints to the `Space`.
    -   Sets initial velocities, positions, and other properties of objects.
    -   May include logic to define boundaries or static elements of the world.
    -   Ensures that for a given `seed` and `scene_profile`, the generated `Space` is always identical.

### 2.2. `SimulationEngine`

-   **Purpose:** Manages the Pymunk physics space, advances the simulation step-by-step, and queries the state of physics objects.
-   **Inputs:** Receives the initialized Pymunk `Space` from `WorldGenerator` and simulation parameters (e.g., time step, number of iterations per step).
-   **Functionality:**
    -   Contains the main loop for stepping the physics simulation.
    -   Calls `space.step(dt)` for a fixed `dt` (time delta) repeatedly.
    -   Handles collision detection and resolution implicitly through Pymunk.
    -   Provides methods to query the current state (position, velocity, rotation, etc.) of all active physics bodies and shapes within the `Space`.
    -   Ensures consistent time stepping to maintain determinism.

### 2.3. `EventScheduler`

-   **Purpose:** Manages time-based events within the simulation, such as triggers for sound generation, visual effects, or changes in simulation parameters.
-   **Inputs:** Receives the current simulation time or frame number.
-   **Functionality:**
    -   Stores a list of scheduled events with their trigger times.
    -   During each simulation step, checks for events that should occur at the current time.
    -   Executes event callbacks, which might involve instructing the audio synthesizer, renderer, or even modifying the physics `Space`.
    -   Events triggered must also be deterministic based on the initial `seed`.

## 3. Simulation Loop Outline

The main simulation loop, typically driven by the `SimulationEngine`, will perform the following sequence of operations for each frame to be rendered:

1.  **Advance Physics:**
    -   The `SimulationEngine` advances the Pymunk `Space` by a fixed `dt` (time delta). This might involve multiple sub-steps for accuracy.
    -   `SimulationEngine` updates the internal state of all physics objects.

2.  **Query Object States:**
    -   After the physics step, the `SimulationEngine` (or a dedicated data retriever) queries the current positions, velocities, rotations, and other relevant attributes of all bodies and shapes in the `Space`. This data will be passed to the renderer and audio synthesizer.

3.  **Generate Visual Data for Renderer:**
    -   Based on the queried object states, data structures representing the visual scene for the current frame are prepared. This includes positions, colors, sizes, and orientations of graphical elements. This data is then passed to the `rendering_pipeline`.

4.  **Generate Audio Data:**
    -   Simultaneously, based on the queried object states and potentially `EventScheduler` triggers (e.g., collision detected), audio events are identified.
    -   The `audio_synthesis` component generates or arranges corresponding audio samples for the current time slice.
    -   This audio data is then passed to the `audio_synthesis` component for processing.