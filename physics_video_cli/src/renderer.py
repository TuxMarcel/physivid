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
        # Initialize pygame display silently
        pygame.init()
        self.screen = pygame.Surface((width, height))
        
        # Premium color palette
        self.background_color = (16, 20, 28)  # Deep dark slate/navy
        self.grid_color = (24, 30, 42)        # Subtle grid lines
        
        # Trail memory: maps body ID to list of recent positions
        self.trails = {}
        self.max_trail_len = 10

    def _to_pygame(self, p):
        # Convert Pymunk coordinates (centered at 0,0) to Pygame coordinates (top-left is 0,0)
        return (int(p.x + self.width / 2), int(self.height / 2 - p.y))

    def _draw_grid(self):
        # Draw a beautiful technical background grid
        grid_interval = 120
        for x in range(0, self.width, grid_interval):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_interval):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y), 1)

    def _get_shape_color(self, shape):
        base_color = getattr(shape, "color", (200, 200, 200))
        
        # Custom color transition for lava lamp bubbles
        body = shape.body
        if body is not None and hasattr(body, "warm"):
            y = body.position.y
            # Map y from [-800, 800] to [0.0, 1.0]
            factor = max(0.0, min(1.0, (y + 750) / 1500.0))
            if body.warm:
                # Rising: interpolate from hot magenta (255, 0, 128) to bright orange/gold (255, 160, 10)
                r = 255
                g = int(160 * factor)
                b = int(128 * (1.0 - factor))
                return (r, g, b)
            else:
                # Sinking: interpolate from purple/violet (160, 20, 240) to electric blue (10, 130, 255)
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
        
        if body_id not in self.trails:
            self.trails[body_id] = []
            
        self.trails[body_id].append(pos)
        if len(self.trails[body_id]) > self.max_trail_len:
            self.trails[body_id].pop(0)
            
        # Draw trail circles
        trail_positions = self.trails[body_id]
        num_pts = len(trail_positions)
        bg = self.background_color
        
        for i, trail_pos in enumerate(trail_positions[:-1]):
            # Faux transparency: blend color with background based on age
            weight = 0.05 + 0.35 * (i / num_pts)
            r = int(bg[0] + (color[0] - bg[0]) * weight)
            g = int(bg[1] + (color[1] - bg[1]) * weight)
            b = int(bg[2] + (color[2] - bg[2]) * weight)
            
            # Trail circles get progressively smaller
            trail_radius = int(shape.radius * (0.4 + 0.5 * (i / num_pts)))
            screen_pos = self._to_pygame(trail_pos)
            pygame.draw.circle(self.screen, (r, g, b), screen_pos, trail_radius)

    def render(self, space, frame_count, output_dir):
        # Clear screen and draw tech grid
        self.screen.fill(self.background_color)
        self._draw_grid()
        
        for shape in space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = self._to_pygame(shape.body.position)
                color = self._get_shape_color(shape)
                
                # Draw trails first
                self._update_and_draw_trails(shape, color)
                
                # Draw main circle
                pygame.draw.circle(self.screen, color, pos, int(shape.radius))
                
                # Draw 3D-sphere highlight for dynamic circles
                if getattr(shape, "is_dynamic", False):
                    highlight_color = tuple(min(255, c + 70) for c in color)
                    highlight_radius = int(shape.radius * 0.25)
                    # Offset highlight to top-left of bubble
                    offset = int(shape.radius * 0.25)
                    highlight_pos = (pos[0] - offset, pos[1] - offset)
                    pygame.draw.circle(self.screen, highlight_color, highlight_pos, highlight_radius)
                else:
                    # Draw a nice clean stroke outline for static pegs to look like blueprint components
                    pygame.draw.circle(self.screen, (100, 115, 135), pos, int(shape.radius), 2)
                    
            elif isinstance(shape, pymunk.Segment):
                # Retrieve world coordinates for segments (accounting for body translation/rotation if kinematic)
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
                
                # Draw segment line
                pygame.draw.line(self.screen, color, sp1, sp2, thickness)
                # Draw rounded caps for the segment ends
                pygame.draw.circle(self.screen, color, sp1, thickness // 2)
                pygame.draw.circle(self.screen, color, sp2, thickness // 2)
        
        filename = os.path.join(output_dir, f"frame_{frame_count:05d}.png")
        pygame.image.save(self.screen, filename)
