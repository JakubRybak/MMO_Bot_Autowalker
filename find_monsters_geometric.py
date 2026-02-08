import cv2
import numpy as np

def find_monsters(map_path, output_path="processed_mini_map.png"):
    img = cv2.imread(map_path)
    if img is None:
        print(f"Error: Could not load {map_path}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 1. Is it Red? (Relaxed Saturation/Value floor to 70)
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    output_img = img.copy()
    monster_count = 0
    print(f"Scanning {map_path} for monsters...")
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 30 < area < 150:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # 2. Is it Square? (Aspect Ratio)
            aspect_ratio = float(w)/h
            is_square = 0.7 <= aspect_ratio <= 1.4
            
            # 3. Is it Solid? (Relaxed Extent to 0.4)
            extent = float(area)/(w*h)
            is_solid = extent > 0.4
            
            if is_square and is_solid:
                monster_count += 1
                center = (x + w//2, y + h//2)
                cv2.circle(output_img, center, 12, (0, 255, 0), 2)
                print(f"  Monster found at {center} (Area: {area}, Extent: {extent:.2f})")

    cv2.imwrite(output_path, output_img)
    print(f"\nDetection complete! Found: {monster_count}")
    print(f"Result saved to: {output_path}")

if __name__ == "__main__":
    import sys
    input_map = sys.argv[1] if len(sys.argv) > 1 else "mini_map.png"
    output_name = sys.argv[2] if len(sys.argv) > 2 else "processed_mini_map.png"
    find_monsters(input_map, output_name)