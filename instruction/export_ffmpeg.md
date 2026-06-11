# Video Export with FFmpeg

## 1. Implementation (`utils_ffmpeg.py`)

The `Utils` class handles temporary files and calls FFmpeg via `subprocess.run()`.

### FFmpeg Command (single pass — video + audio together)

```bash
ffmpeg \
    -framerate <fps> \
    -i temp_frames/frame_%05d.png \
    -i temp_frames/audio.wav \
    -c:v h264_nvenc \
    -pix_fmt yuv420p \
    -vf "scale=<resolution>" \
    -c:a aac \
    -strict experimental \
    -y \
    output/videos/<filename>.mp4
```

**Notes:**
- Uses **NVENC** (GPU hardware encoding via `h264_nvenc`). Falls back to software encoding if unavailable.
- `-vf scale` forces output resolution (PNGs rendered at requested resolution, but scale ensures consistency)
- AAC audio stream from WAV input
- `-y` overwrites existing output

## 2. Prerequisites

- FFmpeg must be in PATH (no availability check implemented — add if needed)
- Tested with FFmpeg 8.1.1

## 3. File Management

### Temporary Files (`temp_frames/`)

| File | Format | Contents |
|---|---|---|
| `frame_%05d.png` | PNG sequence | One per frame (zero-padded to 5 digits) |
| `audio.wav` | 16-bit PCM WAV | Mono, 44.1 kHz |

Cleanup via `Utils.cleanup()` removes the entire `temp_frames/` directory.

### Output Location

Default: `output/videos/` (created automatically if it doesn't exist).

## 4. Known Issues

- No FFmpeg existence check before running (will crash with cryptic error if missing)
- If `h264_nvenc` is unavailable, change to `libx264` in `utils_ffmpeg.py`
- Single-pass approach (encode happens after all frames rendered) — no intermediate video-only file
