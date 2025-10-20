"""
선택한 원본 영상 파일을 지정 비율로 슬로모션 변환.
사용자가 목록 파일(slow_list.txt)에 파일명,속도 비율을 작성하면 처리.
형식 예:
run_finish_clip1.mp4,2.5
tug_clash_original.mp4,2.0

속도 비율: setpts=비율*PTS  (2.5 → 약 40% 속도)

사용:
  python scripts/make_slowmo.py
입력:
  metadata/slow_list.txt
출력:
  work/slow/<원본명>_slow.mp4
"""
import subprocess
from pathlib import Path

LIST_FILE = Path("metadata/slow_list.txt")
RAW_VIDEO = Path("raw/video")
OUT_DIR   = Path("work/slow")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "ffmpeg"  # PATH 추가 되어 있다고 가정 (없으면 절대경로 또는 imageio_ffmpeg 사용)

if not LIST_FILE.exists():
    print("[WARN] slow_list.txt 없음. 예시 작성 후 다시 실행.")
    LIST_FILE.write_text("run_finish_clip1.mp4,2.5\ntug_clash_original.mp4,2.0\nhighfive_original.mp4,2.2\n", encoding="utf-8")
    exit(0)

lines = [l.strip() for l in LIST_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]

for line in lines:
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 2:
        print(f"[WARN] 잘못된 라인: {line}")
        continue
    fname, factor_str = parts
    try:
        factor = float(factor_str)
    except:
        print(f"[WARN] 속도 비율 파싱 실패: {factor_str}")
        continue

    src = RAW_VIDEO / fname
    if not src.exists():
        print(f"[WARN] 원본 없음: {fname}")
        continue

    out = OUT_DIR / (src.stem + "_slow.mp4")
    cmd = [
        FFMPEG, "-y",
        "-i", src.as_posix(),
        "-filter:v", f"setpts={factor}*PTS,fps=30",
        "-an",  # 현장음 제거 (음악만 사용할 예정)
        out.as_posix()
    ]
    print("[CMD]", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout)
    if p.returncode == 0:
        print(f"[OK] {fname} -> {out.name}")
    else:
        print(f"[FAIL] {fname}")

print("[INFO] Slow motion 변환 완료.")