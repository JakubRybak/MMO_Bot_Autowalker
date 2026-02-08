import cv2
import numpy as np
import sys

def find_all(map_path, output_path="processed_all_map.png"):
    img = cv2.imread(map_path)
    if img is None:
        print("Error: Could not load " + map_path)
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    kernel = np.ones((3,3), np.uint8)
    output_img = img.copy()
    
    # --- 1. MONSTERS (REVERTED TO 100% EXACT STANDALONE LOGIC) ---
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_mobs = cv2.bitwise_or(mask1, mask2)
    
    contours_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    m_count = 0
    for cnt in contours_m:
        area = cv2.contourArea(cnt)
        if 30 < area < 150:
            x, y, sw, sh = cv2.boundingRect(cnt)
            aspect_ratio = float(sw)/sh
            extent = float(area)/(sw*sh)
            if extent > 0.4 and 0.7 <= aspect_ratio <= 1.4:
                m_count += 1
                center = (x + sw//2, y + sh//2)
                cv2.circle(output_img, center, 12, (0, 255, 0), 2)

    # --- 2. DOORS (REVERTED TO 100% EXACT STANDALONE LOGIC) ---
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([125, 255, 255])
    mask_doors = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_doors = cv2.morphologyEx(mask_doors, cv2.MORPH_CLOSE, kernel)
    
    contours_d, _ = cv2.findContours(mask_doors, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    d_count = 0
    for cnt in contours_d:
        area = cv2.contourArea(cnt)
        if 35 < area < 200:
            x, y, sw, sh = cv2.boundingRect(cnt)
            aspect_ratio = float(sw)/sh
            extent = float(area)/(sw*sh)
            if extent > 0.4 and 0.3 < aspect_ratio < 4.0:
                d_count += 1
                center = (x + sw//2, y + sh//2)
                cv2.circle(output_img, center, 15, (255, 0, 0), 2)

    cv2.imwrite(output_path, output_img)
    print("\n--- Results for " + map_path + " ---")
    print("Monsters found: " + str(m_count))
    print("Doors found: " + str(d_count))
    print("Result saved to: " + output_path)

if __name__ == "__main__":
    for i in ["1", "2", "3", "4", "5", "6"]:
        map_file = "mini_map.png" if i=="1" else "mini_map_" + i + ".png"
        find_all(map_file, "processed_final_" + i + ".png")