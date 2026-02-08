import cv2
import numpy as np

def analyze_image(image_path):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return

    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    output = img.copy()

    # --- 1. Detect Player (Yellow Box) ---
    # Yellow is typically around Hue 30.
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Find contours for yellow
    contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # Filter small noise
        if cv2.contourArea(cnt) > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            # Draw green rectangle around player box
            cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(output, "Player Area", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw center point
            center_x, center_y = x + w//2, y + h//2
            cv2.circle(output, (center_x, center_y), 3, (0, 255, 0), -1)

    # --- 2. Detect Monsters (White/Gray Squares) ---
    # These are low saturation, high brightness
    lower_gray = np.array([0, 0, 180])   # Very low saturation, high brightness
    upper_gray = np.array([180, 50, 255]) 
    mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)

    contours, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Filter based on expected size of monster squares (adjust these values)
        if 50 < area < 1000: 
            x, y, w, h = cv2.boundingRect(cnt)
            # Draw Red rectangle around monsters
            cv2.rectangle(output, (x, y), (x+w, y+h), (0, 0, 255), 2)
            # cv2.putText(output, "Mob", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # --- 3. Detect Exits (Blue Squares) ---
    # Blue is typically around Hue 110-130
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) > 20:
            x, y, w, h = cv2.boundingRect(cnt)
            # Draw Blue rectangle around exits
            cv2.rectangle(output, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(output, "Exit", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # Save the result
    cv2.imwrite("result.png", output)
    print("Analysis complete. Saved 'result.png'.")

if __name__ == "__main__":
    analyze_image("image copy.png")
