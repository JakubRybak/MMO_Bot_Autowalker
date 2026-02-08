import cv2
import numpy as np

def scan_all_shapes(path):
    img = cv2.imread(path)
    if img is None: return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Very generous mask to catch any "blueish" door
    mask = cv2.inRange(hsv, np.array([90, 20, 20]), np.array([150, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Scanning all blueish shapes in {path}:")
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 2:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area)/(w*h) if w*h > 0 else 0
            aspect = float(w)/h if h > 0 else 0
            
            # Get average color
            c_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(c_mask, [cnt], -1, 255, -1)
            avg_hsv = cv2.mean(hsv, mask=c_mask)[:3]
            
            print(f"  Area: {area:.1f}, Extent: {extent:.2f}, Aspect: {aspect:.2f}, HSV: ({avg_hsv[0]:.1f}, {avg_hsv[1]:.1f}, {avg_hsv[2]:.1f})")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "door.png"
    scan_all_shapes(path)
