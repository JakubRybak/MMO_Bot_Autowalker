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
import json

# --- Configuration ---
ATTACK_RANGE = 12
COOLDOWN = 0.5
ALLOWED_MAPS = ["Kwieciste Kresy", "Krypty Bezsennych p1 s2", "Krypty Bezsennych p2 s2", "Krypty Bezsennych p2 s1", "Błota Sham Al", "Ruiny Tass Zhil", "Las Porywów Wiatru", "Głusza Świstu"]

def clean_text(text):
    """Removes special characters and fixes common OCR errors (p.l -> p1)."""
    import re
    # Fix common Tesseract errors found in location_tooltip samples
    text = text.replace(".l", "1").replace(".1", "1").replace(".2", "2").replace(".s", " s")
    # Keep only alphanumeric and Polish chars
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

    # 2. Monsters (Red/Orange) - Absolute Perfect Geometric Match
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_mobs = cv2.bitwise_or(mask1, mask2)
    # NO Morphological Closing for monsters to preserve square shape

    if player_pos:
        # Mask out player area
        cv2.circle(mask_mobs, player_pos, 8, 0, -1) 
    
    contours_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mobs = []
    for cnt in contours_m:
        area = cv2.contourArea(cnt)
        if 30 < area < 150:
            x, y, sw, sh = cv2.boundingRect(cnt)
            aspect_ratio = float(sw)/sh
            extent = float(area)/(sw*sh)
            # The "Golden" Geometric Filter
            if extent > 0.4 and 0.7 <= aspect_ratio <= 1.4:
                mobs.append((x + sw//2, y + sh//2))

    # 3. Exits (Blue Squares) - Absolute Perfect Geometric Match
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([125, 255, 255])
    mask_doors = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_doors = cv2.morphologyEx(mask_doors, cv2.MORPH_CLOSE, kernel)
    
    contours_e, _ = cv2.findContours(mask_doors, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    exits = []
    for cnt in contours_e:
        area = cv2.contourArea(cnt)
        if 35 < area < 200:
            x, y, sw, sh = cv2.boundingRect(cnt)
            aspect_ratio = float(sw)/sh
            extent = float(area)/(sw*sh)
            # The "Wide" Door Filter
            if extent > 0.4 and 0.3 < aspect_ratio < 4.0:
                exits.append((x + sw//2, y + sh//2))

    return player_pos, mobs, exits

def wait_until_stopped(sct, monitor, player_pos, interrupt_if_mob=False):
    """Returns True if stopped, False if stuck, or 'monster' if interrupted."""
    last_pos = player_pos
    last_move_time = time.time()
    stable_count = 0
    while stable_count < 5:
        if keyboard.is_pressed('esc'): return True
        time.sleep(0.05)
        new_player, new_mobs, _ = get_vision_data(sct, monitor)
        
        # INTERRUPTION LOGIC: If we are walking to an exit and see a monster
        if interrupt_if_mob and new_mobs:
            print("\n[!] Monster spotted! Interrupting walk...")
            return "monster"

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
    last_heal_time = 0
    ignored_mobs = {} 
    ignored_exits = {} 

    # Load heal pixel if available
    heal_px = None
    if "heal_pixel" in ctrl.region: # Checking the config through controller
        heal_px = ctrl.region["heal_pixel"]
    # Wait, Controller only loads map_region. Let's load full config here.
    with open("config.json", "r") as f:
        full_config = json.load(f)
        heal_px = full_config.get("heal_pixel")

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed('esc'): break

            now = time.time()
            ignored_mobs = {k: v for k, v in ignored_mobs.items() if now - v < 600}
            ignored_exits = {k: v for k, v in ignored_exits.items() if now - v < 60}

            # --- AUTO HEAL CHECK ---
            if heal_px:
                # Check if heal is off cooldown
                if now - last_heal_time > 1.5:
                    pixel_color = pyautogui.pixel(heal_px["x"], heal_px["y"])
                    # If red channel is low or green is high, it's not red
                    if not (pixel_color[0] > 100 and pixel_color[1] < 100):
                        print(f"\n[!!!] LOW HEALTH detected ({pixel_color}). Healing!")
                        keyboard.press_and_release('3')
                        last_heal_time = now

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
            print("No monsters. Scanning all exits...        ", end='\r')
            # Filter exits that are not temporarily ignored
            available_exits = [e for e in exits if not any(np.linalg.norm(np.array(e)-np.array(i)) < 10 for i in ignored_exits)]
            
            if not available_exits:
                time.sleep(1)
                continue

            found_destinations = {} # {OCR_Name: (x,y)}
            
            # 1. Scan ALL available doors
            for target_exit in available_exits:
                sx, sy = ctrl.map_to_screen(target_exit[0], target_exit[1])
                
                # Hover to read name
                ctrl.moveTo(target_exit[0], target_exit[1], duration=0.3)
                time.sleep(0.8)

                box = {"top": sy - 5, "left": sx + 25, "width": 300, "height": 40}
                text = ocr.read_tooltip(box)
                clean = clean_text(text)
                
                print(f"  OCR Result for door at {target_exit}: '{clean}'")
                
                if len(clean) > 2:
                    found_destinations[clean] = target_exit
                else:
                    # OCR Failed, ignore briefly so we can check others
                    ignored_exits[tuple(target_exit)] = time.time() - 50 

            # 2. Queue Priority Selection
            selected_map_name = None
            target_coords = None
            
            for map_name in ALLOWED_MAPS:
                # Fuzzy match map name: ignore spaces and case
                search_target = map_name.lower().replace(" ", "")
                
                match_key = None
                for found_name in found_destinations.keys():
                    if search_target in found_name.lower().replace(" ", ""):
                        match_key = found_name
                        break
                
                if match_key:
                    selected_map_name = map_name
                    target_coords = found_destinations[match_key]
                    break 

            # 3. Action
            if selected_map_name:
                print(f"--> Priority Match! Selected: {selected_map_name}.")
                
                ctrl.click_map(target_coords[0], target_coords[1])
                # Blacklist this exit for 60s to prevent immediate turn-back
                ignored_exits[tuple(target_coords)] = time.time()
                
                # Wait for arrival instead of static 5s
                time.sleep(0.5) # Give time to start walking
                # Set interrupt_if_mob=True so we stop if we see a target while walking
                wait_result = wait_until_stopped(sct, monitor, player, interrupt_if_mob=True)
                
                if wait_result == "monster":
                    print("--> Walk interrupted by monster. Switching to combat.")
                    # If interrupted, remove from blacklist so we can try again after combat
                    if tuple(target_coords) in ignored_exits:
                        del ignored_exits[tuple(target_coords)]
                elif not wait_result:
                    print("--> Exploration path timed out or stuck.")
                else:
                    print(f"--> Arrived at exit for {selected_map_name}. Rotating queue...")
                    # Move this map to the END of the queue ONLY NOW
                    ALLOWED_MAPS.remove(selected_map_name)
                    ALLOWED_MAPS.append(selected_map_name)
                    
                    print("--> Waiting for map load...")
                    time.sleep(3) # Short wait for the black screen/loading
            else:
                print("--> No queue matches found. Waiting...")
                ctrl.reset_mouse()
                # Ignore the checked exits for 20s to look for monsters or other events
                for coords in found_destinations.values():
                    ignored_exits[tuple(coords)] = time.time() - 40
                time.sleep(2)
            continue

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()