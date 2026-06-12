from abc import ABC, abstractmethod
import pymunk

class Engine(ABC):
    def __init__(self, space: pymunk.Space):
        self.space = space
        self.time = 0.0

    @abstractmethod
    def step(self, dt: float) -> None:
        pass

    def reset(self) -> None:
        self.time = 0.0
