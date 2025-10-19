from ultralytics import YOLO
import cv2
import torch

WEIGHTS = r"C:\Users\lolly\OneDrive\Desktop\Projects\Hand-Tracking-Robot\runs\pose\train7\weights\best.pt"

print("CUDA:", torch.cuda.is_available(), "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

model = YOLO(WEIGHTS)

cap = cv2.VideoCapture(0)  # try 1,2 if you have multiple cams
if not cap.isOpened():
    raise RuntimeError("Could not open webcam (try a different index).")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    # Run inference on the current frame
    results = model.predict(
        source=frame,
        imgsz=640,
        conf=0.25,
        device=0 if torch.cuda.is_available() else "cpu",
        verbose=False
    )

    # Draw skeleton/boxes
    annotated = results[0].plot()

    # (Optional) access keypoints as NumPy
    # kpts = results[0].keypoints.xy  # list[Tensor], one per detection
    # if len(kpts):
    #     first_detection_kpts = kpts[0].cpu().numpy()  # shape: [num_keypoints, 2]

    cv2.imshow("YOLOv11 Hand Pose", annotated)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
