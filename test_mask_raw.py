import cv2
import numpy as np

img = cv2.imread("doors.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, np.array([110, 30, 50]), np.array([130, 150, 255]))
pixels = cv2.countNonZero(mask)
print(f"Mask has {pixels} active pixels")
cv2.imwrite("debug_mask_raw.png", mask)
