import cv2
import numpy as np
import os
import glob

def batch_template_match(input_folder="tests", output_folder="exact_matching", template_path="monster_exact.png", threshold=0.8):
    # 1. Load Template
    template = cv2.imread(template_path)
    if template is None:
        print(f"Error: Could not load template {template_path}")
        return
    h, w = template.shape[:2]

    # 2. Get images
    image_files = glob.glob(os.path.join(input_folder, "*.png"))
    if not image_files:
        print(f"No PNG images found in {input_folder}")
        return

    print(f"Running Template Matching ({template_path}) on {len(image_files)} images...")

    for img_path in image_files:
        img_rgb = cv2.imread(img_path)
        if img_rgb is None: continue
        
        # Perform Match
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        
        matches = []
        output_img = img_rgb.copy()
        
        for pt in zip(*loc[::-1]):
            is_new = True
            for m in matches:
                # 10px proximity filter
                if abs(pt[0] - m[0]) < 10 and abs(pt[1] - m[1]) < 10:
                    is_new = False
                    break
            if is_new:
                matches.append(pt)
                cv2.rectangle(output_img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
        
        save_name = os.path.basename(img_path)
        cv2.imwrite(os.path.join(output_folder, f"match_{save_name}"), output_img)
        print(f"  {save_name}: Found {len(matches)} matches.")

if __name__ == "__main__":
    batch_template_match(template_path="monster_big.png", threshold=0.9)
