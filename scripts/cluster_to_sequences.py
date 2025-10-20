import csv, os, shutil, subprocess
from pathlib import Path
from PIL import Image
import imageio_ffmpeg

CLUSTER_CSV = Path("metadata/photo_clusters.csv")
RAW_PHOTO   = Path("raw/photo")
SEQ_DIR     = Path("work/sequences")
SEQ_DIR.mkdir(parents=True, exist_ok=True)

MIN_COUNT = 3
FR_FAST   = 8
FR_SLOW   = 5
CONVERT_PNG = True  # png → jpg 변환 여부

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def run(cmd):
    print("[CMD]", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (code={p.returncode})")

clusters = []
with open(CLUSTER_CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        clusters.append({
            "id": int(row["cluster_id"]),
            "count": int(row["count"]),
            "files": [f for f in row["filenames"].split(";") if f.strip()]
        })

selected = [c for c in clusters if c["count"] >= MIN_COUNT]
print(f"[INFO] Total clusters={len(clusters)} | Selected(>= {MIN_COUNT})={len(selected)}")

if not selected:
    print("[WARN] No clusters meet MIN_COUNT. Adjust MIN_COUNT or inspect cluster CSV.")
    exit(0)

for c in selected:
    cid   = c["id"]
    files = c["files"]
    folder = SEQ_DIR / f"cluster{cid}"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    copied = 0
    for fname in files:
        src = RAW_PHOTO / fname
        if not src.exists(): 
            continue
        ext = src.suffix.lower()
        if ext in [".jpg",".jpeg",".png"]:
            # png 변환
            if CONVERT_PNG and ext == ".png":
                try:
                    im = Image.open(src).convert("RGB")
                    jpg_path = folder / (src.stem + ".jpg")
                    im.save(jpg_path, quality=95)
                    copied += 1
                except Exception as e:
                    print(f"[WARN] PNG convert fail {fname}: {e}")
            else:
                shutil.copy(src, folder / fname)
                copied += 1

    if copied == 0:
        print(f"[WARN] cluster {cid} has no convertible images")
        continue

    joined = " ".join(files).lower()
    if any(k in joined for k in ["run","race","tug","rope","highfive","cheer"]):
        fr = FR_FAST
    else:
        fr = FR_SLOW

    # glob 대상: jpg만
    folder_glob = folder.as_posix() + "/*.jpg"
    out_mp4 = SEQ_DIR / f"cluster{cid}_seq.mp4"
    cmd = [
        FFMPEG, "-y",
        "-pattern_type","glob",
        "-i", folder_glob,
        "-framerate", str(fr),
        "-vf","scale=1920:-1:flags=lanczos,format=yuv420p",
        str(out_mp4)
    ]
    try:
        run(cmd)
        print(f"[OK] cluster {cid} -> {out_mp4.name} (fr={fr}, images={copied})")
    except Exception as e:
        print(f"[FAIL] cluster {cid}: {e}")

print("[INFO] Sequence generation complete.")