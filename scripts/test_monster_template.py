import cv2
import numpy as np
import os
import glob

def dual_template_match(input_folder="data", output_folder="exact_matching", 
                        templates=["monster_templates/monster_exact.png", "monster_templates/monster_medium.png", 
                                   "monster_templates/monster_medium_2.png", "monster_templates/monster_big.png"], 
                        threshold=0.95):
    # 1. Setup folders
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    image_files = glob.glob(os.path.join(input_folder, "*.png"))
    if not image_files:
        print(f"No PNG images found in {input_folder}")
        return

    print(f"Running Multi-Template Matching {templates} on {len(image_files)} images...")

    for img_path in image_files:
        img_rgb = cv2.imread(img_path)
        if img_rgb is None: continue
        output_img = img_rgb.copy()
        
        all_matches = [] # List of (x, y, w, h)
        
        # 2. Run detection for each template
        for t_path in templates:
            template = cv2.imread(t_path)
            if template is None: continue
            th, tw = template.shape[:2]
            
            res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            
            for pt in zip(*loc[::-1]):
                # Proximity filter to avoid duplicate boxes for same template
                is_duplicate = False
                for (mx, my, mw, mh) in all_matches:
                    # If centers are closer than 10px, it's the same monster
                    if abs(pt[0] - mx) < 10 and abs(pt[1] - my) < 10:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    all_matches.append((pt[0], pt[1], tw, th))

        # 3. Draw combined results
        for (x, y, w, h) in all_matches:
            cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
        save_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, f"dual_{save_name}"), output_img)
        print(f"  {save_name}: Found {len(all_matches)} total monsters.")

if __name__ == "__main__":
    dual_template_match()
