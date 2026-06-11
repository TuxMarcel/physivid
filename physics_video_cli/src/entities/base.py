import pymunk

class BaseEntity:
    """Basisklasse für alle physischen Objekte."""
    def __init__(self, space, rng):
        self.space = space
        self.rng = rng
        self.body = None
        self.shapes = []

    def remove(self):
        """Entfernt die Entity aus dem Pymunk-Space."""
        for shape in self.shapes:
            self.space.remove(shape)
        if self.body:
            self.space.remove(self.body)
