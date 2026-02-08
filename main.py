import cv2
import numpy as np
import mss
import time
import keyboard
import pyautogui
from controls import Controller
import ocr
import os
import random

# --- Configuration ---
ATTACK_RANGE = 12
COOLDOWN = 0.5
ALLOWED_MAPS = ["Ghuli Mogilnik", "Fort Eder", "Eder", "Przełęcz Łotrzyków", "Gościniec", "Dolina Rozbójników"]

# Create debug folder if not exists
if not os.path.exists("debug_scans"):
    os.makedirs("debug_scans")

def clean_text(text):
    """Removes special characters to make matching easier."""
    import re
    return re.sub(r'[^a-zA-Z0-9ąęćłńóśźżĄĘĆŁŃÓŚŹŻ\s]', '', text).strip()

def get_vision_data(sct, monitor):
    """Captures screen and returns player position, monsters, exits, and frame."""
    img = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = np.ones((3,3), np.uint8)

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
            break
            
    if player_pos is None:
        mask_yellow = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([40, 255, 255]))
        contours_y, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_y:
            if cv2.contourArea(cnt) > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                player_pos = (x + w//2, y + h//2)
                break

    # 2. Monsters (Red/Orange) - Perfect Balance V2
    mask_a = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([32, 255, 255]))
    mask_b1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    mask_b2 = cv2.inRange(hsv, np.array([165, 100, 100]), np.array([180, 255, 255]))
    mask_mobs = cv2.bitwise_or(mask_a, mask_b1)
    mask_mobs = cv2.bitwise_or(mask_mobs, mask_b2)
    mask_mobs = cv2.morphologyEx(mask_mobs, cv2.MORPH_CLOSE, kernel)

    if player_pos:
        cv2.circle(mask_mobs, player_pos, 8, 0, -1) 
    
    contours_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mobs = []
    for cnt in contours_m:
        area = cv2.contourArea(cnt)
        if 24 < area < 120:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area) / (w * h) if w * h > 0 else 0
            aspect_ratio = float(w)/h
            if extent > 0.35 and 0.65 < aspect_ratio < 1.35:
                mobs.append((x + w//2, y + h//2))

    # 3. Exits (Blue Squares) - Precision Vivid Blue Match
    # Analysis showed doors use a core of Hue 115, S>100, V>100
    mask_blue = cv2.inRange(hsv, np.array([110, 100, 100]), np.array([125, 255, 255]))
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
    
    contours_e, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    exits = []
    for cnt in contours_e:
        area = cv2.contourArea(cnt)
        if 30 < area < 150:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area) / (w * h) if w * h > 0 else 0
            aspect_ratio = float(w)/h
            # Doors are solid squares
            if extent > 0.40 and 0.7 < aspect_ratio < 1.3:
                exits.append((x + w//2, y + h//2))

    return player_pos, mobs, exits

def wait_until_stopped(sct, monitor, player_pos):
    """Returns True if stopped, False if stuck."""
    last_pos = player_pos
    last_move_time = time.time()
    stable_count = 0
    while stable_count < 5:
        if keyboard.is_pressed('esc'): return True
        time.sleep(0.05)
        new_player, _, _ = get_vision_data(sct, monitor)
        if new_player:
            if np.linalg.norm(np.array(new_player) - np.array(last_pos)) >= 1.5:
                last_move_time = time.time()
                stable_count = 0
            else:
                stable_count += 1
            last_pos = new_player
        
        if time.time() - last_move_time > 5.0: return False
    return True

def main():
    ctrl = Controller()
    monitor = {"top": ctrl.region["top"], "left": ctrl.region["left"], 
               "width": ctrl.region["width"], "height": ctrl.region["height"]}
    
    print("Bot started! HOLD 'ESC' TO STOP.")
    
    current_target = None
    attack_count = 0
    last_map = ""
    ignored_mobs = {} 
    ignored_exits = {} 

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed('esc'): break

            now = time.time()
            ignored_mobs = {k: v for k, v in ignored_mobs.items() if now - v < 600}
            ignored_exits = {k: v for k, v in ignored_exits.items() if now - v < 60}

            player, mobs, exits = get_vision_data(sct, monitor)

            if player is None:
                time.sleep(0.5)
                continue

            # --- COMBAT LOGIC ---
            available_mobs = [m for m in mobs if not any(np.linalg.norm(np.array(m)-np.array(i)) < 15 for i in ignored_mobs)]
            
            if available_mobs:
                if current_target:
                     found_locked = None
                     for m in available_mobs:
                         if np.linalg.norm(np.array(m) - np.array(current_target)) < 15:
                             found_locked = m
                             break
                     if found_locked:
                         current_target = found_locked
                     else:
                         current_target = None
                         attack_count = 0

                if not current_target:
                    mobs_arr = np.array(available_mobs)
                    distances = np.linalg.norm(mobs_arr - player, axis=1)
                    current_target = available_mobs[np.argmin(distances)]
                    attack_count = 0
                    print(f"\nLocked Mob: {current_target}")

                dist = np.linalg.norm(np.array(current_target) - np.array(player))
                if dist <= ATTACK_RANGE:
                    attack_count += 1
                    print(f"Attacking! (Count: {attack_count})")
                    ctrl.attack()
                    time.sleep(1.5)
                    print(f"Blacklisting coordinate {current_target} for 10 min.")
                    ignored_mobs[tuple(current_target)] = time.time()
                    current_target = None
                    attack_count = 0
                    time.sleep(random.uniform(0.1, 0.4))
                    continue
                else:
                    print(f"Approaching Mob... (Dist: {dist:.1f})", end='\r')
                    ctrl.click_map(current_target[0], current_target[1])
                    time.sleep(0.25)
                    
                    if not wait_until_stopped(sct, monitor, player):
                        print(f"\n[!] Stuck! Blacklisting location.")
                        ignored_mobs[tuple(current_target)] = time.time()
                        current_target = None
                    else:
                        print(f"Arrived! Waiting 1.2s...")
                        time.sleep(1.2)
                        print("Attacking once...")
                        ctrl.attack()
                        time.sleep(1.5)
                        ignored_mobs[tuple(current_target)] = time.time()
                        current_target = None
                        time.sleep(random.uniform(0.1, 0.4))
                continue

            # --- EXPLORATION LOGIC ---
            print("No monsters. Scanning for exits...        ", end='\r')
            available_exits = [e for e in exits if not any(np.linalg.norm(np.array(e)-np.array(i)) < 10 for i in ignored_exits)]
            
            if not available_exits:
                time.sleep(1)
                continue

            target_exit = available_exits[0] # Pick nearest
            sx, sy = ctrl.map_to_screen(target_exit[0], target_exit[1])
            
            # Save debug
            minimap_img = np.array(sct.grab(monitor))
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            cv2.imwrite(f"debug_scans/map_{timestamp}.png", minimap_img)

            ctrl.moveTo(target_exit[0], target_exit[1], duration=0.3)
            time.sleep(0.8)

            box = {"top": sy - 5, "left": sx + 25, "width": 300, "height": 40}
            text = ocr.read_tooltip(box, save_path=f"debug_scans/scan_{timestamp}.png")
            clean = clean_text(text)
            print(f"Read Map Name: '{clean}'")

            is_allowed = False
            for allowed in ALLOWED_MAPS:
                if allowed.lower() in clean.lower():
                    is_allowed = True
                    break
            
            if is_allowed:
                if clean.lower() == last_map.lower():
                    print(f"--> Ignoring {clean} (Just came from there).")
                    ignored_exits[tuple(target_exit)] = time.time()
                    ctrl.reset_mouse()
                    time.sleep(2)
                    continue

                print(f"--> Entering {clean}!")
                last_map = clean
                ctrl.click_map(target_exit[0], target_exit[1])
                ignored_exits[tuple(target_exit)] = time.time() - 40 
                time.sleep(5)
            else:
                if len(clean) > 2:
                    print(f"--> Ignoring {clean} (Not in allow list)")
                    ignored_exits[tuple(target_exit)] = time.time()
                else:
                    print(f"--> OCR Failed. Will retry.")
                    ignored_exits[tuple(target_exit)] = time.time() - 55 
                ctrl.reset_mouse()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
