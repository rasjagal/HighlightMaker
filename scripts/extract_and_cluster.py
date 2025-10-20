"""
사진 EXIF + perceptual hash 추출 후 군집화.
새 파일이 추가된 경우에도 전체 다시 스캔하여 metadata/photos.csv, metadata/photo_clusters.csv 재작성.

사용:
  python scripts/extract_and_cluster.py
출력:
  metadata/photos.csv
  metadata/photo_clusters.csv
로그:
  stdout

설정:
  THRESH = 6 (pHash 거리 기준)
"""
import os, csv, imagehash
from PIL import Image
from pathlib import Path
import exifread

PHOTO_DIR = Path("raw/photo")
META_DIR = Path("metadata")
LOG_DIR = Path("logs")
META_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

THRESH = 6
SUPPORTED = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

def scan_photos():
    rows = []
    print("[INFO] Scanning photos...")
    for p in sorted(PHOTO_DIR.glob("*")):
        if p.suffix.lower() not in [s.lower() for s in SUPPORTED]:
            continue
        dt_str = ""
        try:
            with open(p, "rb") as f:
                tags = exifread.process_file(f, details=False)
                if 'EXIF DateTimeOriginal' in tags:
                    dt_str = str(tags['EXIF DateTimeOriginal'])
        except Exception:
            pass
        try:
            img = Image.open(p).convert("RGB")
            ph = imagehash.phash(img)
        except Exception as e:
            print(f"[WARN] Cannot hash {p.name}: {e}")
            continue
        rows.append((p.name, dt_str, str(ph)))
    return rows

def write_photos_csv(rows):
    photos_csv = META_DIR / "photos.csv"
    with open(photos_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["filename","datetime_original","phash"])
        w.writerows(rows)
    return photos_csv

def cluster(rows):
    clusters = []
    for name, dt, phash_str in rows:
        phash = imagehash.hex_to_hash(phash_str)
        placed = False
        for c in clusters:
            if phash - c["rep_hash"] <= THRESH:
                c["items"].append(name)
                placed = True
                break
        if not placed:
            clusters.append({"rep_hash": phash, "items":[name]})
    return clusters

def write_clusters_csv(clusters):
    clusters_csv = META_DIR / "photo_clusters.csv"
    with open(clusters_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cluster_id","count","filenames"])
        for i,c in enumerate(clusters):
            w.writerow([i, len(c["items"]), ";".join(c["items"])])
    return clusters_csv

def main():
    rows = scan_photos()
    print(f"[INFO] Total photos hashed: {len(rows)}")
    photos_csv = write_photos_csv(rows)
    clusters = cluster(rows)
    clusters_csv = write_clusters_csv(clusters)
    print(f"[INFO] Total clusters: {len(clusters)}")
    top = sorted(clusters, key=lambda x: len(x["items"]), reverse=True)[:10]
    print("[INFO] Top 10 cluster sizes:")
    for i, c in enumerate(top):
        print(f"  {i+1}. size={len(c['items'])} example={c['items'][:3]}")
    print("[INFO] Done.")
    print(f"  {photos_csv}")
    print(f"  {clusters_csv}")

if __name__ == "__main__":
    main()