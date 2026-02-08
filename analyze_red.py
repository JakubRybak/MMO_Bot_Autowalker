import cv2
import numpy as np

def analyze_image(path):
    img = cv2.imread(path)
    if img is None:
        print(f"Could not read {path}")
        return
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Standard Red ranges in HSV
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    res = cv2.bitwise_and(img, img, mask=mask)
    
    # Find contours to see if we found the dots
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} red objects")
    
    cv2.imwrite("debug_red_detection.png", res)
    print("Saved debug_red_detection.png")

if __name__ == "__main__":
    analyze_image("image copy.png")
