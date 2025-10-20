"""
여러 소스 mp4가 코덱/프레임레이트/해상도가 혼재할 경우 uniform 폴더에
1920x1080 30fps H.264로 재인코딩.

사용:
  python scripts/create_uniform_videos.py
출력:
  work/uniform/*.mp4
"""
import subprocess
from pathlib import Path

SRC_DIRS = [Path("work/sequences"), Path("work/slow"), Path("raw/video")]
OUT_DIR  = Path("work/uniform")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "ffmpeg"

def transcode(src):
    out = OUT_DIR / (src.stem + "_u.mp4")
    cmd = [
        FFMPEG, "-y",
        "-i", src.as_posix(),
        "-vf", "scale=1920:1080:flags=lanczos,fps=30",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        out.as_posix()
    ]
    print("[CMD]", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if p.returncode == 0:
        print(f"[OK] {src.name} -> {out.name}")
    else:
        print(f"[FAIL] {src.name}")

all_mp4 = []
for d in SRC_DIRS:
    if not d.exists():
        continue
    for f in d.glob("*.mp4"):
        all_mp4.append(f)

print(f"[INFO] Found mp4 files: {len(all_mp4)}")
for f in all_mp4:
    transcode(f)

print("[INFO] Uniform transcode complete.")