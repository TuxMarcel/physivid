import pymunk
import random

class BaseScene:
    def __init__(self, space, rng, palette):
        self.space = space
        self.rng = rng
        self.palette = palette

    def setup(self):
        """
        Set up boundaries, static obstacles, kinematic spinners, and initial entities.
        """
        pass

    def update(self, frame, dt):
        """
        Hook called at the start of each physics frame step.
        Useful for dynamic object spawning, gravity shifts, etc.
        """
        pass
