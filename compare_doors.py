import cv2
import numpy as np

def analyze(path):
    img = cv2.imread(path)
    if img is None: return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Generous mask to catch both good and bad
    mask = cv2.inRange(hsv, np.array([80, 10, 10]), np.array([150, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    results = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area)/(w*h) if w*h > 0 else 0
            aspect = float(w)/h if h > 0 else 0
            
            c_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(c_mask, [cnt], -1, 255, -1)
            avg_hsv = cv2.mean(hsv, mask=c_mask)[:3]
            results.append((area, extent, aspect, avg_hsv))
    return results

if __name__ == "__main__":
    print("--- DOORS (GOOD) ---")
    good = analyze("doors.png")
    if good:
        for r in good:
            print(f"Area: {r[0]:.1f}, Extent: {r[1]:.2f}, Aspect: {r[2]:.2f}, HSV: {r[3]}")
    else:
        print("No objects found in doors.png")
        
    print("\n--- DOOR_BAD (BAD) ---")
    bad = analyze("door_bad.png")
    if bad:
        for r in bad:
            print(f"Area: {r[0]:.1f}, Extent: {r[1]:.2f}, Aspect: {r[2]:.2f}, HSV: {r[3]}")
    else:
        print("No blueish objects found in door_bad.png")