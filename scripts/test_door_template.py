import cv2
import numpy as np
import os
import glob

def door_template_match(input_folder="data", output_folder="results_doors", 
                        templates=["doors_templates/doors_1.png", "doors_templates/doors_2.png", 
                                   "doors_templates/doors_3.png", "doors_templates/doors_4.png", 
                                   "doors_templates/doors_5.png", "doors_templates/doors_6.png", 
                                   "doors_templates/doors_7.png"], 
                        threshold=0.98):
    # 1. Setup folders
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    image_files = glob.glob(os.path.join(input_folder, "*.png"))
    if not image_files:
        print(f"No PNG images found in {input_folder}")
        return

    print(f"Running Multi-Door Template Matching on {len(image_files)} images...")

    for img_path in image_files:
        img_rgb = cv2.imread(img_path)
        if img_rgb is None: continue
        output_img = img_rgb.copy()
        
        all_matches = [] # List of (x, y, w, h)
        
        # 2. Run detection for each door template
        for t_path in templates:
            template = cv2.imread(t_path)
            if template is None: continue
            th, tw = template.shape[:2]
            
            res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            
            for pt in zip(*loc[::-1]):
                is_duplicate = False
                for (mx, my, mw, mh) in all_matches:
                    # 15px proximity for doors
                    if abs(pt[0] - mx) < 15 and abs(pt[1] - my) < 15:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    all_matches.append((pt[0], pt[1], tw, th))

        # 3. Draw combined results (BLUE circles for doors)
        for (x, y, w, h) in all_matches:
            center = (x + w//2, y + h//2)
            cv2.circle(output_img, center, 15, (255, 0, 0), 2)
            
        save_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, f"door_match_{save_name}"), output_img)
        print(f"  {save_name}: Found {len(all_matches)} doors.")

if __name__ == "__main__":
    door_template_match(threshold=0.98)
