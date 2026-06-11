import os
import subprocess
import shutil

class Utils:
    def __init__(self, temp_dir="temp_frames"):
        self.temp_dir = temp_dir
        self.ensure_temp_dir()

    def ensure_temp_dir(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_video(self, output_path, fps, resolution):
        """
        Uses FFmpeg to create an MP4 from frames and audio.
        Assumes frame sequence is frame_%05d.png in temp_dir.
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # FFmpeg command:
        # -i input_pattern: frames
        # -i audio: wav
        # -c:v libx264: video codec
        # -pix_fmt yuv420p: compatibility
        # -r: fps
        
        frame_pattern = os.path.join(self.temp_dir, "frame_%05d.png")
        audio_path = os.path.join(self.temp_dir, "audio.wav")
        
        cmd = [
            "ffmpeg",
            "-framerate", str(fps),
            "-i", frame_pattern,
            "-i", audio_path,
            "-c:v", "h264_nvenc",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={resolution}", # Force resolution
            "-c:a", "aac",
            "-strict", "experimental",
            "-y", # Overwrite output
            output_path
        ]
        
        subprocess.run(cmd, check=True)
