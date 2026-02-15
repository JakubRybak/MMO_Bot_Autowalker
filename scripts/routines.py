import time
import keyboard
import pyautogui
import ocr
from scripts.vision_engine import get_vision_data, clean_text
from scripts.movement import wait_until_stopped
import numpy as np

def perform_selling_routine(ctrl):
    print("\n=== STARTING SELL ROUTINE ===")
    
    # 0. Clear UI (just in case we were just in a fight)
    keyboard.press_and_release('z')
    time.sleep(1)

    print("[1/4] Teleporting (7)...")
    keyboard.press_and_release('7')
    time.sleep(2)

    print("[2/4] Entering Shop (Fixed Click)...")
    pyautogui.click(121, 399)
    time.sleep(3)

    print("[3/4] Walking to Trade Point...")
    pyautogui.click(266, 528)
    time.sleep(3)

    print("[4/4] Executing Trade Macro...")
    keyboard.press_and_release('r')
    time.sleep(0.5)
    keyboard.press_and_release('1')
    time.sleep(1.0)

    clicks = [(1119, 410), (1143, 791), (1119, 410), (1143, 791),
              (1155, 411), (1143, 791), (1155, 411), (1143, 791),
              (1191, 412), (1143, 791), (1191, 412), (1143, 791)]
    
    for cx, cy in clicks:
        pyautogui.click(cx, cy)
        time.sleep(0.4)

    keyboard.press_and_release('esc')
    time.sleep(0.5)
    print("=== SELL ROUTINE COMPLETE ===\n")

def perform_return_routing(sct, monitor, ctrl, player, heal_px=None):
    print("=== STARTING RETURN ROUTING ===")
    print("Exiting Shop (Fixed Click)...")
    pyautogui.click(339, 640)
    time.sleep(0.5)
    wait_until_stopped(sct, monitor, player)
    time.sleep(3) 

    route = ["Lazurowe Wzgórze", "Grań Gawronich", "Błota Sham"]
    
    while route:
        if keyboard.is_pressed('esc'): return
        next_goal = route[0]
        
        # --- Health Check during return ---
        if heal_px:
            px_color = pyautogui.pixel(heal_px["x"], heal_px["y"])
            if not (px_color[0] > 100 and px_color[1] < 100):
                keyboard.press_and_release('3')

        print(f"Seeking door to: {next_goal}...")

        p_now, _, exits = get_vision_data(sct, monitor)
        if not p_now:
            time.sleep(0.5); continue

        found_target = None
        for target_exit in exits:
            mx, my = target_exit
            sx, sy = ctrl.map_to_screen(mx, my)
            ctrl.moveTo(mx, my, duration=0.3)
            time.sleep(0.8)
            text = ocr.read_tooltip({"top": sy - 5, "left": sx + 25, "width": 300, "height": 40})
            clean = clean_text(text)
            
            if next_goal.lower().replace(" ", "") in clean.lower().replace(" ", ""):
                print(f"  Found goal! Entering {next_goal}")
                found_target = target_exit
                break
        
        if found_target:
            ctrl.click_map(found_target[0], found_target[1])
            route.pop(0)
            time.sleep(0.5)
            wait_until_stopped(sct, monitor, p_now)
            time.sleep(3)
        else:
            time.sleep(2)
    print("=== BACK IN FARMING ZONE ===\n")

def perform_death_recovery(sct, monitor, ctrl, heal_px=None):
    print("\n[!!!] POSSIBLE DEATH DETECTED. Waiting 8 minutes for respawn...")
    
    for _ in range(8 * 60):
        if keyboard.is_pressed('esc'): return
        time.sleep(1)

    print(f"[{time.strftime('%H:%M:%S')}] Respawn window over. Clearing UI...")
    keyboard.press_and_release('z')
    time.sleep(1)
    
    # Initial heal after respawn
    if heal_px:
        print("Restoring health...")
        for _ in range(3): 
            px_color = pyautogui.pixel(heal_px["x"], heal_px["y"])
            if not (px_color[0] > 100 and px_color[1] < 100):
                keyboard.press_and_release('3')
                time.sleep(0.5)

    route = ["Grań Gawronich", "Błota Sham Al"]
    fail_count = 0 # Track consecutive failures
    
    while route:
        if keyboard.is_pressed('esc'): return
        next_goal = route[0]
        
        # Health check during recovery walk
        if heal_px:
            px_color = pyautogui.pixel(heal_px["x"], heal_px["y"])
            if not (px_color[0] > 100 and px_color[1] < 100):
                keyboard.press_and_release('3')

        print(f"Seeking door to: {next_goal}...")

        p_now, _, exits = get_vision_data(sct, monitor)
        found_target = None
        
        if p_now:
            for target_exit in exits:
                mx, my = target_exit
                sx, sy = ctrl.map_to_screen(mx, my)
                ctrl.moveTo(mx, my, duration=0.3)
                time.sleep(0.8)
                text = ocr.read_tooltip({"top": sy - 5, "left": sx + 25, "width": 300, "height": 40})
                clean = clean_text(text)
                
                if next_goal.lower().replace(" ", "") in clean.lower().replace(" ", ""):
                    print(f"  Found goal! Entering {next_goal}")
                    found_target = target_exit
                    break
        
        if found_target:
            ctrl.click_map(found_target[0], found_target[1])
            route.pop(0)
            fail_count = 0 # Reset on success
            time.sleep(0.5)
            wait_until_stopped(sct, monitor, p_now)
            time.sleep(5)
        else:
            fail_count += 1
            print(f"  Door not visible (Attempt {fail_count}/10). Retrying...")
            if fail_count >= 10:
                print("  [!] Recovery failed repeatedly. Returning to main loop.")
                return # Exit to main loop so it can detect death again
            time.sleep(10)
    
    print("=== RECOVERY COMPLETE ===\n")
