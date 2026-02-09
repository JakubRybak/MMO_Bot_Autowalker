import cv2
import numpy as np

img = cv2.imread("small_location.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, w, _ = img.shape

print("Scanning for high-vibrancy pixels (Red/Blue)...")
for y in range(0, h, 5): # Scan every 5th pixel for speed
    for x in range(0, w, 5):
        p = hsv[y, x]
        # Red-ish or Blue-ish
        if p[1] > 100: 
            if (p[0] < 15 or p[0] > 165) or (100 < p[0] < 130):
                print(f"Interesting pixel at ({x},{y}): HSV={p}")
