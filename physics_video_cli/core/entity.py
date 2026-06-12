import pymunk

class Entity:
    def __init__(self, body: pymunk.Body, shape: pymunk.Shape, color: tuple, trail: bool = False, trail_len: int = 10):
        self.body = body
        self.shape = shape
        self.color = color
        self.trail = trail
        self.trail_positions = []
        self.trail_len = trail_len
        
        # Tag attributes directly for renderer compatibility
        if self.shape:
            self.shape.color = color
            self.shape.is_dynamic = (self.body.body_type == pymunk.Body.DYNAMIC) if self.body else False
        if self.trail and self.body:
            self.body.trail_len = trail_len

    def add_to_space(self, space: pymunk.Space) -> None:
        if self.body and self.body != space.static_body and self.body not in space.bodies:
            space.add(self.body)
        if self.shape and self.shape not in space.shapes:
            space.add(self.shape)

    def remove_from_space(self, space: pymunk.Space) -> None:
        if self.shape and self.shape in space.shapes:
            space.remove(self.shape)
        if self.body and self.body != space.static_body and self.body in space.bodies:
            space.remove(self.body)

    def update_trail(self) -> None:
        if self.trail and self.body:
            self.trail_positions.append(tuple(self.body.position))
            if len(self.trail_positions) > self.trail_len:
                self.trail_positions.pop(0)
