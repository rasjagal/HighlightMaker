"""
파일명에 run/tug/highfive 등의 키워드를 넣어 자동 컷리스트 분류를 돕기 위한 리네임 스크립트.

사용:
  python scripts/rename_to_pattern.py
수정:
  RULES 리스트에서 특정 조건 -> 새 파일명 접두어 설정
"""
from pathlib import Path
import re

PHOTO_DIR = Path("raw/photo")

# 예시 규칙 (현재 단순: 파일명에 'IMG_' 포함 + 특정 인덱스 범위)
# 필요시 로직을 사용자가 상황에 맞게 조정
RULES = [
    (re.compile(r"IMG_.*"), "generic"),
]

def main():
    renamed = 0
    for f in PHOTO_DIR.glob("*"):
        if f.is_file() and f.suffix.lower() in [".jpg",".jpeg",".png"]:
            for pattern, prefix in RULES:
                if pattern.match(f.name):
                    new_name = f"{prefix}_{f.name}"
                    new_path = f.parent / new_name
                    if not new_path.exists():
                        f.rename(new_path)
                        renamed += 1
                    break
    print(f"[INFO] Renamed files: {renamed}")

if __name__ == "__main__":
    main()