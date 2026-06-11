# Project Overview: Deterministic Audiovisual Physics CLI Tool

## 1. Project Goal

This project aims to develop a Python Command-Line Interface (CLI) tool capable of generating deterministic audiovisual physics videos within a headless rendering pipeline. The core objective is to create a reusable simulation engine where a user-provided seed guarantees a unique yet reproducible world, and subsequently renders synchronized visuals and sound into a final MP4 video.

## 2. Core Functionality

The primary function of this tool is to simulate physical interactions based on a user-defined seed and then render these simulations into a video format, complete with integrated audio.

## 3. Key Features

-   **Seed-Based World Generation:** A given seed will always produce the exact same simulation world and subsequent video, ensuring full reproducibility. Different seeds will generate distinct videos.
-   **Reusable Engine Architecture:** The project will be built as a modular and extensible engine, not a one-off script, allowing for future expansion and varied scene profiles.
-   **Headless Frame Rendering:** The visual component of the simulation will be rendered off-screen, without requiring a graphical user interface (GUI) to be displayed.
-   **Automatic MP4 Export:** The rendered frames and synchronized audio will be automatically compiled and encoded into a single MP4 video file using FFmpeg.
-   **Integrated Audio Synthesis:** Sound is a fundamental part of the system, generated and structured in direct synchronization with the visual simulation, rather than being added as an optional overlay.
-   **Shared Output Folder:** All final `.mp4` video outputs will be saved into a single, designated shared output directory.

## 4. User Interaction

The application will be exclusively interacted with via the command-line interface (CLI). There will be no web-based user interface or public API in the initial version. Users will pass parameters such as `seed`, `duration`, `fps`, `resolution`, `output_name`, and `scene_profile` as CLI arguments.
