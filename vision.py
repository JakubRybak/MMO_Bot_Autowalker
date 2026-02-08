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
    # mss format: {'top': 0, 'left': 0, 'width': 100, 'height': 100}
    monitor = {"top": reg["top"], "left": reg["left"], "width": reg["width"], "height": reg["height"]}

    with mss.mss() as sct:
        print("Vision started. Press 'q' in the window to stop.")
        while True:
            # Capture screen
            img = np.array(sct.grab(monitor))
            # mss returns BGRA, we need BGR for OpenCV
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            debug_frame = frame.copy()

            # --- 1. Detect Player (Bright Cyan/Blue Dot) ---
            # This is typically very bright and saturated
            lower_cyan = np.array([80, 100, 200])
            upper_cyan = np.array([100, 255, 255])
            mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
            
            contours, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            player_pos = None
            for cnt in contours:
                if cv2.contourArea(cnt) > 5: # Small dot
                    x, y, w, h = cv2.boundingRect(cnt)
                    player_pos = (x + w//2, y + h//2)
                    cv2.circle(debug_frame, player_pos, 5, (255, 255, 0), 2)
                    cv2.putText(debug_frame, "BOT", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                    break

            # If no cyan dot, fallback to Yellow Square center
            if player_pos is None:
                mask_yellow = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([40, 255, 255]))
                contours_y, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours_y:
                    if cv2.contourArea(cnt) > 100:
                        x, y, w, h = cv2.boundingRect(cnt)
                        player_pos = (x + w//2, y + h//2)
                        cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
                        break

            # Monsters (Red/Orange) - Refined
            mask_a = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([32, 255, 255]))
            mask_b1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
            mask_b2 = cv2.inRange(hsv, np.array([165, 100, 100]), np.array([180, 255, 255]))
            mask_mobs = cv2.bitwise_or(mask_a, mask_b1)
            mask_mobs = cv2.bitwise_or(mask_mobs, mask_b2)
            
            if player_pos:
                cv2.circle(mask_mobs, player_pos, 8, 0, -1)

            contours, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mobs = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 20 < area < 150:
                    x, y, w, h = cv2.boundingRect(cnt)
                    extent = float(area) / (w * h) if w * h > 0 else 0
                    aspect_ratio = float(w)/h
                    if extent > 0.35 and 0.6 < aspect_ratio < 1.4:
                        mob_center = (x + w//2, y + h//2)
                        mobs.append(mob_center)
                        cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

            # Exits (Blue Squares) - Precision Match
            mask_blue = cv2.inRange(hsv, np.array([110, 80, 100]), np.array([130, 150, 255]))
            contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 80 < area < 150:
                    x, y, w, h = cv2.boundingRect(cnt)
                    extent = float(area) / (w * h) if w * h > 0 else 0
                    if extent > 0.40:
                        cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Draw lines to nearest mob if player exists
            if player_pos and mobs:
                # Find nearest mob
                mobs_arr = np.array(mobs)
                distances = np.linalg.norm(mobs_arr - player_pos, axis=1)
                nearest_idx = np.argmin(distances)
                cv2.line(debug_frame, player_pos, mobs[nearest_idx], (255, 255, 255), 1)

            # Show results
            cv2.imshow("Bot Vision Debugger", debug_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_vision()
