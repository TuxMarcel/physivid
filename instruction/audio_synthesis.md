# Integrated Audio Synthesis and Synchronization

This document outlines the approach for generating and synchronizing audio with the physics simulation. Sound is an integral part of the final video, directly tied to simulation events.

## 1. Sound Generation Strategy

The initial implementation should focus on simple, programmatic sound generation directly from Python code.

-   **Types of Sounds:**
    -   **Collision Sounds:** Generate short, percussive sounds upon physics body collisions. The intensity (volume, pitch) of the sound could correlate with the force or relative velocity of the collision.
    -   **Movement Sounds:** Optionally, subtle sounds could be generated for objects moving rapidly or consistently (e.g., a "whoosh" sound for fast objects, or a low hum for rolling objects).
    -   **Event-Based Tones:** Sounds triggered by `EventScheduler` for specific, pre-defined simulation events.
-   **Programmatic Generation:**
    -   Utilize Python's standard libraries or a minimal external library (e.g., `scipy.io.wavfile` or `sounddevice` if extremely lightweight) to generate raw audio samples (e.g., sine waves, square waves, basic envelopes). Avoid complex, heavy audio synthesis frameworks initially.
    -   Parameters for sound characteristics (frequency, amplitude, duration, attack/decay) must be derived deterministically from simulation state or event properties.
    -   The generation should output raw PCM audio data.

## 2. Synchronization with Visuals

Accurate synchronization between audio and visuals is paramount for a cohesive audiovisual experience.

-   **Frame-Accurate Generation:** Audio should be generated in small chunks that correspond precisely to the time duration of each visual frame.
-   **Event Triggering:**
    -   The `EventScheduler` or the `SimulationEngine` itself should detect physics events (like collisions) and trigger the audio synthesis component to generate the appropriate sound data for that specific time slice.
    -   Ensure that the time at which an audio event is triggered in the simulation exactly matches the visual event it accompanies.
-   **Deterministic Audio:** Just like the visuals, the audio generated must be deterministic based on the `seed`. The same simulation run with the same seed should always produce the exact same audio output.

## 3. Output Format for Audio

-   **Temporary Audio File:** The generated audio samples for the entire simulation duration should be concatenated and saved as a single, temporary **WAV file**. This format is uncompressed and widely compatible, making it suitable for FFmpeg.
-   **File Naming:** The temporary WAV file should have a clear, unique name, possibly incorporating the `output_name` and `seed` to avoid conflicts during concurrent runs.
-   **Sampling Rate/Bit Depth:** A common sampling rate (e.g., 44.1 kHz or 48 kHz) and bit depth (e.g., 16-bit PCM) should be chosen and consistently applied throughout the audio generation process.
-   **Channels:** Mono or Stereo, depending on complexity, but start with mono for simplicity.

## 4. Considerations

-   **Performance:** Generating audio programmatically can be CPU-intensive. Optimize the generation process to keep up with the real-time simulation and rendering pace.
-   **Mixing:** If multiple sounds occur simultaneously, their audio samples will need to be mixed together (summed) correctly, taking care to avoid clipping.
-   **Volume Control:** Implement basic volume control for different types of sounds.
