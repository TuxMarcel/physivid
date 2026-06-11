# Die Simulation-Engine

Die `SimulationEngine` (`src/engines/simulation.py`) ist das Herzstück der Pipeline, fungiert aber rein als Orchestrator.

## 1. Aufgaben

1. **Zeittaktung:** Berechnet die Frames und die physikalischen Zeitschritte (`dt`).
2. **Physik-Steuerung:** Ruft `space.step(dt)` auf.
3. **Kollisions-Delegation:** Registriert einen globalen Kollisions-Handler, leitet aber jeden Aufprall an `scene.handle_collisions()` weiter.
4. **Rendering-Trigger:** Ruft nach jedem Schritt den Renderer auf.

## 2. Abstraktion

Die Engine besitzt keine Referenzen auf szenespezifische Objekte wie "Bälle" oder "Blobs". Sie interagiert ausschließlich über die abstrakten Schnittstellen von `BaseScene`.
