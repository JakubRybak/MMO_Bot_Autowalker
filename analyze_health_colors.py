import cv2
import numpy as np
from collections import Counter

def analyze_health(path):
    img = cv2.imread(path)
    if img is None: return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w, _ = img.shape
    
    # Get all colors to see the health bar red vs background
    all_pixels = hsv.reshape(-1, 3)
    counts = Counter([tuple(p) for p in all_pixels])
    
    print(f"--- Analysis of {path} ({w}x{h}) ---")
    print("Top 10 Colors (H, S, V):")
    for color, count in counts.most_common(10):
        print(f"  {color}: {count}")

if __name__ == "__main__":
    analyze_health("health_bar.png")
