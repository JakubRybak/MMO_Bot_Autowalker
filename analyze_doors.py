import cv2
import numpy as np
import sys
from collections import Counter

def analyze_regions(image_path):
    img = cv2.imread(image_path)
    if img is None: return
    h, w, _ = img.shape
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define 3 regions based on user description
    # Top center, Right center, Bottom center
    regions = {
        "TOP": (0, h//3, w//4, 3*w//4),
        "RIGHT": (h//4, 3*h//4, 3*w//4, w),
        "BOTTOM": (2*h//3, h, w//4, 3*w//4)
    }
    
    for name, (y1, y2, x1, x2) in regions.items():
        print(f"\n--- Analyzing {name} Region ---")
        roi_hsv = hsv[y1:y2, x1:x2]
        
        # Look for BROAD BLUE
        mask = cv2.inRange(roi_hsv, np.array([80, 30, 30]), np.array([140, 255, 255]))
        blue_pixels = roi_hsv[mask > 0]
        
        if len(blue_pixels) > 0:
            counts = Counter([tuple(p) for p in blue_pixels])
            print("Top 3 Blue Colors (H, S, V):")
            for color, count in counts.most_common(3):
                print(f"  Color: {color}, Count: {count}")
        else:
            print("  No blue found in this region.")

if __name__ == "__main__":
    analyze_regions("image.png")