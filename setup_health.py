import pyautogui
import time
import json
import os

def calibrate_health():
    print("--- Margonem Health Bar Calibration ---")
    print("This will add the health bar region to your config.json.")
    print("")
    
    # Load existing config
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)

    print("Instructions:")
    print("Hover your mouse over the TOP-LEFT corner of the RED HEALTH BAR and wait 3 seconds...")
    time.sleep(3)
    tl = pyautogui.position()
    print(f"Captured Top-Left: {tl}")

    print("")
    print("Now hover your mouse over the BOTTOM-RIGHT corner of the RED HEALTH BAR and wait 3 seconds...")
    time.sleep(3)
    br = pyautogui.position()
    print(f"Captured Bottom-Right: {br}")

    # Add health_region to config
    config["health_region"] = {
        "top": tl.y,
        "left": tl.x,
        "width": br.x - tl.x,
        "height": br.y - tl.y
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("")
    print("Health bar configuration saved to config.json!")
    print(f"Region: {config['health_region']}")

if __name__ == "__main__":
    calibrate_health()
