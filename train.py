# train.py
from ultralytics import YOLO
import torch

def main():
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
    else:
        print("No GPU")
        exit()

    model = YOLO("yolo11n-pose.pt")
    results = model.train(
        data=r"C:\Users\lolly\OneDrive\Desktop\Projects\Hand-Tracking-Robot\hand-keypoints.yaml",
        epochs=100,
        imgsz=640,
        workers=0,    
        device=0 if torch.cuda.is_available() else "cpu"
    )

if __name__ == "__main__":  
    main()
