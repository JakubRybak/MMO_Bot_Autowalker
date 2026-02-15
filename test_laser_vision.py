import cv2
import numpy as np
from scripts.vision_engine import get_vision_data

class MockSCT:
    def grab(self, monitor):
        img = cv2.imread(monitor)
        if img is None: return None
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        return img

def test_final(path, out_name):
    img = cv2.imread(path)
    if img is None: return

    # Call the restored modular vision engine
    _, mobs, exits = get_vision_data(MockSCT(), path)
    
    output_img = img.copy()
    print("\n--- Final Restored Test for " + path + " ---")
    
    # Monsters (Green)
    for mx, my in mobs:
        cv2.circle(output_img, (mx, my), 12, (0, 255, 0), 2)
        
    # Doors (Blue)
    for dx, dy in exits:
        cv2.circle(output_img, (dx, dy), 15, (255, 0, 0), 2)

    cv2.imwrite(out_name, output_img)
    print("Monsters: " + str(len(mobs)))
    print("Doors:    " + str(len(exits)))
    print("Result saved to: " + out_name)

if __name__ == "__main__":
    test_final("image copy.png", "restored_result_1.png")
    test_final("image copy 2.png", "restored_result_2.png")
    test_final("image copy 3.png", "restored_result_3.png")
    test_final("image copy 4.png", "restored_result_4.png")