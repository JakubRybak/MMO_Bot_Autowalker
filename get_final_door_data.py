import cv2
import numpy as np

img = cv2.imread("doors.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Extremely broad mask to see everything blueish
mask = cv2.inRange(hsv, np.array([90, 10, 10]), np.array([150, 255, 255]))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 2:
        x, y, w, h = cv2.boundingRect(cnt)
        extent = float(area)/(w*h)
        # Average HSV of the door
        c_mask = np.zeros(mask.shape, np.uint8)
        cv2.drawContours(c_mask, [cnt], -1, 255, -1)
        avg_hsv = cv2.mean(hsv, mask=c_mask)[:3]
        print(f"Area: {area}, Extent: {extent:.2f}, HSV: {avg_hsv}")
