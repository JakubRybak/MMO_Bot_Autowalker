import cv2
import numpy as np

def analyze_sample(path):
    img = cv2.imread(path)
    if img is None:
        print(f"Error: Could not load {path}")
        return
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w, _ = img.shape
    print(f"Dimensions: {w}x{h}")
    
    # Broad mask to find the object first (assuming it's blueish based on previous context)
    mask = cv2.inRange(hsv, np.array([90, 30, 30]), np.array([150, 255, 255]))
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No blue contour found in sample. Scanning ALL pixels...")
        # Fallback: scan all pixels to see what color is actually there
        all_pixels = hsv.reshape(-1, 3)
        from collections import Counter
        counts = Counter([tuple(p) for p in all_pixels])
        print("Top colors (H, S, V):")
        for color, count in counts.most_common(5):
            print(f"  {color}: {count}")
        return
    
    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    x, y, sw, sh = cv2.boundingRect(cnt)
    extent = float(area)/(sw*sh) if sw*sh > 0 else 0
    aspect = float(sw)/sh if sh > 0 else 0
    
    c_mask = np.zeros(mask.shape, np.uint8)
    cv2.drawContours(c_mask, [cnt], -1, 255, -1)
    cnt_hsv = cv2.mean(hsv, mask=c_mask)[:3]
    
    print(f"Door Stats:")
    print(f"  Area: {area}")
    print(f"  Extent (Solidity): {extent:.2f}")
    print(f"  Aspect Ratio: {aspect:.2f}")
    print(f"  Exact HSV: {cnt_hsv}")

if __name__ == "__main__":
    analyze_sample("door.png")
