import cv2
import numpy as np
import os
import glob

def filter_monsters_red(input_folder="tests", output_folder="results_monsters"):
    # Targets:
    # 1. #ff5656 (255, 86, 86) -> HSV(0, 169, 255)
    # 2. #ff3b3b (255, 59, 59) -> HSV(0, 196, 255)
    # 3. #f15252 (241, 82, 82) -> HSV(0, 168, 241)
    # 4. #ff6c6c (255, 108, 108) -> HSV(0, 147, 255)
    # 5. #f73d3d (247, 61, 61) -> HSV(0, 192, 247)
    
    # Combined Red Range covering all 5 targets
    lower_red1 = np.array([0, 130, 170])
    upper_red1 = np.array([10, 230, 255])
    lower_red2 = np.array([170, 130, 170])
    upper_red2 = np.array([180, 230, 255])
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    image_files = glob.glob(os.path.join(input_folder, "*.png"))
    
    if not image_files:
        print(f"No PNG images found in {input_folder}")
        return

    print(f"Filtering for 5 Monster Reds in {len(image_files)} images...")

    for img_path in image_files:
        img = cv2.imread(img_path)
        if img is None: continue
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Clean mask
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        raw_points = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 2:
                x, y, w, h = cv2.boundingRect(cnt)
                raw_points.append((x + w//2, y + h//2))
        
        # --- PROXIMITY FILTERING (25px) ---
        unique_mobs = []
        for p in raw_points:
            is_duplicate = False
            for um in unique_mobs:
                dist = np.sqrt((p[0]-um[0])**2 + (p[1]-um[1])**2)
                if dist < 25:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_mobs.append(p)

        output_img = img.copy()
        for p in unique_mobs:
            # Draw GREEN circle for monsters
            cv2.circle(output_img, p, 10, (0, 255, 0), 2)
        
        save_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, f"monster_{save_name}"), output_img)
        print(f"  {save_name}: Found {len(unique_mobs)} unique monsters.")

if __name__ == "__main__":
    filter_monsters_red()
