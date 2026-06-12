import os
import sys
import argparse
import random
import subprocess
import importlib
from core.registry import list_all, get
from renderer.pygame_capturer import PygameCapturer
from audio.synthesizer import Synthesizer
from audio.mixer import write_wav

def _discover():
    """Importiert alle Welten aus dem worlds/-Verzeichnis zur automatischen Registrierung."""
    worlds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worlds")
    if not os.path.exists(worlds_dir):
        return
    # Top-level modules
    for f in os.listdir(worlds_dir):
        if f.endswith(".py") and not f.startswith("__"):
            module_name = f"worlds.{f[:-3]}"
            importlib.import_module(module_name)
    # Subdirectories (packages)
    for d in os.listdir(worlds_dir):
        dir_path = os.path.join(worlds_dir, d)
        if os.path.isdir(dir_path) and not d.startswith("__"):
            scene_file = os.path.join(dir_path, "scene.py")
            if os.path.exists(scene_file):
                module_name = f"worlds.{d}.scene"
                importlib.import_module(module_name)

def interactive_menu():
    print("=" * 60)
    print("       AUDIOVISUELLER PHYSIK-SIMULATOR (CLI)       ")
    print("=" * 60)
    print("Verfügbare Welten:")
    
    experiments = list_all()
    keys = list(experiments.keys())
    for idx, key in enumerate(keys, 1):
        desc = experiments[key].description
        print(f"  {idx}. {key} — {desc}")
    print("-" * 60)
    
    choice = input(f"Wähle ein Experiment (1-{len(keys)}): ").strip()
    try:
        scene_profile = keys[int(choice) - 1]
    except Exception:
        scene_profile = keys[0]
        
    seed = input("Seed (Enter für Zufall): ").strip()
    seed = int(seed) if seed else random.randint(1, 999999)
        
    duration = input("Dauer in s (Standard 10.0): ").strip()
    duration = float(duration) if duration else 10.0
    
    fps = input("FPS (Standard 60): ").strip()
    fps = int(fps) if fps else 60
    
    resolution = input("Auflösung (Standard 1080x1920): ").strip()
    resolution = resolution if resolution else "1080x1920"
    
    return seed, scene_profile, duration, fps, resolution, "output"

def run_experiment(experiment_name, seed, duration, fps, resolution, output_path):
    # 1. Experiment instanziieren
    experiment_cls = get(experiment_name)
    experiment = experiment_cls(seed)
    
    # Setup durchführen (baut Space auf)
    experiment.setup()
    
    # 2. Renderer & Audio initialisieren
    capturer = PygameCapturer(resolution)
    sample_rate = 44100
    synthesizer = Synthesizer(sample_rate, seed, duration)
    
    # Ambient Sound Pad Layer hinzufügen
    synthesizer.add_pad_layer(duration)
    
    # Register collision hooks
    def _on_collision(arbiter, space, data):
        experiment.handle_collisions(arbiter, synthesizer.time, synthesizer)
        
    experiment.space.on_collision(post_solve=_on_collision)
    
    # 3. FFmpeg-Subprozess für Video-Encoding starten
    # Auto-detection für Encoder
    video_codec = "libx264"
    try:
        res = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True)
        if "h264_nvenc" in res.stdout:
            video_codec = "h264_nvenc"
    except Exception:
        pass

    temp_video_path = os.path.abspath("temp_video.mp4")
    temp_audio_path = os.path.abspath("temp_audio.wav")
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", resolution,
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",  # stdin
        "-c:v", video_codec,
        "-pix_fmt", "yuv420p",
        temp_video_path
    ]
    
    print(f"Starte Echtzeit-Rendering & Video-Pipe (Codec: {video_codec})...")
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    num_frames = int(duration * fps)
    dt = 1.0 / fps
    
    try:
        for frame in range(num_frames):
            current_time = frame * dt
            synthesizer.time = current_time
            
            # Hooks
            experiment.pre_step(dt)
            
            # Physik-Schritt
            experiment.space.step(dt)
            
            # Hooks
            experiment.post_step(dt)
            
            # Frame rendern & direkt an FFmpeg senden (im RAM!)
            frame_arr = capturer.render_frame(experiment.space, experiment)
            ffmpeg_proc.stdin.write(frame_arr.tobytes())
            
            # Statusanzeige
            if frame % max(1, num_frames // 10) == 0 or frame == num_frames - 1:
                progress = int((frame + 1) / num_frames * 100)
                print(f"Fortschritt: {progress}% ({frame + 1}/{num_frames} Frames)", end="\r")
                sys.stdout.flush()
                
        print("\nRendering abgeschlossen. Finalisiere Video und Audio...")
    finally:
        # Pipe schließen und auf FFmpeg warten
        if ffmpeg_proc.stdin:
            ffmpeg_proc.stdin.close()
        ffmpeg_proc.wait()
        
    # 4. Audio-Datei schreiben
    write_wav(temp_audio_path, synthesizer.buffer, sample_rate)
    
    # 5. Remux Video + Audio
    print("Mische Video- und Audio-Spuren zusammen...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    merge_cmd = [
        "ffmpeg",
        "-y",
        "-i", temp_video_path,
        "-i", temp_audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    subprocess.run(merge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # 6. Cleanup temporärer Dateien
    for temp_file in [temp_video_path, temp_audio_path]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"Deleted temp file: {temp_file}")
            except Exception as e:
                print(f"Failed to delete {temp_file}: {e}")

def main():
    _discover()
    
    parser = argparse.ArgumentParser(description="Deterministischer Audiovisueller Physik-Simulator")
    parser.add_argument("--seed", type=int, default=None, help="Zufalls-Seed")
    parser.add_argument("--duration", type=float, default=None, help="Videolänge in Sekunden")
    parser.add_argument("--fps", type=int, default=60, help="Bilder pro Sekunde")
    parser.add_argument("--resolution", type=str, default="1080x1920", help="Auflösung (WxH)")
    parser.add_argument("--output_name", type=str, default="output", help="Ausgabename")
    parser.add_argument("--scene_profile", type=str, default=None, help="Szene (ball_pit, lava_lamp, dna_helix)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Direkter Zielpfad für das MP4")
    parser.add_argument("--list", action="store_true", help="Listet alle verfügbaren Szenen auf")
    
    args = parser.parse_args()
    
    if args.list:
        print("Verfügbare Szenen:")
        for name, cls in list_all().items():
            print(f"  {name}: {cls.description}")
        return
        
    # Interactive mode or CLI mode
    if len(sys.argv) == 1:
        seed, scene_profile, duration, fps, resolution, output_name = interactive_menu()
        output_path = os.path.abspath(os.path.join("output", "videos", f"{output_name}_{seed}_{scene_profile}.mp4"))
    else:
        seed = args.seed if args.seed is not None else random.randint(1, 999999)
        scene_profile = args.scene_profile if args.scene_profile else "ball_pit"
        duration = args.duration if args.duration is not None else 10.0
        fps = args.fps
        resolution = args.resolution
        
        if args.output:
            output_path = os.path.abspath(args.output)
        else:
            output_path = os.path.abspath(os.path.join("output", "videos", f"{args.output_name}_{seed}_{scene_profile}.mp4"))
            
    print(f"\nGeneriere Physik-Video: {scene_profile}")
    print(f"Seed: {seed} | Dauer: {duration}s | FPS: {fps} | Resolution: {resolution}")
    print(f"Zielpfad: {output_path}\n")
    
    run_experiment(scene_profile, seed, duration, fps, resolution, output_path)
    print(f"\n[ERFOLG] Video erfolgreich gerendert: {output_path}")

if __name__ == "__main__":
    main()
