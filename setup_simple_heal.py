import pyautogui
import time
import json
import os

def calibrate_pixel():
    print("--- Margonem Simple Heal Calibration ---")
    print("Find the spot on your health bar that is RED when high, but BLACK when < 60%.")
    print("")
    print("Hover your mouse over that exact spot and wait 5 seconds...")
    time.sleep(5)
    pos = pyautogui.position()
    color = pyautogui.pixel(pos.x, pos.y)
    print(f"Captured Pixel at ({pos.x}, {pos.y}) with Color {color}")

    # Load and save
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            
    config["heal_pixel"] = {"x": pos.x, "y": pos.y}
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
        
    print("\nCalibration saved to config.json!")
    print("You can now run 'python simple_heal.py'")

if __name__ == "__main__":
    calibrate_pixel()