# Die Audio-Engine

Die Audio-Engine ist eine generische Synthese-Einheit, die keine szenespezifische Logik enthält.

## 1. Funktionsweise (`src/engines/audio.py`)

- Arbeitet mit einem PCM-WAV-Buffer (44.1 kHz).
- Bietet die Methode `play_sound(t, params)`, die rein datengesteuert arbeitet.
- Nutzt `math.tanh` für Soft-Clipping und Schutz vor Verzerrung.

## 2. Audio-Profile (`src/audio_profiles/`)

Jedes Profil berechnet aus einem physikalischen Impuls die Synthese-Parameter:

| Profil | Sound-Charakter | Einsatzgebiet |
|---|---|---|
| `ImpactProfile` | Klickend, metallisch/hölzern | Ball Pit, Kollisionen |
| `LiquidProfile` | Blubbernd, tieffrequent | Lava Lamp, DNA |

## 3. Parameter-Mapping

Eine Szene liefert folgende Parameter an die Engine:
- `freq`: Basis-Frequenz in Hz.
- `duration`: Länge in Sekunden.
- `noise_level`: Anteil des initialen Klick-Geräusches.
- `pitch_drop`: Wie stark die Frequenz über die Zeit abfällt.
- `inharmonicity`: Multiplikator für unharmonische Obertöne.
