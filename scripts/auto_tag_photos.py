"""
사진의 평균 색/밝기 기반으로 청팀/백팀/운영진(검정)을 대략 추정.
파일명이나 색상이 불명확하면 unknown.

사용:
  python scripts/auto_tag_photos.py
출력:
  metadata/photo_tags.csv
"""
import csv
from pathlib import Path
from PIL import Image

PHOTOS_CSV = Path("metadata/photos.csv")
RAW_PHOTO  = Path("raw/photo")
OUT_CSV    = Path("metadata/photo_tags.csv")

def classify(img):
    small = img.resize((64,64))
    pixels = list(small.getdata())
    total = len(pixels)
    avg_r = sum(p[0] for p in pixels) / total
    avg_g = sum(p[1] for p in pixels) / total
    avg_b = sum(p[2] for p in pixels) / total
    avg_brightness = (avg_r + avg_g + avg_b) / 3

    # 단순 규칙 (원하는 경우 세부 조정)
    if avg_b > avg_r * 0.9 and avg_b > avg_g * 0.9 and avg_brightness > 70:
        return "blue"
    elif avg_brightness > 185 and abs(avg_r - avg_g) < 18 and abs(avg_g - avg_b) < 18:
        return "white"
    elif avg_brightness < 75:
        return "staff_black"
    else:
        return "unknown"

rows = []
with open(PHOTOS_CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        fname = row["filename"]
        path = RAW_PHOTO / fname
        if not path.exists():
            continue
        try:
            img = Image.open(path).convert("RGB")
            team = classify(img)
        except Exception:
            team = "error"
        rows.append((fname, team))

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["filename","team_guess"])
    w.writerows(rows)

print("[INFO] Tag file written:", OUT_CSV)