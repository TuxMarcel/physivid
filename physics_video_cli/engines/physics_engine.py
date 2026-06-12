import pymunk
from engines.base import Engine

class PhysicsEngine(Engine):
    def step(self, dt: float) -> None:
        self.space.step(dt)
        self.time += dt
