import cv2
import numpy as np
import sys
import argparse

def test_on_image(image_path, min_area=28, max_area=75, min_extent=0.40):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # MONSTER MASK
    mask_a = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([32, 255, 255]))
    mask_b1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    mask_b2 = cv2.inRange(hsv, np.array([165, 100, 100]), np.array([180, 255, 255]))
    mask_mobs = cv2.bitwise_or(mask_a, mask_b1)
    mask_mobs = cv2.bitwise_or(mask_mobs, mask_b2)
    
    # DOOR MASK
    mask_blue = cv2.inRange(hsv, np.array([90, 50, 50]), np.array([130, 255, 255]))
    
    contours_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_e, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    debug_img = img.copy()
    found_mobs = 0
    found_doors = 0
    
    print(f"\n--- Analysis for {image_path} ---")
    
    print(f"Stats for potential MONSTERS (Red):")
    for cnt in contours_m:
        area = cv2.contourArea(cnt)
        if 20 < area < 100:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area) / (w * h) if w * h > 0 else 0
            aspect_ratio = float(w)/h
            is_monster = (min_area < area < max_area) and (extent > min_extent) and (0.7 < aspect_ratio < 1.3)
            print(f"  Mob: Area={area}, Extent={extent:.2f}, Aspect={aspect_ratio:.2f} -> {'PASS' if is_monster else 'FAIL'}")
            if is_monster:
                found_mobs += 1
                cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    print(f"Stats for potential DOORS (Blue):")
    for cnt in contours_e:
        area = cv2.contourArea(cnt)
        if 20 < area < 100:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area) / (w * h) if w * h > 0 else 0
            aspect_ratio = float(w)/h
            is_door = (min_area < area < max_area) and (extent > min_extent) and (0.7 < aspect_ratio < 1.3)
            print(f"  Door: Area={area}, Extent={extent:.2f}, Aspect={aspect_ratio:.2f} -> {'PASS' if is_door else 'FAIL'}")
            if is_door:
                found_doors += 1
                cv2.rectangle(debug_img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    save_name = f"test_result_{image_path.replace(' ', '_')}"
    cv2.imwrite(save_name, debug_img)
    print(f"\nSummary: Mobs={found_mobs}, Doors={found_doors}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs='?', default="image.png")
    args = parser.parse_args()
    test_on_image(args.image)