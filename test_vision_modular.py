import cv2
import numpy as np
from scripts.vision_engine import get_vision_data

class MockSct:
    def __init__(self, image_path):
        self.img = cv2.imread(image_path)
        if self.img is None:
            raise FileNotFoundError(f"Could not load {image_path}")
        self.img_bgra = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
    def grab(self, monitor):
        return self.img_bgra

def test_on_image(path):
    sct = MockSct(path)
    monitor = {}
    
    player, mobs, exits = get_vision_data(sct, monitor)
    
    img_draw = cv2.imread(path)
    print("\n--- Testing Modular Vision on " + path + " ---")
    print("Monsters found: " + str(len(mobs)))
    print("Doors found: " + str(len(exits)))
    
    for center in exits:
        cv2.circle(img_draw, center, 15, (255, 0, 0), 2)
        print("  [DOOR] at " + str(center))

    cv2.imwrite("test_modular_result.png", img_draw)
    print("Result saved to: test_modular_result.png")

if __name__ == "__main__":
    test_on_image("image.png")