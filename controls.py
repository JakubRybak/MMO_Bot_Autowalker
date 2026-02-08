import pyautogui
import json
import time
import keyboard

# Speed up pyautogui
pyautogui.PAUSE = 0.1

def get_config():
    with open("config.json", "r") as f:
        return json.load(f)

class Controller:
    def __init__(self):
        config = get_config()
        self.region = config["map_region"]
        
    def map_to_screen(self, map_x, map_y):
        """Translates a pixel in the minimap image to a screen coordinate."""
        screen_x = self.region["left"] + map_x
        screen_y = self.region["top"] + map_y
        return screen_x, screen_y

    def moveTo(self, map_x, map_y, duration=0.1):
        """Moves mouse to map coordinates smoothly."""
        sx, sy = self.map_to_screen(map_x, map_y)
        pyautogui.moveTo(sx, sy, duration=duration)

    def click_map(self, map_x, map_y):
        """Clicks a specific point on the minimap."""
        sx, sy = self.map_to_screen(map_x, map_y)
        pyautogui.click(sx, sy)
        time.sleep(0.1)
        self.reset_mouse()

    def reset_mouse(self):
        """Moves mouse slightly outside the map area to clear tooltips."""
        # Move to Top-Left corner of the map window minus a few pixels
        pyautogui.moveTo(self.region["left"] - 15, self.region["top"] - 15)

    def attack(self):
        """Simulates the attack key."""
        keyboard.press_and_release('q')

if __name__ == "__main__":
    # Test Script: This will click the center of your map if run directly
    print("Testing controls in 3 seconds... Switch to Margonem window!")
    time.sleep(3)
    ctrl = Controller()
    
    # Test Corner
    print("Moving to Top-Left of minimap...")
    ctrl.moveTo(0, 0, duration=1.0)
    time.sleep(1)
    
    cx = ctrl.region["width"] // 2
    cy = ctrl.region["height"] // 2
    print(f"Moving to center: {cx}, {cy}")
    ctrl.moveTo(cx, cy, duration=1.0)
    print("Test complete.")
