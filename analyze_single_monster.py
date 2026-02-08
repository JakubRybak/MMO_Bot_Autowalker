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
    
    # Get average HSV of the whole sample (assuming it's mostly the monster)
    avg_hsv = cv2.mean(hsv)[:3]
    print(f"Average HSV: {avg_hsv}")
    
    # Let's find the main contour to get geometric stats
    # We'll use a broad red mask to find it first
    mask = cv2.bitwise_or(
        cv2.inRange(hsv, np.array([0, 50, 50]), np.array([20, 255, 255])),
        cv2.inRange(hsv, np.array([160, 50, 50]), np.array([180, 255, 255]))
    )
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No red contour found in sample.")
        return
    
    # Assume the largest contour is the monster
    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    x, y, sw, sh = cv2.boundingRect(cnt)
    extent = float(area)/(sw*sh)
    aspect = float(sw)/sh
    
    # Get average color of just the contour
    c_mask = np.zeros(mask.shape, np.uint8)
    cv2.drawContours(c_mask, [cnt], -1, 255, -1)
    cnt_hsv = cv2.mean(hsv, mask=c_mask)[:3]
    
    print(f"Monster Stats:")
    print(f"  Area: {area}")
    print(f"  Extent (Solidity): {extent:.2f}")
    print(f"  Aspect Ratio: {aspect:.2f}")
    print(f"  Exact HSV: {cnt_hsv}")

if __name__ == "__main__":
    analyze_sample("single_monster.png")
