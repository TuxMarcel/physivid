import pymunk

class BaseScene:
    """Abstrakte Basisklasse für alle Szenen."""
    def __init__(self, space, rng, palette):
        self.space = space
        self.rng = rng
        self.palette = palette
        self.audio_profile = None

    def setup(self):
        """Initialisiert die Welt-Geometrie und Entities."""
        raise NotImplementedError("Subclasses must implement setup")

    def update(self, frame, dt):
        """Per-Frame Logik (Spawning, Recycling, etc.)."""
        pass

    def handle_collisions(self, arbiter, current_time, audio_engine):
        """Behandelt Kollisionen und triggert Audio."""
        if not self.audio_profile:
            return

        impulse = arbiter.total_impulse.length
        # Jede Szene kann ihren eigenen Schwellenwert definieren
        if impulse > self.get_impulse_threshold():
            params = self.audio_profile.get_params(impulse)
            audio_engine.play_sound(current_time, params)

    def get_impulse_threshold(self):
        """Gibt den minimalen Impuls für einen Sound zurück."""
        return 10.0
