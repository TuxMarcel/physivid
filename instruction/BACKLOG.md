# Physivid - Backlog, Optimierungen & Offene Aufgaben

Diese Datei dokumentiert alle geplanten Features, bekannten Optimierungspotenziale und Design-Entscheidungen für zukünftige Versionen.

---

## WICHTIGE ENTWICKLER-RICHTLINIE
> [!IMPORTANT]
> **Jeder Entwickler, der dieses Projekt modifiziert, erweitert oder Bugs behebt, MUSS die Dokumentation in der `README.md` und dieser `BACKLOG.md` pflegen!**

---

## 1. Zukünftige Features (Roadmap)

### Domino-Effekt-Szene
- **Ziel**: Eine Kaskade von fallenden Domino-Steinen (Segment- oder Polygon-Entities), die eine Kettenreaktion auslösen.
- **Anforderung**: Präziser physikalischer Aufbau der Steine über Joints oder exakt positionierte Polygon-Körper.

### Metaballs für Lava-Lampe
- **Ziel**: Weiches Verschmelzen der Lava-Blobs beim Rendern anstelle von sich überschneidenden Kreisen.
- **Technischer Ansatz**: Pixel-Shader oder Marching-Cubes-ähnliche Interpolation auf der Pygame-Surface, um die Blobs organisch wirken zu lassen.

### Zusätzliche Welten & Constraints
- Verknüpfte Federgelenke (Spring Joints) für elastische Netze oder weiche Körper (Softbodies).

---

## 2. Bekannte Optimierungspotenziale & Performance

### Trail-Konfigurierbarkeit
- **Status**: Die Leuchtspuren (Trails) sind derzeit teilweise fest verdrahtet (Länge 5–10).
- **Ziel**: Trails über CLI-Argumente oder szenenspezifische Konfigurationen anpassbar machen (Farbe, Transparenzverlauf, Länge).

### FFmpeg Validierung
- **Status**: Wenn FFmpeg im Systempfad fehlt, stürzt das Skript mit einem Fehler ab.
- **Ziel**: Ein sauberer Check beim Startup mit einer aussagekräftigen Fehlermeldung, falls FFmpeg nicht installiert ist.

### Flexiblere Audio-Profile
- **Status**: Neue Szenen nutzen das standardmäßige `ImpactProfile`.
- **Ziel**: Generische XML/YAML-basierte oder programmatische Audio-Profile für flexiblere Klangsynthese.
