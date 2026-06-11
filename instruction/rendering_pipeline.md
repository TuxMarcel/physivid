# Headless Rendering Pipeline

## 1. Renderer (`engine_render.py`)

Uses Pygame in headless mode (`SDL_VIDEODRIVER=dummy`).

### Initialization:
```python
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
self.screen = pygame.Surface((width, height))
```

### Per-Frame Rendering:

1. **Clear:** Fill surface with dark background `(16, 20, 28)`
2. **Grid:** Draw subtle blue-gray grid lines (every 120px)
3. **Draw shapes** (iterates `space.shapes`):
   - **Circles:** Filled circle + optional highlight (3D effect) + trail circles
   - **Segments:** Thick line with rounded caps
4. **Save:** `pygame.image.save(screen, "frame_%05d.png")`

## 2. Shape-to-Visual Mapping

| Pymunk Shape | Pygame Drawing | Notes |
|---|---|---|
| `Circle` (dynamic) | Filled circle + highlight offset to top-left | 3D sphere look |
| `Circle` (static) | Outline circle (2px stroke, blue-gray) | Blueprint style |
| `Segment` | Thick line + rounded caps | Color from shape.color |

## 3. Color System

Color is determined by `_get_shape_color(shape)`:

1. If `body.temp` exists (lava blobs) → smooth gradient based on temperature (0.0=purple, 0.5=orange, 1.0=yellow-white)
2. If `body.warm` exists (legacy) → binary warm/cool gradient based on y-position
3. Otherwise → `shape.color` (set by scene during setup)

## 4. Trail System

Dynamic bodies render motion trails:
- Configurable via `body.trail_len` attribute (default `max_trail_len = 10`)
- Each frame appends position; old positions fade out with reduced opacity and size
- Background blending for smooth fade effect

## 5. Coordinate System

- **Pymunk:** y-up, origin at center (range: ~ -520×-920 to 520×920)
- **Pygame:** y-down, origin at top-left
- **Transform in `_to_pygame()`:** `(x + w/2, h/2 - y)`

## 6. Performance Notes

- PNG save via `pygame.image.save()` is the main bottleneck
- At 1080×1920, 60 FPS: expect ~50-200ms per frame save
- Reducing resolution or FPS gives linear speedup
- Trail rendering adds overhead per dynamic shape (set `trail_len` lower for performance)
