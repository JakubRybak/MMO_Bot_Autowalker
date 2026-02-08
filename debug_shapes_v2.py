import cv2
import numpy as np

def analyze_monsters(path):
    img = cv2.imread(path)
    if img is None: return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Very broad mask to catch everything red-ish
    mask = cv2.bitwise_or(
        cv2.inRange(hsv, np.array([0, 50, 50]), np.array([40, 255, 255])),
        cv2.inRange(hsv, np.array([160, 50, 50]), np.array([180, 255, 255]))
    )
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    stats = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 2: # Very low threshold to see everything
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area)/(w*h) if w*h > 0 else 0
            cnt_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(cnt_mask, [cnt], -1, 255, -1)
            avg_sat = cv2.mean(hsv[:,:,1], mask=cnt_mask)[0]
            avg_hue = cv2.mean(hsv[:,:,0], mask=cnt_mask)[0]
            stats.append((area, extent, avg_sat, avg_hue))
            
    stats.sort(key=lambda x: x[0], reverse=True)
    print(f"Stats for top 10 red objects in {path}:")
    for s in stats[:10]:
        print(f"Area: {s[0]:.1f}, Extent: {s[1]:.2f}, Saturation: {s[2]:.1f}, Hue: {s[3]:.1f}")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "image copy 2.png"
    analyze_monsters(path)
