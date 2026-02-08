import cv2
import numpy as np

img = cv2.imread("doors.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, w, _ = img.shape
print(f"Image dimensions: {w}x{h}")
for y in range(h):
    for x in range(w):
        p = hsv[y, x]
        print(f"Pixel ({x},{y}): HSV=({p[0]}, {p[1]}, {p[2]})")
