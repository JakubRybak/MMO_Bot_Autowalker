import cv2
import numpy as np

def extract_red_hexes(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read {image_path}")
        return

    # Convert to HSV for easier red detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define broad red range
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Get coordinates of all red pixels
    red_pixels = img[mask > 0]

    # Convert BGR to HEX and get unique values
    unique_hexes = set()
    for pixel in red_pixels:
        # OpenCV uses BGR
        hex_code = '#{:02x}{:02x}{:02x}'.format(pixel[2], pixel[1], pixel[0])
        unique_hexes.add(hex_code)

    print(f"Found {len(unique_hexes)} unique red HEX codes in {image_path}:")
    for hex_code in sorted(list(unique_hexes)):
        print(hex_code)

if __name__ == "__main__":
    extract_red_hexes("example.png")
