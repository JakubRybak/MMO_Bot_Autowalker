import cv2
import numpy as np

def find_doors(map_path, output_path="processed_doors_map.png"):
    img = cv2.imread(map_path)
    if img is None:
        print(f"Error: Could not load {map_path}")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 1. Color Mask (Hue 110-125, S>100, V>100)
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([125, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Clean mask
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    output_img = img.copy()
    door_count = 0
    print(f"\nScanning {map_path} for doors...")
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 10:
            x, y, sw, sh = cv2.boundingRect(cnt)
            extent = float(area)/(sw*sh) if sw*sh > 0 else 0
            aspect = float(sw)/sh if sh > 0 else 0
            
            # Wide aspect ratio to catch long/tall doors on edges
            is_door = (35 < area < 200) and (extent > 0.40) and (0.3 < aspect < 4.0)
            
            print(f"  Candidate at ({(x+sw//2)}, {(y+sh//2)}): Area={area:.1f}, Extent={extent:.2f}, Aspect={aspect:.2f} -> {'PASS' if is_door else 'FAIL'}")
            
            if is_door:
                door_count += 1
                center = (x + sw//2, y + sh//2)
                cv2.circle(output_img, center, 15, (255, 0, 0), 2)

    cv2.imwrite(output_path, output_img)
    print(f"Total doors found: {door_count}")
    print(f"Result saved to: {output_path}")

if __name__ == "__main__":
    import sys
    input_map = sys.argv[1] if len(sys.argv) > 1 else "mini_map.png"
    output_name = sys.argv[2] if len(sys.argv) > 2 else "processed_doors_map.png"
    find_doors(input_map, output_name)