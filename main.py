import mss
import time
import keyboard
import pyautogui
import os
import random
import json
import cv2
import numpy as np

# Core Imports
from controls import Controller
import ocr

# Modular Scripts
from scripts.vision_engine import get_vision_data, clean_text
from scripts.movement import wait_until_stopped
from scripts.routines import perform_selling_routine, perform_return_routing

# --- Configuration ---
ATTACK_RANGE = 12
ALLOWED_MAPS = ["Kwieciste Kresy", "Błota Sham", "Krypty Bezsennych p1 s1", "Krypty Bezsennych p1 s2", "Grota Arbor s1", "Grota Arbor s2", "Krypty Bezsennych p2 s1", "Krypty Bezsennych p2 s2", "Ruiny Tass Zhil", "Las Porywów Wiatru", "Głusza Świstu"]

def main():
    ctrl = Controller()
    monitor = {"top": ctrl.region["top"], "left": ctrl.region["left"], 
               "width": ctrl.region["width"], "height": ctrl.region["height"]}
    
    print("Bot started! HOLD 'ESC' TO STOP.")
    
    current_target = None
    attack_count = 0
    last_map = ""
    map_entry_time = time.time()
    last_heal_time = 0
    ignored_mobs = {} 
    ignored_exits = {} 

    # Load config for healing and bags
    with open("config.json", "r") as f:
        config = json.load(f)
        heal_px = config.get("heal_pixel")
        bag_reg = config.get("bag_region")

    with mss.mss() as sct:
        while True:
            if keyboard.is_pressed('esc'): break
            now = time.time()
            
            # Cleanup ignored lists
            ignored_mobs = {k: v for k, v in ignored_mobs.items() if now - v < 600}
            ignored_exits = {k: v for k, v in ignored_exits.items() if now - v < 60}

            # --- 1. AUTO HEAL CHECK ---
            if heal_px and (now - last_heal_time > 0.5):
                pixel_color = pyautogui.pixel(heal_px["x"], heal_px["y"])
                if not (pixel_color[0] > 100 and pixel_color[1] < 100):
                    print(f"\n[!!!] LOW HEALTH detected. Healing!")
                    keyboard.press_and_release('3')
                    last_heal_time = now

            # --- 2. BAG FULL CHECK ---
            if bag_reg:
                bag_mon = {"top": bag_reg["top"], "left": bag_reg["left"], 
                           "width": bag_reg["width"], "height": bag_reg["height"]}
                bag_img = np.array(sct.grab(bag_mon))
                gray = cv2.cvtColor(bag_img, cv2.COLOR_BGRA2GRAY)
                resized = cv2.resize(gray, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
                _, thresh = cv2.threshold(resized, 150, 255, cv2.THRESH_BINARY_INV)
                bag_text = ocr.pytesseract.image_to_string(thresh, lang='eng', 
                                config='--psm 6 -c tessedit_char_whitelist=0123456789').strip()
                
                if bag_text in ["0", "1"]:
                    print(f"\n[!!!] BAGS FULL ({bag_text} left). Moving to sell...")
                    perform_selling_routine(ctrl)
                    p_now, _, _ = get_vision_data(sct, monitor)
                    perform_return_routing(sct, monitor, ctrl, p_now)
                    map_entry_time = time.time()
                    continue

            player, mobs, exits = get_vision_data(sct, monitor)
            if player is None:
                time.sleep(0.5); continue

            # --- 3. COMBAT LOGIC ---
            available_mobs = [m for m in mobs if not any(np.linalg.norm(np.array(m)-np.array(i)) < 15 for i in ignored_mobs)]
            if available_mobs:
                if current_target:
                     found_locked = None
                     for m in available_mobs:
                         if np.linalg.norm(np.array(m) - np.array(current_target)) < 15:
                             found_locked = m; break
                     current_target = found_locked
                if not current_target:
                    mobs_arr = np.array(available_mobs)
                    distances = np.linalg.norm(mobs_arr - player, axis=1)
                    current_target = available_mobs[np.argmin(distances)]
                    attack_count = 0
                    print(f"\nLocked Mob: {current_target}")

                dist = np.linalg.norm(np.array(current_target) - np.array(player))
                if dist <= ATTACK_RANGE:
                    attack_count += 1
                    print(f"Attacking! (Count: {attack_count}/3)")
                    ctrl.attack(); time.sleep(1.5)
                    
                    if attack_count >= 3:
                        print(f"Blacklisting coordinate {current_target} for 10 min.")
                        ignored_mobs[tuple(current_target)] = now
                        current_target = None
                        attack_count = 0
                    
                    time.sleep(random.uniform(0.1, 0.4)); continue
                else:
                    print(f"Approaching Mob... (Dist: {dist:.1f})", end='\r')
                    ctrl.click_map(current_target[0], current_target[1]); time.sleep(0.25)
                    if not wait_until_stopped(sct, monitor, player, ignored_mobs=ignored_mobs):
                        ignored_mobs[tuple(current_target)] = now; current_target = None
                    else:
                        print("Arrived! Waiting 1.2s...")
                        time.sleep(1.2)
                        print(f"Attacking once (Count: {attack_count + 1}/3)...")
                        ctrl.attack(); time.sleep(1.5)
                        attack_count += 1
                        
                        if attack_count >= 3:
                            ignored_mobs[tuple(current_target)] = now; current_target = None
                            attack_count = 0
                        
                        time.sleep(random.uniform(0.1, 0.4))
                continue

            # --- 4. EXPLORATION LOGIC ---
            print("No monsters. Scanning all exits...        ", end='\r')
            available_exits = [e for e in exits if not any(np.linalg.norm(np.array(e)-np.array(i)) < 10 for i in ignored_exits)]
            if not available_exits:
                if (now - map_entry_time < 10.0) and last_map:
                    print(f"--> Nothing visible. Trying 'P' to return to {last_map}")
                    keyboard.press_and_release('p')
                    if last_map in ALLOWED_MAPS:
                        ALLOWED_MAPS.remove(last_map); ALLOWED_MAPS.append(last_map)
                    map_entry_time = now; time.sleep(5); continue
                time.sleep(1); continue

            found_destinations = {}
            for target_exit in available_exits:
                sx, sy = ctrl.map_to_screen(target_exit[0], target_exit[1])
                ctrl.moveTo(target_exit[0], target_exit[1], duration=0.3); time.sleep(0.8)
                text = ocr.read_tooltip({"top": sy - 5, "left": sx + 25, "width": 300, "height": 40})
                clean = clean_text(text)
                if len(clean) > 2: found_destinations[clean] = target_exit
                else: ignored_exits[tuple(target_exit)] = now - 50 

            selected_map_name = None
            for map_name in ALLOWED_MAPS:
                search_target = map_name.lower().replace(" ", "")
                match_key = None
                for found_name in found_destinations.keys():
                    if search_target in found_name.lower().replace(" ", ""):
                        match_key = found_name; break
                if match_key:
                    selected_map_name = map_name; target_coords = found_destinations[match_key]; break 

            if selected_map_name:
                print(f"--> Priority Match! Selected: {selected_map_name}.")
                ctrl.click_map(target_coords[0], target_coords[1])
                ignored_exits[tuple(target_coords)] = now; time.sleep(0.5)
                wait_result = wait_until_stopped(sct, monitor, player, interrupt_if_mob=True, ignored_mobs=ignored_mobs)
                if wait_result == "monster":
                    print("--> Walk interrupted. Switching to combat.")
                    if tuple(target_coords) in ignored_exits: del ignored_exits[tuple(target_coords)]
                elif not wait_result:
                    print("--> Path timed out.")
                else:
                    print(f"--> Arrived at {selected_map_name}. Rotating queue...")
                    ALLOWED_MAPS.remove(selected_map_name); ALLOWED_MAPS.append(selected_map_name)
                    last_map = selected_map_name; map_entry_time = now
                    time.sleep(3)
            else:
                if (now - map_entry_time < 10.0) and last_map:
                    print(f"--> No matches. Trying 'P' to return to {last_map}")
                    keyboard.press_and_release('p')
                    if last_map in ALLOWED_MAPS:
                        ALLOWED_MAPS.remove(last_map); ALLOWED_MAPS.append(last_map)
                    map_entry_time = now; time.sleep(5); continue
                ctrl.reset_mouse()
                for coords in found_destinations.values(): ignored_exits[tuple(coords)] = now - 40
                time.sleep(2)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
