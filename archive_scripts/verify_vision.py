import cv2
import numpy as np
import sys

def verify_vision(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load {image_path}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    kernel = np.ones((3,3), np.uint8)
    
    # 1. MONSTER MASK (Perfect Balance V2 + Closing)
    mask_a = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([32, 255, 255]))
    mask_b1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    mask_b2 = cv2.inRange(hsv, np.array([165, 100, 100]), np.array([180, 255, 255]))
    mask_mobs = cv2.bitwise_or(mask_a, mask_b1)
    mask_mobs = cv2.bitwise_or(mask_mobs, mask_b2)
    mask_mobs = cv2.morphologyEx(mask_mobs, cv2.MORPH_CLOSE, kernel)
    
    # 2. DOOR MASK (Vivid Blue Precision Match + Closing)
    mask_blue = cv2.inRange(hsv, np.array([110, 100, 100]), np.array([125, 255, 255]))
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
    
    output_img = img.copy()
    print(f"\n--- SYNCED Detailed Analysis for {image_path} ---")

    # Find Monsters (Green)
    m_count = 0
    cnts_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in cnts_m:
        area = cv2.contourArea(cnt)
        if 24 < area < 120:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area) / (w * h) if w * h > 0 else 0
            aspect_ratio = float(w)/h
            if extent > 0.35 and 0.65 < aspect_ratio < 1.35:
                m_count += 1
                center = (x+w//2, y+h//2)
                print(f"  [MOB] at {center} (Area: {area:.1f})")
                cv2.circle(output_img, center, 10, (0, 255, 0), 2)

    # Find Doors (Blue)
    d_count = 0
    cnts_e, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in cnts_e:
        area = cv2.contourArea(cnt)
        if 30 <= area < 150:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area) / (w * h) if w * h > 0 else 0
            aspect_ratio = float(w)/h
            if extent > 0.40 and 0.7 < aspect_ratio < 1.3:
                d_count += 1
                center = (x+w//2, y+h//2)
                print(f"  [DOOR] at {center} (Area: {area:.1f})")
                cv2.circle(output_img, center, 10, (255, 0, 0), 2)

    cv2.imwrite("procesed_image.png", output_img)
    print(f"Summary: Mobs={m_count}, Doors={d_count}")
    print(f"Result saved to: procesed_image.png")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "image.png"
    verify_vision(path)