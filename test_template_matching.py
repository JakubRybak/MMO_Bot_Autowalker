import cv2
import numpy as np
import os

def test_template_matching(target_image_path, template_path, threshold=0.8):
    # 1. Load images
    img_rgb = cv2.imread(target_image_path)
    if img_rgb is None:
        print(f"Error: Could not load target {target_image_path}")
        return
        
    template = cv2.imread(template_path)
    if template is None:
        print(f"Error: Could not load template {template_path}. Create a tiny 1:1 icon first!")
        return
        
    h, w = template.shape[:2]

    # 2. Perform Match
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    
    # 3. Find all locations above threshold
    loc = np.where(res >= threshold)
    
    matches = []
    output_img = img_rgb.copy()
    
    for pt in zip(*loc[::-1]): # Switch x and y
        # Check for duplicates (proximity filter)
        is_new = True
        for m in matches:
            if abs(pt[0] - m[0]) < 5 and abs(pt[1] - m[1]) < 5:
                is_new = False
                break
        if is_new:
            matches.append(pt)
            # Draw result
            cv2.rectangle(output_img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

    print(f"Template Matching for {template_path}:")
    print(f"  Found {len(matches)} matches in {target_image_path}")
    
    cv2.imwrite("template_match_result.png", output_img)
    print("Result saved to: template_match_result.png")

if __name__ == "__main__":
    # Test on example.png with the monster_exact icon
    test_template_matching("example.png", "monster_exact.png", threshold=0.8)
