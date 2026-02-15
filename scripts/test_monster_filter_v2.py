import cv2
import numpy as np
import os
import glob

def get_target_colors(sample_paths):
    """Extracts unique BGR colors from multiple samples using the broad red mask."""
    all_colors = set()
    for path in sample_paths:
        img = cv2.imread(path)
        if img is None: continue
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 50, 50]); upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50]); upper_red2 = np.array([180, 255, 255])
        mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
        pixels = img[mask > 0]
        for p in pixels:
            all_colors.add(tuple(p))
    return all_colors

def filter_monsters_comprehensive(input_folder="tests", output_folder="results_monsters", sample_files=["example.png", "example_2.png"]):
    print(f"Extracting target colors from {sample_files}...")
    target_colors = get_target_colors(sample_files)
    if not target_colors:
        print("Error: No colors found in samples.")
        return
    print(f"Loaded {len(target_colors)} unique color targets from all samples.")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    image_files = glob.glob(os.path.join(input_folder, "*.png"))
    
    for img_path in image_files:
        img = cv2.imread(img_path)
        if img is None: continue
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 50, 50]); upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50]); upper_red2 = np.array([180, 255, 255])
        broad_mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
        
        # Exact match logic
        precise_mask = np.zeros(broad_mask.shape, dtype=np.uint8)
        y_coords, x_coords = np.where(broad_mask > 0)
        for y, x in zip(y_coords, x_coords):
            if tuple(img[y, x]) in target_colors:
                precise_mask[y, x] = 255
        
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.morphologyEx(precise_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        raw_points = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 1:
                x, y, w, h = cv2.boundingRect(cnt)
                raw_points.append((x + w//2, y + h//2))
        
        # PROXIMITY FILTERING (25px)
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
            cv2.circle(output_img, p, 10, (0, 255, 0), 2)
        
        save_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, f"monster_combined_{save_name}"), output_img)
        print(f"  {save_name}: Found {len(unique_mobs)} monsters.")

if __name__ == "__main__":
    filter_monsters_comprehensive()