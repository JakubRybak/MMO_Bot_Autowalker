import cv2
import numpy as np
from collections import Counter

def find_exact_color(path):
    img = cv2.imread(path)
    if img is None: return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define a broad BLUE range
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Get all blue pixels
    blue_pixels = hsv[mask > 0]
    
    # Count occurrences of each (H, S, V)
    pixel_counts = Counter([tuple(p) for p in blue_pixels])
    
    print("Top 5 most common BLUE colors (H, S, V):")
    for color, count in pixel_counts.most_common(5):
        print(f"Color: {color}, Count: {count}")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "image.png"
    find_exact_color(path)
