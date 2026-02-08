import cv2
import numpy as np
import mss
import json
import time
import keyboard

def get_config():
    with open("config.json", "r") as f:
        return json.load(f)

def run_health_check():
    config = get_config()
    if "health_region" not in config:
        print("ERROR: 'health_region' not found in config.json!")
        return

    reg = config["health_region"]
    monitor = {"top": reg["top"], "left": reg["left"], "width": reg["width"], "height": reg["height"]}
    
    last_heal_time = 0
    max_pixels = 0
    
    print("Circle Health Monitor Started.")
    print("Step 1: Calibration - Make sure your health is at 100%!")
    print("Step 2: Press 'C' while health is FULL to calibrate the Orb.")
    print("Press 'Q' to stop.")

    with mss.mss() as sct:
        while True:
            # Capture the health region
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Mask the Red/Brown health
            mask1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([15, 255, 255]))
            mask2 = cv2.inRange(hsv, np.array([165, 50, 50]), np.array([180, 255, 255]))
            red_mask = cv2.bitwise_or(mask1, mask2)
            
            current_pixels = cv2.countNonZero(red_mask)

            # Manual Calibration
            if keyboard.is_pressed('c'):
                max_pixels = current_pixels
                print(f"\n[CALIBRATED] 100% Health = {max_pixels} pixels.")
                time.sleep(1)

            if max_pixels > 0:
                hp_percent = (current_pixels / max_pixels) * 100
                print(f"Health Orb: {hp_percent:.1f}% ({current_pixels}/{max_pixels})", end='\r')
                
                # Trigger Healing below 60%
                if hp_percent < 60 and hp_percent > 5:
                    now = time.time()
                    if now - last_heal_time > 2.0:
                        print(f"\n[!!!] LOW HEALTH: {hp_percent:.1f}%! Drinking Potion '3'.")
                        keyboard.press_and_release('3')
                        last_heal_time = now
            else:
                print("Waiting for calibration (Press 'C' when health is 100%)...", end='\r')

            if keyboard.is_pressed('q'):
                break
            
            time.sleep(0.2)

if __name__ == "__main__":
    run_health_check()