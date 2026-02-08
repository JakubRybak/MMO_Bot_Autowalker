import cv2
import numpy as np
from collections import Counter

def analyze_doors_perfectly(path):
    img = cv2.imread(path)
    if img is None:
        print(f"Error: Could not load {path}")
        return
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 1. Get ALL colors in the image to find the "Door Blue"
    all_pixels = hsv.reshape(-1, 3)
    counts = Counter([tuple(p) for p in all_pixels])
    
    print("Top 10 most common colors in the image (H, S, V):")
    # Filter out very dark background pixels
    valid_colors = [c for c in counts.most_common(50) if c[0][2] > 30] 
    for color, count in valid_colors[:10]:
        print(f"  Color: {color}, Count: {count}")

    # Use the most frequent color as a seed for the mask
    if valid_colors:
        top_h = valid_colors[0][0][0]
        print(f"\nAnalyzing shapes with Hue around {top_h}...")
        lower = np.array([top_h-5, 30, 30])
        upper = np.array([top_h+5, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5:
                x, y, w, h = cv2.boundingRect(cnt)
                extent = float(area)/(w*h) if w*h > 0 else 0
                aspect = float(w)/h if h > 0 else 0
                print(f"  Area: {area}, Extent: {extent:.2f}, Aspect: {aspect:.2f}, Size: {w}x{h}")

if __name__ == "__main__":
    analyze_doors_perfectly("doors.png")