# Physivid - Modulares 2D Physik-Simulations- & Render-Framework

Physivid ist ein performantes Python-Framework zur Generierung von 2D-Physiksimulationen mit deterministischer Video- und Audioausgabe. Es nutzt **Pymunk** für die Physik, **Pygame** für das headless Rendering direkt im RAM und **FFmpeg** zur Echtzeit-MP4-Kodierung über Memory-Pipes (ohne temporäre Bilddateien auf der Festplatte).

Jede Simulation ist durch einen **Seed** deterministisch reproduzierbar.

---

## WICHTIGE ENTWICKLER-RICHTLINIE
> [!IMPORTANT]
> **Jeder, der an diesem Projekt arbeitet, ist verpflichtet, diese Dokumentation aktuell zu halten und zu pflegen!** Änderungen an der Architektur, neue Parameter oder zusätzliche Module müssen unverzüglich hier und im Backlog dokumentiert werden.

---

## Projektstruktur

Das Framework ist in einen Kern (**Core**), wiederverwendbare Bausteine (**Entities**) und konkrete Szenarien (**Worlds**) unterteilt.

```
physics_video_cli/
├── main.py                  # CLI + interaktives Menü (Einstiegspunkt)
│
├── core/                    # DAS HERZ (Framework-Kern)
│   ├── experiment.py        # Abstrakte Basisklasse für alle Szenen
│   ├── entity.py            # Basisklasse für physikalische Objekte (Body + Shape + Trail)
│   └── registry.py          # Dynamische Entdeckung von Welten
│
├── entities/                # BAUSTEINE (Wiederverwendbare Objekte)
│   ├── shapes.py            # Grundformen: Circle, Polygon, Segment
│   └── lava_blob.py         # Komplexe Entität mit Convection-Logik
│
├── worlds/                  # INHALTE (Szenen-Definitionen)
│   ├── ball_pit/            # Beispiel für eine komplexe Welt als Paket
│   │   ├── scene.py         # Die Experiment-Klasse
│   │   └── components.py    # Szenenspezifische Hilfsfunktionen
│   ├── lava_lamp.py         # Eigenständige Szenen-Datei
│   └── dna_helix.py         # Eigenständige Szenen-Datei
│
├── renderer/                # Visualisierung
│   └── pygame_capturer.py   # Headless Rendering (NumPy -> FFmpeg Pipe)
│
├── audio/                   # Klangsynthese
│   ├── synthesizer.py       # FM/Subtraktive Synthese + Pentatonik
│   └── profiles/            # Szenenspezifische Sound-Parameter
│
└── utils/                   # Helfer
    └── colors.py            # Dynamische Farbpaletten
```

---

## Bedienung & CLI

Aktivierung des Virtualenvs:
```bash
source venv/bin/activate
```

### Interaktiver Modus
```bash
python main.py
```

### CLI-Modus
```bash
# Startet den Bälle-Parcours mit bestimmten Parametern
python main.py --scene_profile ball_pit --seed 42 --duration 15.0 --fps 60 --resolution 1080x1920

# Direktes Festlegen des Dateinamens
python main.py --scene_profile lava_lamp -o output.mp4
```

| Parameter | CLI-Flag | Standard | Beschreibung |
|---|---|---|---|
| Seed | `--seed` | Zufällig | Seed für den deterministischen Zufall |
| Dauer | `--duration` | 10.0 | Videodauer in Sekunden |
| FPS | `--fps` | 60 | Ziel-Bilder pro Sekunde |
| Auflösung | `--resolution` | "1080x1920" | Ausgabegröße "BxH" |
| Profil | `--scene_profile`| "ball_pit" | ball_pit, lava_lamp, dna_helix |
| Output | `-o`/`--output` | automatisch | Ausgabepfad |

---

## Funktionsweise des Renderers (RAM-Streaming)

Um maximale Performance zu erzielen, speichert Physivid **keine** PNG-Frames auf der SSD. 
1. Der Renderer zeichnet die physikalische Welt auf eine Pygame Headless-Surface.
2. Das Bild wird per `pygame.surfarray.array3d()` im RAM als raw NumPy-Array erfasst.
3. Dieses Array wird direkt in den `stdin`-Stream eines im Hintergrund laufenden FFmpeg-Prozesses geschrieben.
4. FFmpeg kodiert das Video in Echtzeit. Am Ende werden die synthetisierte Audiospur (WAV) und die Videospur verlustfrei gemuxt.
