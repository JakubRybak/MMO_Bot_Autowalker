import cv2
import numpy as np

def find_door_color(path):
    img = cv2.imread(path)
    if img is None: return
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Ultra broad mask to find ANY square of ANY color
    mask = cv2.inRange(hsv, np.array([0, 10, 10]), np.array([180, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Analyzing ALL objects in {path}...")
    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5:
            x, y, w, h = cv2.boundingRect(cnt)
            extent = float(area)/(w*h)
            aspect = float(w)/h
            
            c_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(c_mask, [cnt], -1, 255, -1)
            avg_hsv = cv2.mean(hsv, mask=c_mask)[:3]
            
            print(f"Object: Area={area:.1f}, Extent={extent:.2f}, Aspect={aspect:.2f}, HSV=({avg_hsv[0]:.1f}, {avg_hsv[1]:.1f}, {avg_hsv[2]:.1f})")

    # Sort by Y position to see Top vs Bottom
    candidates.sort(key=lambda x: x["pos"][1])
    
    for c in candidates:
        print(f"Pos: {c['pos']}, Area: {c['area']:.1f}, HSV: ({c['hsv'][0]:.1f}, {c['hsv'][1]:.1f}, {c['hsv'][2]:.1f})")

if __name__ == "__main__":
    find_door_color("image.png")
