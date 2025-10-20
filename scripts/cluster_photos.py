import cv2, imagehash
from PIL import Image
from pathlib import Path
import csv

photo_dir = Path("raw/photo")
rows = []
for p in photo_dir.glob("*.jpg"):
    img = Image.open(p)
    phash = imagehash.phash(img)
    rows.append((p.name, str(phash)))

with open("metadata_hash.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["filename","phash"])
    w.writerows(rows)