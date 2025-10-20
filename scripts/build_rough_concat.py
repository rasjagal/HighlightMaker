"""
자동 컷리스트 파일(timeline_cutlist_generated.md)을 읽어
시퀀스 mp4 / 슬로모션 mp4 / raw/video 내 mp4를 찾아 concat용 리스트 생성.

사용:
  python scripts/build_rough_concat.py
출력:
  metadata/concat_list.txt
이후:
  ffmpeg -y -f concat -safe 0 -i metadata/concat_list.txt -c:v libx264 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k outputs/drafts/draft_v1.mp4
"""
from pathlib import Path

CUTLIST   = Path("metadata/timeline_cutlist_generated.md")
SEQ_DIR   = Path("work/sequences")
SLOW_DIR  = Path("work/slow")
RAW_VIDEO = Path("raw/video")
OUT_LIST  = Path("metadata/concat_list.txt")
OUT_LIST.parent.mkdir(exist_ok=True)
OUTPUTS   = Path("outputs/drafts")
OUTPUTS.mkdir(parents=True, exist_ok=True)

ORDER = ["intro","prep","team","running","tug","highfive","group","misc"]

sections = {}
current = None
if not CUTLIST.exists():
    print("[ERROR] 컷리스트 파일 없음. 먼저 generate_cutlist.py 실행.")
    exit(1)

for line in CUTLIST.read_text(encoding="utf-8").splitlines():
    line=line.strip()
    if line.startswith("## "):
        current = line[3:].strip()
        sections[current] = []
    elif line.startswith("- "):
        if current:
            item = line[2:].strip()
            if item != "(none)":
                sections[current].append(item)

entries = []
for sec in ORDER:
    for name in sections.get(sec, []):
        candidates = [
            SEQ_DIR / name,
            SLOW_DIR / name,
            RAW_VIDEO / name
        ]
        for c in candidates:
            if c.exists() and c.suffix.lower() == ".mp4":
                entries.append(c)
                break

if not entries:
    print("[WARN] concat 대상 MP4 없음.")
else:
    with OUT_LIST.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"file '{e.as_posix()}'\n")
    print(f"[INFO] Concat list entries={len(entries)} -> {OUT_LIST}")
    print("예시 ffmpeg 명령:")
    print(f"ffmpeg -y -f concat -safe 0 -i {OUT_LIST.as_posix()} -c:v libx264 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k outputs/drafts/draft_v1.mp4")