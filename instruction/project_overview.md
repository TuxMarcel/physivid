# Modulare Physik-Video-Pipeline (Physivid)

Diese Dokumentation beschreibt die Architektur der hochgradig modularen Video-Generierungs-Pipeline.

## 1. Architektur-Prinzipien

- **Strikte Entkopplung:** Kern-Engines wissen nichts über den Inhalt der Szenen.
- **Klassen-basierte Struktur:** Jede Komponente (Engine, Szene, Entity, Audio-Profil) ist eine eigenständige Klasse.
- **Scene Ownership:** Szenen besitzen ihre eigene Physik (Gravity), Kollisions-Logik und Sound-Charakteristik.
- **Determinisierung:** Alles wird über einen einzigen `seed` gesteuert.

## 2. Ordnerstruktur

- `src/engines/`: Generische Kern-Engines (`simulation.py`, `audio.py`, `rendering.py`).
- `src/scenes/`: Orchestrierung der Welten (`base.py`, `ball_pit.py`, etc.).
- `src/entities/`: Physische Objekte als Klassen (`ball_pit_entities.py`, `lava_entities.py`).
- `src/audio_profiles/`: Sound-Modelle (`impact_profile.py`, `liquid_profile.py`).

## 3. Workflow der Pipeline

1. **`main.py`** erfasst User-Input und instanziiert die Engines.
2. **`WorldGenerator`** erstellt dynamisch die gewünschte Szene.
3. **`SimulationEngine`** taktet die Simulation und delegiert Kollisionen an die Szene.
4. **`AudioEngine`** synthetisiert Sounds basierend auf den Parametern des Szenen-Audio-Profils.
5. **`RenderingEngine`** zeichnet den physischen Zustand in PNG-Frames.
6. **`FFmpeg`** fügt Frames und Audio zum finalen MP4 zusammen.
