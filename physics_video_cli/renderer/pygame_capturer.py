import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import pymunk
import numpy as np

class PygameCapturer:
    def __init__(self, resolution="1080x1920"):
        width, height = map(int, resolution.split('x'))
        self.width = width
        self.height = height
        pygame.init()
        self.screen = pygame.Surface((self.width, self.height))
        self.background_color = (16, 20, 28)
        self.grid_color = (24, 30, 42)

    def _to_pygame(self, p):
        return (int(p.x + self.width / 2), int(self.height / 2 - p.y))

    def _draw_grid(self):
        grid_interval = 120
        for x in range(0, self.width, grid_interval):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_interval):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y), 1)

    def render_frame(self, space, experiment=None) -> np.ndarray:
        self.screen.fill(self.background_color)
        
        # Check if experiment visual data requests grid/stars
        visual_data = experiment.get_visual_data() if experiment else {}
        bg_options = visual_data.get("background", {})
        if bg_options.get("grid", True):
            self._draw_grid()

        # Render trails first (so they are behind entities)
        if experiment and hasattr(experiment, "entities"):
            for entity in experiment.entities:
                if getattr(entity, "trail", False) and len(entity.trail_positions) > 1:
                    color = entity.color
                    for i in range(len(entity.trail_positions) - 1):
                        p1 = self._to_pygame(pymunk.Vec2d(*entity.trail_positions[i]))
                        p2 = self._to_pygame(pymunk.Vec2d(*entity.trail_positions[i+1]))
                        pygame.draw.line(self.screen, color[:3], p1, p2, max(2, int(entity.shape.radius * 0.4) if hasattr(entity.shape, 'radius') else 4))

        # Render custom visual rods or joints
        for rod in visual_data.get("rods", []):
            p1 = self._to_pygame(pymunk.Vec2d(*rod[0]))
            p2 = self._to_pygame(pymunk.Vec2d(*rod[1]))
            pygame.draw.line(self.screen, (100, 110, 130), p1, p2, 6)

        # Draw the shapes in space
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = self._to_pygame(shape.body.position)
                color = getattr(shape, "color", (200, 200, 200))
                pygame.draw.circle(self.screen, color[:3], pos, int(shape.radius))
                
                if getattr(shape, "is_dynamic", False):
                    highlight_color = tuple(min(255, c + 70) for c in color[:3])
                    offset = int(shape.radius * 0.25)
                    pygame.draw.circle(self.screen, highlight_color, (pos[0]-offset, pos[1]-offset), int(shape.radius*0.25))
            
            elif isinstance(shape, pymunk.Segment):
                body = shape.body
                p1 = body.position + shape.a.rotated(body.angle)
                p2 = body.position + shape.b.rotated(body.angle)
                sp1, sp2 = self._to_pygame(p1), self._to_pygame(p2)
                color = getattr(shape, "color", (255, 255, 255))
                thickness = max(1, int(shape.radius * 2))
                pygame.draw.line(self.screen, color[:3], sp1, sp2, thickness)
                pygame.draw.circle(self.screen, color[:3], sp1, thickness // 2)
                pygame.draw.circle(self.screen, color[:3], sp2, thickness // 2)
                
            elif isinstance(shape, pymunk.Poly):
                body = shape.body
                vertices = [self._to_pygame(v.rotated(body.angle) + body.position) for v in shape.get_vertices()]
                color = getattr(shape, "color", (150, 150, 150))
                pygame.draw.polygon(self.screen, color[:3], vertices)

        img_array = pygame.surfarray.array3d(self.screen)
        return np.transpose(img_array, (1, 0, 2))
