import os
import sys
import random
from src.cli_handler import parse_args
from src.utils_ffmpeg import Utils
from src.engine_sim import SimulationEngine

def interactive_menu():
    print("=" * 60)
    print("       AUDIOVISUELLER PHYSIK-SIMULATOR (CLI)       ")
    print("=" * 60)
    print("Wähle eine Physik-Welt aus:")
    print("  1. Bälle-Parcours (ball_pit) - Plinko-Pins, Bälle, rotierende Spinner")
    print("  2. Lava-Lampe (lava_lamp) - Sanft schwebende Farbblobs")
    print("  3. [Zukünftig] DNA-Helix (dna_helix)")
    print("  4. [Zukünftig] Domino-Effekt (domino_effect)")
    print("-" * 60)
    
    choice = input("Wähle eine Welt (1-2, Standard 1): ").strip()
    if choice == "2":
        scene_profile = "lava_lamp"
    elif choice == "3":
        print("DNA-Helix ist noch nicht implementiert. Nutze Bälle-Parcours.")
        scene_profile = "ball_pit"
    elif choice == "4":
        print("Domino-Effekt ist noch nicht implementiert. Nutze Bälle-Parcours.")
        scene_profile = "ball_pit"
    else:
        scene_profile = "ball_pit"
        
    print(f"\nAusgewählte Welt: {scene_profile}")
    
    seed_input = input("Seed eingeben (optional, Enter für zufälligen Seed): ").strip()
    if seed_input:
        try:
            seed = int(seed_input)
        except ValueError:
            print("Ungültiger Seed. Ein zufälliger Seed wird generiert.")
            seed = random.randint(1, 999999)
    else:
        seed = random.randint(1, 999999)
        
    duration_input = input("Videodauer in Sekunden (Standard 60.0): ").strip()
    try:
        duration = float(duration_input) if duration_input else 60.0
    except ValueError:
        print("Ungültige Dauer. Standard von 60.0 Sekunden wird verwendet.")
        duration = 60.0
        
    # Standardwerte für FPS und Auflösung
    fps = 60
    resolution = "1080x1920"
    output_name = "output"
    
    return seed, scene_profile, duration, fps, resolution, output_name

def main():
    # If terminal arguments are provided, use argparse, else show the interactive menu
    if len(sys.argv) > 1:
        args = parse_args()
        seed = args.seed
        if seed is None:
            seed = random.randint(1, 999999)
        scene_profile = args.scene_profile
        duration = args.duration
        fps = args.fps
        resolution = args.resolution
        output_name = args.output_name
    else:
        seed, scene_profile, duration, fps, resolution, output_name = interactive_menu()
        
    print("\n" + "=" * 60)
    print(f"Starte Simulation:")
    print(f"  - Welt:       {scene_profile}")
    print(f"  - Seed:       {seed}")
    print(f"  - Dauer:      {duration}s")
    print(f"  - FPS:        {fps}")
    print(f"  - Auflösung:  {resolution}")
    print("=" * 60 + "\n")
    
    # Initialize utilities
    temp_dir = "temp_frames"
    utils = Utils(temp_dir=temp_dir)
    
    try:
        # Run Simulation
        engine = SimulationEngine(seed, scene_profile, resolution, temp_dir, duration)
        engine.run(duration, fps)
        
        # Assemble Video
        output_filename = f"{output_name}_{seed}_{scene_profile}.mp4" if output_name == "output" else f"{output_name}_{seed}.mp4"
        output_file = os.path.join("output", "videos", output_filename)
        utils.create_video(output_file, fps, resolution)
        print(f"\n[ERFOLG] Video wurde gespeichert unter: {output_file}")
        
    finally:
        utils.cleanup()
        print("Bereinigung der temporären Dateien abgeschlossen.")

if __name__ == "__main__":
    main()
