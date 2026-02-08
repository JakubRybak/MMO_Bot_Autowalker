import pyautogui
import keyboard
import time
import json
import os

def run_simple_heal():
    if not os.path.exists("config.json"):
        print("Error: config.json not found.")
        return
        
    with open("config.json", "r") as f:
        config = json.load(f)
        
    if "heal_pixel" not in config:
        print("ERROR: No heal pixel calibrated!")
        print("Please run setup_simple_heal.py first.")
        return
        
    px = config["heal_pixel"]["x"]
    py = config["heal_pixel"]["y"]
    
    print(f"Monitoring Pixel at ({px}, {py}). Close with 'Q'.")
    last_heal = 0

    while True:
        # Get color of that exact pixel
        # Note: pyautogui.pixel() returns (R, G, B)
        color = pyautogui.pixel(px, py)
        
        # Check if it's "not red"
        # Most Margonem health is bright red (R > 150, G < 100, B < 100)
        # If R is low, it means the bar is empty at that spot
        is_red = color[0] > 100 and color[1] < 100
        
        if not is_red:
            now = time.time()
            if now - last_heal > 1.5:
                print(f"[!!!] HEAL TRIGGERED! Color was {color}. Pressing '3'!")
                keyboard.press_and_release('3')
                last_heal = now
        
        if keyboard.is_pressed('q'):
            break
            
        time.sleep(0.1)

if __name__ == "__main__":
    run_simple_heal()
