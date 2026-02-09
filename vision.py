import cv2
import numpy as np
import mss
import json
import time

def get_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Run setup.py first.")
        exit()

def run_vision():
    config = get_config()
    reg = config["map_region"]
    monitor = {"top": reg["top"], "left": reg["left"], "width": reg["width"], "height": reg["height"]}
    kernel = np.ones((3,3), np.uint8)

    with mss.mss() as sct:
        print("Vision started. Press 'q' in the window to stop.")
        print("Opening 3 windows: [Debugger], [Monster Mask], [Door Mask]")
        
        while True:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            debug_frame = frame.copy()

            # 1. Player Dot
            lower_cyan = np.array([80, 100, 200])
            upper_cyan = np.array([100, 255, 255])
            mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
            contours_p, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            player_pos = None
            for cnt in contours_p:
                if cv2.contourArea(cnt) > 5:
                    x, y, w, h = cv2.boundingRect(cnt)
                    player_pos = (x + w//2, y + h//2)
                    cv2.circle(debug_frame, player_pos, 5, (255, 255, 0), 2)
                    break

            # 2. Monsters (Red/Orange)
            lower_red1 = np.array([0, 70, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 70, 70])
            upper_red2 = np.array([180, 255, 255])
            mask_mobs = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), 
                                       cv2.inRange(hsv, lower_red2, upper_red2))
            
            cv2.imshow("Monster Mask (Raw Red)", mask_mobs)

            if player_pos:
                cv2.circle(mask_mobs, player_pos, 8, 0, -1)

            cnts_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in cnts_m:
                area = cv2.contourArea(cnt)
                # Broad Area for small locations
                if 20 < area < 400:
                    x, y, sw, sh = cv2.boundingRect(cnt)
                    aspect_ratio = float(sw)/sh
                    extent = float(area)/(sw*sh)
                    if extent > 0.4 and 0.7 <= aspect_ratio <= 1.4:
                        cv2.circle(debug_frame, (x + sw//2, y + sh//2), 12, (0, 255, 0), 2)

            # 3. Doors (Blue)
            lower_blue = np.array([110, 100, 100])
            upper_blue = np.array([125, 255, 255])
            mask_doors = cv2.inRange(hsv, lower_blue, upper_blue)
            mask_doors = cv2.morphologyEx(mask_doors, cv2.MORPH_CLOSE, kernel)
            
            cv2.imshow("Door Mask (Raw Blue)", mask_doors)

            cnts_d, _ = cv2.findContours(mask_doors, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in cnts_d:
                area = cv2.contourArea(cnt)
                # Broad Area for small locations
                if 30 < area < 400:
                    x, y, sw, sh = cv2.boundingRect(cnt)
                    aspect_ratio = float(sw)/sh
                    extent = float(area)/(sw*sh)
                    if extent > 0.4 and 0.3 < aspect_ratio < 4.0:
                        cv2.circle(debug_frame, (x + sw//2, y + sh//2), 15, (255, 0, 0), 2)

            cv2.imshow("Bot Vision Debugger", debug_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_vision()