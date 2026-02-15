import pyautogui
import keyboard
import time

def capture_coordinates():
    print("--- Margonem Coordinate Capture ---")
    print("Instructions:")
    print("  - Hover your mouse over a point.")
    print("  - Press 'SPACE' to capture the coordinates.")
    print("  - Press 'ESC' to stop.")
    print("")

    while True:
        if keyboard.is_pressed('space'):
            pos = pyautogui.position()
            # Printed in a format ready for Python lists or JSON
            print(f"Captured: ({pos.x}, {pos.y})")
            # Small sleep to prevent capturing the same point multiple times
            time.sleep(0.3)
            
        if keyboard.is_pressed('esc'):
            print("\nCapture finished.")
            break
            
        time.sleep(0.01)

if __name__ == "__main__":
    capture_coordinates()