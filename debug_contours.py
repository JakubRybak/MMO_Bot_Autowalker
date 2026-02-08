import cv2
import numpy as np

img = cv2.imread("doors.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, np.array([110, 30, 50]), np.array([130, 150, 255]))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"Found {len(contours)} contours")
for cnt in contours:
    print(f"Contour Area: {cv2.contourArea(cnt)}")
