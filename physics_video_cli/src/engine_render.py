import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import pymunk
import math

class Renderer:
    def __init__(self, resolution="1080x1920"):
        width, height = map(int, resolution.split('x'))
        self.width = width
        self.height = height
        pygame.init()
        self.screen = pygame.Surface((width, height))

        self.background_color = (16, 20, 28)
        self.grid_color = (24, 30, 42)

        self.trails = {}
        self.max_trail_len = 10

    def _to_pygame(self, p):
        return (int(p.x + self.width / 2), int(self.height / 2 - p.y))

    def _draw_grid(self):
        grid_interval = 120
        for x in range(0, self.width, grid_interval):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_interval):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y), 1)

    def _get_shape_color(self, shape):
        base_color = getattr(shape, "color", (200, 200, 200))
        body = shape.body
        if body is not None:
            if hasattr(body, "temp"):
                t = max(0.0, min(1.0, body.temp))
                if t < 0.5:
                    s = t / 0.5
                    r = int(40 + 215 * s)
                    g = int(10 + 150 * s)
                    b = int(180 - 130 * s)
                else:
                    s = (t - 0.5) / 0.5
                    r = 255
                    g = int(160 + 95 * s)
                    b = int(50 - 40 * s)
                return (r, g, b)
            elif hasattr(body, "warm"):
                y = body.position.y
                factor = max(0.0, min(1.0, (y + 750) / 1500.0))
                if body.warm:
                    r = 255
                    g = int(160 * factor)
                    b = int(128 * (1.0 - factor))
                    return (r, g, b)
                else:
                    r = int(10 + 150 * factor)
                    g = int(130 - 110 * factor)
                    b = 255
                    return (r, g, b)
        return base_color

    def _update_and_draw_trails(self, shape, color):
        if not getattr(shape, "is_dynamic", False):
            return

        body = shape.body
        if body is None:
            return

        body_id = id(body)
        pos = body.position
        max_trail = getattr(body, "trail_len", self.max_trail_len)

        if body_id not in self.trails:
            self.trails[body_id] = []

        self.trails[body_id].append(pos)
        if len(self.trails[body_id]) > max_trail:
            self.trails[body_id].pop(0)

        trail_positions = self.trails[body_id]
        num_pts = len(trail_positions)
        bg = self.background_color

        for i, trail_pos in enumerate(trail_positions[:-1]):
            weight = 0.05 + 0.35 * (i / num_pts)
            r = int(bg[0] + (color[0] - bg[0]) * weight)
            g = int(bg[1] + (color[1] - bg[1]) * weight)
            b = int(bg[2] + (color[2] - bg[2]) * weight)

            trail_radius = int(shape.radius * (0.4 + 0.5 * (i / num_pts)))
            screen_pos = self._to_pygame(trail_pos)
            pygame.draw.circle(self.screen, (r, g, b), screen_pos, trail_radius)

    def render(self, space, frame_count, output_dir):
        self.screen.fill(self.background_color)
        self._draw_grid()

        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = self._to_pygame(shape.body.position)
                color = self._get_shape_color(shape)

                self._update_and_draw_trails(shape, color)

                pygame.draw.circle(self.screen, color, pos, int(shape.radius))

                if getattr(shape, "is_dynamic", False):
                    highlight_color = tuple(min(255, c + 70) for c in color)
                    highlight_radius = int(shape.radius * 0.25)
                    offset = int(shape.radius * 0.25)
                    highlight_pos = (pos[0] - offset, pos[1] - offset)
                    pygame.draw.circle(self.screen, highlight_color, highlight_pos, highlight_radius)
                else:
                    pygame.draw.circle(self.screen, (100, 115, 135), pos, int(shape.radius), 2)

            elif isinstance(shape, pymunk.Segment):
                body = shape.body
                if body is not None and body.body_type != pymunk.Body.STATIC:
                    p1 = body.position + shape.a.rotated(body.angle)
                    p2 = body.position + shape.b.rotated(body.angle)
                else:
                    p1 = shape.a
                    p2 = shape.b

                sp1 = self._to_pygame(p1)
                sp2 = self._to_pygame(p2)

                color = getattr(shape, "color", (255, 255, 255))
                thickness = int(shape.radius * 2) if shape.radius > 0 else 5

                pygame.draw.line(self.screen, color, sp1, sp2, thickness)
                pygame.draw.circle(self.screen, color, sp1, thickness // 2)
                pygame.draw.circle(self.screen, color, sp2, thickness // 2)

        filename = os.path.join(output_dir, f"frame_{frame_count:05d}.png")
        pygame.image.save(self.screen, filename)
