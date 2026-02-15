from ultralytics import YOLO
import os

def train_model():
    # 1. Load a pretrained YOLOv8 Nano model
    model = YOLO("yolov8n.pt") 

    # 2. Train the model
    # data: path to our corrected data.yaml
    # epochs: 50 is usually enough for simple icons
    # imgsz: 640 is standard
    print("--- Starting AI Training ---")
    results = model.train(
        data="My First Project.v1i.yolov8/data.yaml", 
        epochs=50, 
        imgsz=640, 
        device="cpu" # Use "0" if you have an NVIDIA GPU
    )
    
    print("\nTraining complete!")
    print("The trained model is saved in: runs/detect/train/weights/best.pt")

if __name__ == "__main__":
    train_model()