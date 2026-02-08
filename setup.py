import pyautogui
import time
import json
import os

def calibrate():
    print("--- Margonem Bot Calibration ---")
    print("1. Open Margonem in your browser.")
    print("2. Make sure the 'Podreczna mapa' is visible and in its fixed position.")
    print("")
    print("Instructions:")
    print("Hover your mouse over the TOP-LEFT corner of the MAP AREA and wait 3 seconds...")
    time.sleep(3)
    tl = pyautogui.position()
    print(f"Captured Top-Left: {tl}")

    print("")
    print("Now hover your mouse over the BOTTOM-RIGHT corner of the MAP AREA and wait 3 seconds...")
    time.sleep(3)
    br = pyautogui.position()
    print(f"Captured Bottom-Right: {br}")

    config = {
        "map_region": {
            "top": tl.y,
            "left": tl.x,
            "width": br.x - tl.x,
            "height": br.y - tl.y
        }
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("")
    print("Configuration saved to config.json!")
    print(f"Region: {config['map_region']}")

if __name__ == "__main__":
    calibrate()