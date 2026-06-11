import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import pymunk

class RenderingEngine:
    """Die generische Rendering-Engine."""
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

    def render(self, space, frame_count, output_dir):
        self.screen.fill(self.background_color)
        self._draw_grid()

        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = self._to_pygame(shape.body.position)
                color = getattr(shape, "color", (200, 200, 200))
                pygame.draw.circle(self.screen, color, pos, int(shape.radius))
                
                # Highlight für dynamische Objekte
                if getattr(shape, "is_dynamic", False):
                    highlight_color = tuple(min(255, c + 70) for c in color)
                    offset = int(shape.radius * 0.25)
                    pygame.draw.circle(self.screen, highlight_color, (pos[0]-offset, pos[1]-offset), int(shape.radius*0.25))
            
            elif isinstance(shape, pymunk.Segment):
                body = shape.body
                p1 = body.position + shape.a.rotated(body.angle)
                p2 = body.position + shape.b.rotated(body.angle)
                sp1, sp2 = self._to_pygame(p1), self._to_pygame(p2)
                color = getattr(shape, "color", (255, 255, 255))
                thickness = max(1, int(shape.radius * 2))
                pygame.draw.line(self.screen, color, sp1, sp2, thickness)
                pygame.draw.circle(self.screen, color, sp1, thickness // 2)
                pygame.draw.circle(self.screen, color, sp2, thickness // 2)

        filename = os.path.join(output_dir, f"frame_{frame_count:05d}.png")
        pygame.image.save(self.screen, filename)
