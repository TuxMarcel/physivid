# Qwen2.5-Coder:14b Coding Guidelines and Output Format

This document provides specific instructions and expectations for the `qwen2.5-coder:14b` model when generating code for the deterministic audiovisual physics CLI tool. Adherence to these guidelines will ensure the generated code is maintainable, functional, and aligns with project standards.

## 1. General Coding Style

-   **PEP 8 Compliance:** All Python code generated must strictly adhere to the [PEP 8 Style Guide for Python Code](https://peps.python.org/pep-0008/). This includes naming conventions, indentation (4 spaces), line length, and whitespace.

## 2. Modularity and Structure

-   **Organize Code:** Break down functionality into logical functions, classes, and Python modules (`.py` files). Avoid monolithic code blocks.
-   **Classes for Components:** Implement main components identified in `engine_architecture.md` (e.g., `WorldGenerator`, `SimulationEngine`, `EventScheduler`, `Renderer`, `AudioSynthesizer`) as well-defined Python classes.
-   **File-per-Concern:** Each major component or logical group of functions should reside in its own Python file within the `src/` directory, as per the specified file structure.

## 3. Docstrings and Comments

-   **Docstrings:** Provide clear and concise docstrings for all modules, classes, and functions, explaining their purpose, arguments, and return values.
-   **Comments:** Use inline comments sparingly, primarily for explaining complex logic or non-obvious choices. Avoid comments that merely restate the code.

## 4. Error Handling

-   **Basic Handling:** Implement basic error handling for critical operations, especially argument parsing in the CLI and file operations (e.g., temporary file creation, FFmpeg invocation).
-   **Informative Messages:** When an error occurs, provide informative error messages that help diagnose the issue.

## 5. Testing

-   **Unit Tests:** Create basic unit tests for core deterministic logic. This includes testing the `WorldGenerator` (to ensure it produces identical worlds for identical seeds) and parts of the `SimulationEngine` that involve deterministic state changes.
-   **Test Framework:** `unittest` or `pytest` can be used for tests. Place test files in the `tests/` directory.

## 6. Expected Output Format for Qwen

When presented with an instruction Markdown file, the `qwen2.5-coder:14b` model is expected to output **only the code** for the specified component or task. Do not include conversational text, explanations, or summaries in the output unless explicitly requested.

-   **"Return code only"**: For each instruction, provide the Python code directly, formatted within a Markdown code block.

## 7. Project File Structure Expectation

The generated code should adhere to the following project structure. When creating new files, place them in their respective directories.

```
physics_video_cli/
├── src/
│   ├── __init__.py         # To make src a Python package
│   ├── cli.py              # CLI argument parsing and main execution flow
│   ├── engine.py           # Orchestrates simulation, rendering, audio
│   ├── world_generator.py  # Generates initial Pymunk world based on seed/profile
│   ├── renderer.py         # Handles headless frame drawing (e.g., using Pygame)
│   ├── audio_synth.py      # Programmatic audio generation
│   └── utils.py            # Utility functions (e.g., temporary file management, FFmpeg execution)
├── tests/
│   ├── __init__.py         # To make tests a Python package
│   └── test_engine.py      # Basic unit tests for core engine components
├── output/                 # Directory for final video outputs (managed by the script)
│   └── videos/             # Subdirectory for MP4 files
└── main.py                 # Entry point for the CLI tool
```

-   **File Creation:** The model should explicitly provide the full content for each new file it is asked to create within this structure. For instance, if asked to implement `cli.py`, the output should be the complete code for `cli.py`.
-   **Existing Files:** If an instruction modifies an existing file, the model should provide the complete, updated content of that file.

This structured approach will facilitate incremental code generation and easier integration into the final project.