import cv2, mediapipe as mp, os
in_path = "outputs/draft_v1.mp4"
out_path = "outputs/draft_v1_vertical.mp4"

cap = cv2.VideoCapture(in_path)
w_out, h_out = 1080, 1920
mp_pose = mp.solutions.pose.Pose()
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(out_path, fourcc, 30, (w_out, h_out))

while True:
    ret, frame = cap.read()
    if not ret: break
    h, w = frame.shape[:2]
    results = mp_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.pose_landmarks:
        xs = [lmk.x * w for lmk in results.pose_landmarks.landmarks]
        ys = [lmk.y * h for lmk in results.pose_landmarks.landmarks]
        cx, cy = int(sum(xs)/len(xs)), int(sum(ys)/len(ys))
    else:
        cx, cy = w//2, h//2
    # 9:16 크롭 박스 계산
    target_h = h
    target_w = int(target_h * 9/16)
    if target_w > w:
        target_w = w
        target_h = int(target_w * 16/9)
    x1 = max(0, cx - target_w//2)
    x2 = min(w, x1 + target_w)
    y1 = max(0, cy - target_h//2)
    y2 = min(h, y1 + target_h)
    crop = frame[y1:y2, x1:x2]
    resized = cv2.resize(crop, (w_out, h_out))
    out.write(resized)

cap.release()
out.release()