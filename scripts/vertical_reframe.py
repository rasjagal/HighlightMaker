"""
16:9 본편 영상을 9:16으로 재크롭.
얼굴(Haar Cascade) 중심 → 실패 시 프레임 중앙.
사용 전 haarcascade_frontalface_default.xml 파일을 work/models/ 에 넣어야 함.

사용:
  python scripts/vertical_reframe.py
입력:
  outputs/final/Mangwon_Field_Day_20251020_full.mp4 (최종 본편)
출력:
  work/vertical/Mangwon_Field_Day_vertical_full.mp4
"""
import cv2, os
from pathlib import Path

IN_VIDEO  = Path("outputs/final/Mangwon_Field_Day_20251020_full.mp4")
OUT_DIR   = Path("work/vertical")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_VIDEO = OUT_DIR / "Mangwon_Field_Day_vertical_full.mp4"

MODEL_DIR = Path("work/models")
FACE_CASCADE_PATH = MODEL_DIR / "haarcascade_frontalface_default.xml"

if not IN_VIDEO.exists():
    print("[ERROR] 최종 16:9 영상이 없습니다. 먼저 본편 export 후 실행.")
    exit(1)

if not FACE_CASCADE_PATH.exists():
    print("[ERROR] Haar Cascade 파일 없음. OpenCV GitHub에서 다운로드 후 위치:")
    print(FACE_CASCADE_PATH)
    exit(1)

face_cascade = cv2.CascadeClassifier(str(FACE_CASCADE_PATH))

cap = cv2.VideoCapture(str(IN_VIDEO))
fps = cap.get(cv2.CAP_PROP_FPS) or 30
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
w_out, h_out = 1080, 1920
writer = cv2.VideoWriter(str(OUT_VIDEO), fourcc, fps, (w_out, h_out))

prev_cx, prev_cy = None, None
alpha = 0.15

while True:
    ret, frame = cap.read()
    if not ret:
        break
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(40,40))
    if len(faces) > 0:
        areas = [(fw*fh, (x,y,fw,fh)) for (x,y,fw,fh) in faces]
        _, (x,y,fw,fh) = max(areas, key=lambda z: z[0])
        target_cx = x + fw//2
        target_cy = y + fh//2
    else:
        target_cx, target_cy = w//2, h//2

    if prev_cx is None:
        smooth_cx, smooth_cy = target_cx, target_cy
    else:
        smooth_cx = int(prev_cx + alpha*(target_cx - prev_cx))
        smooth_cy = int(prev_cy + alpha*(target_cy - prev_cy))
    prev_cx, prev_cy = smooth_cx, smooth_cy

    crop_h = h
    crop_w = int(crop_h * 9/16)
    if crop_w > w:
        crop_w = w
        crop_h = int(crop_w * 16/9)

    x1 = max(0, smooth_cx - crop_w//2)
    x2 = min(w, x1 + crop_w)
    if x2 - x1 < crop_w:
        x1 = max(0, x2 - crop_w)

    y1 = max(0, smooth_cy - crop_h//2)
    y2 = min(h, y1 + crop_h)
    if y2 - y1 < crop_h:
        y1 = max(0, y2 - crop_h)

    crop = frame[y1:y2, x1:x2]
    resized = cv2.resize(crop, (w_out, h_out), interpolation=cv2.INTER_AREA)
    writer.write(resized)

cap.release()
writer.release()
print("[INFO] Vertical reframing complete:", OUT_VIDEO)