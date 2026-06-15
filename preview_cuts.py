"""
Usage:
  python preview_cuts.py --video myvideo.mp4 --cuts cuts.json
  python preview_cuts.py --video myvideo.mp4 --cuts '[{"scene":1,"start":0.0,"end":2.5},...]'

GIFs are saved to ./preview_cuts/ with filenames that include timestamps.
Review them, correct the JSON if needed, then run Prompt 2.
"""
import json, argparse, subprocess, os, sys

def make_gif(video, start, dur, out, width=360, fps=12):
    if dur <= 0:
        print(f"  skipped (zero duration)")
        return
    palette = out.replace('.gif', '_p.png')
    subprocess.run([
        "ffmpeg","-y","-ss",str(start),"-t",str(dur),"-i",video,
        "-vf",f"fps={fps},scale={width}:-1:flags=lanczos,palettegen",
        "-loglevel","error", palette
    ], check=True)
    subprocess.run([
        "ffmpeg","-y","-ss",str(start),"-t",str(dur),"-i",video,"-i",palette,
        "-lavfi",f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
        "-loglevel","error", out
    ], check=True)
    os.remove(palette)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True, help="Path to source video")
    p.add_argument("--cuts", required=True, help="JSON array or path to .json file")
    p.add_argument("--out", default="preview_cuts", help="Output folder (default: preview_cuts)")
    p.add_argument("--width", type=int, default=360, help="GIF width in px (default: 360)")
    p.add_argument("--fps", type=int, default=12, help="GIF fps (default: 12)")
    args = p.parse_args()

    # Accept either a raw JSON string or a path to a .json file
    if os.path.isfile(args.cuts):
        cuts = json.load(open(args.cuts))
    else:
        cuts = json.loads(args.cuts)

    os.makedirs(args.out, exist_ok=True)

    print(f"\n{len(cuts)} scenes detected. Generating GIFs → ./{args.out}/\n")

    for c in cuts:
        i, start, end = c["scene"], c["start"], c["end"]
        dur = round(end - start, 3)
        out = os.path.join(args.out, f"scene_{i:02d}_{start:.2f}-{end:.2f}.gif")
        print(f"  Scene {i:>2}: {start:>7.2f}s → {end:>7.2f}s  ({dur:.2f}s) ...", end=" ", flush=True)
        try:
            make_gif(args.video, start, dur, out, width=args.width, fps=args.fps)
            size_kb = os.path.getsize(out) // 1024
            print(f"✓  {size_kb} KB")
        except subprocess.CalledProcessError as e:
            print(f"FAILED: {e}")

    print(f"\nDone. Review GIFs in ./{args.out}/, correct JSON if needed, then run Prompt 2.")

if __name__ == "__main__":
    main()
