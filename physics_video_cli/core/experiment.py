from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pymunk

class Experiment(ABC):
    name: str = ""
    description: str = ""

    def __init__(self, seed: int):
        self.seed = seed
        self.space: pymunk.Space = pymunk.Space()
        self.entities: List[Any] = []
        self.audio_profile: Any = None
        self.rng: Any = None
        self.palette: List[tuple] = []

    @abstractmethod
    def setup(self) -> None:
        """Welt aufbauen (Entities und Constraints erzeugen)"""
        pass

    @abstractmethod
    def get_duration(self) -> float:
        """Gibt die Dauer des Videos in Sekunden zurück."""
        pass

    def pre_step(self, dt: float) -> None:
        """Hook vor dem Physik-Schritt."""
        pass

    def post_step(self, dt: float) -> None:
        """Hook nach dem Physik-Schritt (z.B. Trail-Updates). Konkrete Experimente sollten super().post_step(dt) aufrufen."""
        for entity in self.entities:
            if hasattr(entity, "update_trail"):
                entity.update_trail()

    def get_visual_data(self) -> Dict[str, Any]:
        """Gibt zusätzliche visuelle Daten für den Renderer zurück (z.B. Linien, Lager, Grid)."""
        return {}

    def handle_collisions(self, arbiter: pymunk.Arbiter, current_time: float, audio_engine: Any) -> None:
        """Behandelt Kollisionen und triggert Audio-Synthese."""
        if not self.audio_profile:
            return

        shapes = arbiter.shapes
        # Prüfen, ob einer der Kollisionspartner ein dynamisches Objekt ist (hat trail_len)
        has_dynamic = any(hasattr(shape.body, 'trail_len') for shape in shapes)
        if not has_dynamic:
            return

        impulse = arbiter.total_impulse.length
        if impulse > self.get_impulse_threshold():
            params = self.audio_profile.get_params(impulse)
            audio_engine.play_sound(current_time, params)

    def get_impulse_threshold(self) -> float:
        """Gibt den minimalen Impuls für einen Sound zurück."""
        return 10.0
