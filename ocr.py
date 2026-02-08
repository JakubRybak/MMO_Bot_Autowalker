import cv2
import pytesseract
import numpy as np
import mss

# --- CONFIGURATION ---
# UPDATE THIS PATH if you installed Tesseract somewhere else!
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def read_tooltip(monitor_area, save_path=None):
    """
    Captures a small area of the screen and tries to read text.
    'monitor_area' should be a dict: {'top': y, 'left': x, 'width': w, 'height': h}
    """
    with mss.mss() as sct:
        # Capture the region
        img = np.array(sct.grab(monitor_area))
        
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        
        # Resize image (2x larger) - Tesseract likes larger text
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Thresholding to make text pop (White text on black background usually)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Read text (Polish + English)
        # --psm 3 means "Fully automatic page segmentation, but no OSD"
        # This proved more reliable than PSM 7 in debug tests
        text = pytesseract.image_to_string(thresh, lang='pol+eng', config='--psm 3')
        
        clean_text = text.strip()
        # Remove special chars if needed
        return clean_text

if __name__ == "__main__":
    import pyautogui
    import time
    print("Hover over a map name tooltip in 3 seconds...")
    time.sleep(3)
    x, y = pyautogui.position()
    
    # Adjusted Offsets (Attempt 3):
    # Capture a larger vertical slice to catch the text
    box = {
        "top": y - 5,    # Start slightly above cursor
        "left": x + 25,   # Right of cursor
        "width": 300,     # Wide enough for long names
        "height": 40      # Tall enough for 2 lines of text
    }
    
    print("Capturing...")
    text = read_tooltip(box)
    print(f"Read Text: '{text}'")
