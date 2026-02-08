import cv2
import numpy as np

def analyze_shapes(path):
    img = cv2.imread(path)
    if img is None:
        return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Total objects found: {len(contours)}")
    stats = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        extent = float(area)/(w*h) if w*h > 0 else 0
        aspect = float(w)/h if h > 0 else 0
        stats.append((area, extent, aspect))
    
    # Sort by area descending
    stats.sort(key=lambda x: x[0], reverse=True)
    for i, s in enumerate(stats[:20]):
        print(f"Object {i}: Area={s[0]}, Extent={s[1]:.2f}, Aspect={s[2]:.2f}")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "image copy.png"
    analyze_shapes(path)
