import mss
import json
import time
import keyboard
import os
import cv2
import numpy as np

def run_data_collector():
    # 1. Load config
    if not os.path.exists("config.json"):
        print("Error: config.json not found!")
        return
        
    with open("config.json", "r") as f:
        config = json.load(f)
        
    if "map_region" not in config:
        print("Error: 'map_region' not in config!")
        return
        
    reg = config["map_region"]
    monitor = {"top": reg["top"], "left": reg["left"], "width": reg["width"], "height": reg["height"]}
    
    # 2. Setup folder
    if not os.path.exists("data"):
        os.makedirs("data")
        
    print("--- AI Data Collector Started ---")
    print(f"Region: {monitor}")
    print("Instructions:")
    print("  - Press 'SPACE' to capture the minimap.")
    print("  - Press 'ESC' to stop.")
    print(f"Files will be saved in the 'data/' folder.")

    with mss.mss() as sct:
        count = 0
        while True:
            if keyboard.is_pressed('esc'):
                break
                
            if keyboard.is_pressed('space'):
                # Capture
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Save with timestamp
                timestamp = int(time.time() * 1000)
                filename = f"data/minimap_{timestamp}.png"
                cv2.imwrite(filename, frame)
                
                count += 1
                print(f"[{count}] Captured: {filename}")
                
                # Small sleep to prevent multiple captures per single press
                time.sleep(0.3)
            
            time.sleep(0.01)

if __name__ == "__main__":
    run_data_collector()
