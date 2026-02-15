import cv2
import numpy as np
import mss
import json
import keyboard
import time
import os

def debug_capture():
    if not os.path.exists("config.json"):
        print("Error: config.json not found.")
        return
        
    with open("config.json", "r") as f:
        config = json.load(f)
        
    if "bag_region" not in config:
        print("Error: bag_region not in config.")
        return
        
    reg = config["bag_region"]
    monitor = {"top": reg["top"], "left": reg["left"], "width": reg["width"], "height": reg["height"]}
    
    print(f"--- Bag Region Debug Capture ---")
    print(f"Targeting: {monitor}")
    print("Press SPACE to capture the region. Press ESC to quit.")

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed('esc'):
                break
                
            if keyboard.is_pressed('space'):
                # Capture the raw pixels
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Save the raw capture
                cv2.imwrite("bag_debug_raw.png", frame)
                
                # Show what the bot's preprocessing looks like (Gray + Threshold)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
                _, thresh = cv2.threshold(resized, 150, 255, cv2.THRESH_BINARY_INV)
                cv2.imwrite("bag_debug_preprocessed.png", thresh)
                
                print("Captured! Saved to bag_debug_raw.png and bag_debug_preprocessed.png")
                time.sleep(0.5) # debounce
            
            time.sleep(0.01)

if __name__ == "__main__":
    debug_capture()
