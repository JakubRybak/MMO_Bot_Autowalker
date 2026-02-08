import cv2
import numpy as np
import sys

def analyze(path):
    img = cv2.imread(path)
    if img is None: return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Ultra generous mask
    mask = cv2.inRange(hsv, np.array([100, 10, 10]), np.array([140, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"--- Analysis for {path} ---")
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 10:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area)/(w*h)
            aspect = float(w)/h
            c_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(c_mask, [cnt], -1, 255, -1)
            avg_hsv = cv2.mean(hsv, mask=c_mask)[:3]
            print(f"Area: {area:.1f}, Extent: {extent:.2f}, Aspect: {aspect:.2f}, HSV: {avg_hsv}")

if __name__ == "__main__":
    analyze(sys.argv[1] if len(sys.argv) > 1 else "image.png")
