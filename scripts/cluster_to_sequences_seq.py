"""
군집 CSV를 읽어 각 군집을 순차 번호 img_0000.jpg 로 리네임/변환 후 시퀀스 mp4 생성.
PNG → JPG 변환 가능. glob 기능 미지원 빌드 대응을 위해 %04d 패턴 사용.

사용:
  python scripts/cluster_to_sequences_seq.py
출력:
  work/sequences/clusterX_seq.mp4 (군집별)
"""
import csv, os, shutil, subprocess
from pathlib import Path
from PIL import Image
import imageio_ffmpeg

CLUSTER_CSV = Path("metadata/photo_clusters.csv")
RAW_PHOTO   = Path("raw/photo")
SEQ_DIR     = Path("work/sequences")
SEQ_DIR.mkdir(parents=True, exist_ok=True)

MIN_COUNT = 3          # 시퀀스로 만들 최소 이미지 수(필요시 조정)
FR_FAST   = 8
FR_SLOW   = 5
FFMPEG    = imageio_ffmpeg.get_ffmpeg_exe()

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
        files = [f for f in row["filenames"].split(";") if f.strip()]
        clusters.append({"id": int(row["cluster_id"]), "count": int(row["count"]), "files": files})

selected = [c for c in clusters if c["count"] >= MIN_COUNT]
print(f"[INFO] Total clusters={len(clusters)} | Selected(>= {MIN_COUNT})={len(selected)}")

if not selected:
    print("[WARN] No clusters meet MIN_COUNT.")
    exit(0)

for c in selected:
    cid   = c["id"]
    files = c["files"]
    folder = SEQ_DIR / f"cluster{cid}"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)

    copied_files = []
    idx = 0
    for fname in files:
        src = RAW_PHOTO / fname
        if not src.exists():
            continue
        ext = src.suffix.lower()
        if ext in [".png",".jpg",".jpeg",".JPG",".JPEG",".PNG"]:
            target_name = f"img_{idx:04d}.jpg"
            dst = folder / target_name
            try:
                if ext in [".png",".PNG"]:
                    im = Image.open(src).convert("RGB")
                    im.save(dst, quality=95)
                else:
                    # jpg/jpeg는 바로 복사 후 이름만 맞춤
                    im = Image.open(src).convert("RGB")
                    im.save(dst, quality=95)
                copied_files.append(dst)
                idx += 1
            except Exception as e:
                print(f"[WARN] conversion fail {fname}: {e}")

    if len(copied_files) < 2:
        print(f"[INFO] cluster {cid}: only {len(copied_files)} image(s), skip.")
        continue

    joined_lower = " ".join(files).lower()
    if any(k in joined_lower for k in ["run","race","tug","rope","highfive","cheer"]):
        fr = FR_FAST
    else:
        fr = FR_SLOW

    out_mp4 = SEQ_DIR / f"cluster{cid}_seq.mp4"
    cmd = [
        FFMPEG, "-y",
        "-framerate", str(fr),
        "-i", (folder / "img_%04d.jpg").as_posix(),
        "-vf", "scale=1920:-1:flags=lanczos,format=yuv420p",
        out_mp4.as_posix()
    ]
    try:
        run(cmd)
        print(f"[OK] cluster {cid} -> {out_mp4.name} (fr={fr}, images={len(copied_files)})")
    except Exception as e:
        print(f"[FAIL] cluster {cid}: {e}")

print("[INFO] Sequence generation done.")