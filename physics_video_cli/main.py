import os
import sys
import random
from src.cli_handler import parse_args
from src.utils_ffmpeg import Utils
from src.engine_world import WorldGenerator
from src.engines.simulation import SimulationEngine
from src.engines.audio import AudioEngine
from src.engines.rendering import RenderingEngine

def interactive_menu():
    print("=" * 60)
    print("       AUDIOVISUELLER PHYSIK-SIMULATOR (CLI)       ")
    print("=" * 60)
    print("Wähle eine Physik-Welt aus:")
    print("  1. Bälle-Parcours (ball_pit)")
    print("  2. Lava-Lampe (lava_lamp)")
    print("  3. DNA-Helix (dna_helix)")
    print("-" * 60)
    
    choice = input("Wähle eine Welt (1-3): ").strip()
    mapping = {"1": "ball_pit", "2": "lava_lamp", "3": "dna_helix"}
    scene_profile = mapping.get(choice, "ball_pit")
        
    seed = input("Seed (Enter für Zufall): ").strip()
    seed = int(seed) if seed else random.randint(1, 999999)
        
    duration = input("Dauer in s (Standard 60.0): ").strip()
    duration = float(duration) if duration else 60.0
    
    return seed, scene_profile, duration, 60, "1080x1920", "output"

def main():
    if len(sys.argv) > 1:
        args = parse_args()
        seed, scene_profile, duration = args.seed or random.randint(1, 999999), args.scene_profile, args.duration
        fps, resolution, output_name = args.fps, args.resolution, args.output_name
    else:
        seed, scene_profile, duration, fps, resolution, output_name = interactive_menu()
    
    temp_dir = os.path.abspath("temp_frames")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # 1. World & Scene Factory
    wg = WorldGenerator(seed, scene_profile)
    scene = wg.generate()
    
    # 2. Engines Initialisierung
    audio_file = os.path.join(temp_dir, "audio.wav")
    audio_engine = AudioEngine(audio_file, duration)
    rendering_engine = RenderingEngine(resolution)
    
    # 3. Simulation Runner
    sim_engine = SimulationEngine(scene, audio_engine, rendering_engine)
    
    utils = Utils(temp_dir=temp_dir)
    
    try:
        print(f"Starte Generierung: {scene_profile} (Seed: {seed})")
        sim_engine.run(duration, fps, temp_dir)
        
        # 4. Video Export
        output_filename = f"{output_name}_{seed}_{scene_profile}.mp4"
        output_path = os.path.abspath(os.path.join("output", "videos", output_filename))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        utils.create_video(output_path, fps, resolution)
        print(f"\n[ERFOLG] Video: {output_path}")
        
    finally:
        # Cleanup erst am Ende
        utils.cleanup()
        print("Bereinigung der temporären Dateien abgeschlossen.")

if __name__ == "__main__":
    main()
