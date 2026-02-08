import cv2
import numpy as np

def final_debug(path):
    img = cv2.imread(path)
    if img is None: return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 1. Broad Monster Mask
    m_mask = cv2.bitwise_or(
        cv2.inRange(hsv, np.array([0, 50, 50]), np.array([40, 255, 255])),
        cv2.inRange(hsv, np.array([160, 50, 50]), np.array([180, 255, 255]))
    )
    
    # 2. Broad Door Mask
    d_mask = cv2.inRange(hsv, np.array([90, 30, 30]), np.array([150, 255, 255]))
    
    def get_stats(mask, label):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"\n--- {label} Candidates ---")
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5:
                x, y, w, h = cv2.boundingRect(cnt)
                extent = float(area)/(w*h) if w*h > 0 else 0
                aspect = float(w)/h if h > 0 else 0
                center = (x+w//2, y+h//2)
                print(f"Pos: {center}, Area: {area:.1f}, Extent: {extent:.2f}, Aspect: {aspect:.2f}")

    get_stats(m_mask, "RED (MONSTER)")
    get_stats(d_mask, "BLUE (DOOR)")

if __name__ == "__main__":
    final_debug("image.png")