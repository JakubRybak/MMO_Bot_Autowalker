import cv2
import numpy as np
import os
import glob

def filter_exact_blue(input_folder="tests", output_folder="results"):
    # Targets:
    # 1. #3b50ff (59, 80, 255) -> HSV(117, 196, 255)
    # 2. #3162ff (49, 98, 255) -> HSV(113, 206, 255)
    # 3. #1b3699 (27, 54, 153) -> HSV(113, 210, 153)
    
    # Combined Range covering all 3 targets
    lower_blue = np.array([110, 170, 130])
    upper_blue = np.array([120, 235, 255])
    
    # Create results folder if not exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    image_files = glob.glob(os.path.join(input_folder, "*.png"))
    
    if not image_files:
        print(f"No PNG images found in {input_folder}")
        return

    print(f"Filtering for 3 Specific Blues in {len(image_files)} images...")

    for img_path in image_files:
        img = cv2.imread(img_path)
        if img is None: continue
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        # Clean mask to join core pixels
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        raw_points = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2:
                x, y, w, h = cv2.boundingRect(cnt)
                raw_points.append((x + w//2, y + h//2))
        
        # --- PROXIMITY FILTERING ---
        filtered_points = []
        for p in raw_points:
            # Check if this point is too close to any already filtered point
            is_duplicate = False
            for fp in filtered_points:
                dist = np.sqrt((p[0]-fp[0])**2 + (p[1]-fp[1])**2)
                if dist < 25: # Increased from 15 to 25 pixels
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered_points.append(p)

        output_img = img.copy()
        for p in filtered_points:
            cv2.circle(output_img, p, 10, (255, 80, 59), 2)
        
        save_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, f"filtered_{save_name}"), output_img)
        print(f"  {save_name}: Found {len(filtered_points)} unique matches.")

if __name__ == "__main__":
    filter_exact_blue()
