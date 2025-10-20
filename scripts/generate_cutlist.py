"""
시퀀스 mp4 + 대표 사진(군집 첫 장)를 이용해 섹션별 자동 초안 Cutlist 생성.
섹션: intro, prep, team, running, tug, highfive, group, misc

사용:
  python scripts/generate_cutlist.py
출력:
  metadata/timeline_cutlist_generated.md
"""
import csv, re
from pathlib import Path

CLUSTER_CSV = Path("metadata/photo_clusters.csv")
SEQ_DIR     = Path("work/sequences")
OUT_MD      = Path("metadata/timeline_cutlist_generated.md")

PATTERNS = {
    "running": re.compile(r"(run|race)", re.I),
    "tug": re.compile(r"(tug|rope)", re.I),
    "highfive": re.compile(r"(highfive|high_five|high-five|cheer)", re.I),
    "group": re.compile(r"(group|all|together)", re.I),
    "team": re.compile(r"(team|blue|white)", re.I),
    "prep": re.compile(r"(prep|setup|staff)", re.I),
}

sections = {k: [] for k in ["intro","prep","team","running","tug","highfive","group","misc"]}

# 1) 시퀀스 분류
for sf in sorted(SEQ_DIR.glob("*_seq.mp4")):
    low = sf.name.lower()
    placed = False
    for key, pat in PATTERNS.items():
        if pat.search(low):
            sections[key].append(sf.name)
            placed = True
            break
    if not placed:
        sections["misc"].append(sf.name)

# 2) 대표 사진 보강
with open(CLUSTER_CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        files = [f for f in row["filenames"].split(";") if f.strip()]
        if not files:
            continue
        rep = files[0]
        low = rep.lower()
        matched = None
        for key, pat in PATTERNS.items():
            if pat.search(low):
                matched = key
                break
        target = matched if matched else "misc"
        if len(sections[target]) < 12:
            sections[target].append(rep)

# intro 확보
if not sections["intro"]:
    for candidate in ["team","prep","misc","running"]:
        if sections[candidate]:
            sections["intro"].append(sections[candidate][0])
            break

lines = ["# Auto-generated Cutlist (Draft v3)", ""]
for sec, items in sections.items():
    lines.append(f"## {sec}")
    if not items:
        lines.append("- (none)")
    else:
        for it in items[:20]:
            lines.append(f"- {it}")
    lines.append("")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print("[INFO] Written:", OUT_MD)