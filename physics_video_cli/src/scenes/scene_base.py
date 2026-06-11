import pymunk
import random

class BaseScene:
    def __init__(self, space, rng, palette):
        self.space = space
        self.rng = rng
        self.palette = palette

    def setup(self):
        pass

    def update(self, frame, dt):
        pass
