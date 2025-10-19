from ultralytics import YOLO
import cv2
import torch
import time
import numpy as np

WEIGHTS = r"C:\Users\lolly\OneDrive\Desktop\Projects\Hand-Tracking-Robot\runs\pose\train7\weights\best.pt"

# --- Mapping functions ---
def map_x_angle(x, W):
    """Maps X center to -90 (left) → 0 (center) → +90 (right)."""
    return ((x - (W / 2)) / (W / 2)) * 90.0

def map_y_value(y, H):
    """Maps Y below midline to -90 (middle) → 0 (bottom). Above midline returns None."""
    if y < H / 2:
        return None
    return 180.0 * (y / H - 1.0)  # (H/2)->-90, H->0

def draw_text(img, text, org, color=(255, 255, 255), bg=(0, 0, 0)):
    """Draw text with outline for readability."""
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, bg, 3, cv2.LINE_AA)
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

# --- Main ---
def main():
    print("CUDA:", torch.cuda.is_available(), "|",
          (torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"))
    model = YOLO(WEIGHTS)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    prev_time = time.time()
    fps = 0


    while True:
        ok, frame = cap.read()
        if not ok:
            break
        H, W = frame.shape[:2]

        # guides
        cv2.line(frame, (0, H // 2), (W, H // 2), (80, 80, 80), 1)
        cv2.line(frame, (W // 2, 0), (W // 2, H), (80, 80, 80), 1)

        results = model.predict(
            source=frame,
            imgsz=640,
            conf=0.25,
            device=0 if torch.cuda.is_available() else "cpu",
            verbose=False
        )

        annotated = results[0].plot()
        boxes = results[0].boxes

        num = int(boxes.xyxy.shape[0]) if (boxes is not None and boxes.xyxy is not None) else 0

        if num == 1:
            # exactly one hand -> compute overlay for that single box
            (x1, y1, x2, y2) = boxes.xyxy[0].cpu().numpy().astype(float)
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            w, h = x2 - x1, y2 - y1
            area = max(w, 0) * max(h, 0)

            x_angle = ((cx - (W / 2)) / (W / 2)) * 90.0
            y_val = (None if cy < H / 2 else (180.0 * (cy / H - 1.0)))  # middle=-90, bottom=0

            x_txt = f"X: {x_angle:+.1f}°"
            y_txt = f"Y: {y_val:.1f}°" if y_val is not None else "Y: N/A"
            a_txt = f"Area: {area:.0f}px²"
            info = f"{x_txt} | {y_txt} | {a_txt}"

            # draw center marker + label
            cv2.drawMarker(annotated, (int(cx), int(cy)), (0,255,255),
                        markerType=cv2.MARKER_CROSS, markerSize=12, thickness=2)
            # text helper
            def draw_text(img, text, org, color=(255,255,255), bg=(0,0,0)):
                cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, bg, 3, cv2.LINE_AA)
                cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)
            draw_text(annotated, info, (int(x1), int(max(0, y1 - 10))))
        else:
            # 0 or >1 detections -> skip calculations and show a status banner
            msg = "Waiting for exactly ONE hand..." if num != 1 else ""
            if num == 0:
                msg = "No hands detected"
            elif num > 1:
                msg = f"{num} hands detected — calculations paused"
            cv2.rectangle(annotated, (10, 10), (420, 45), (0, 0, 0), -1)
            cv2.putText(annotated, msg, (18, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2, cv2.LINE_AA)

        # (optional HUD / FPS from your previous version)
        cv2.imshow("YOLOv11 Hand Pose Overlay", annotated)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()