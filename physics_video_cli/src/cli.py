import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Deterministic Audiovisual Physics CLI Tool")
    
    parser.add_argument("--seed", type=int, default=None, help="Seed for world generation (optional, will generate randomly if omitted)")
    parser.add_argument("--duration", type=float, default=60.0, help="Video duration in seconds")
    parser.add_argument("--fps", type=int, default=60, help="Frames per second")
    parser.add_argument("--resolution", type=str, default="1080x1920", help="Resolution (WxH)")
    parser.add_argument("--output_name", type=str, default="output", help="Base name for the output file")
    parser.add_argument("--scene_profile", type=str, default="ball_pit", choices=["ball_pit", "lava_dna"], help="Simulation scenario")
    
    return parser.parse_args()
