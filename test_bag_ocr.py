import cv2
import pytesseract
import os

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_bag_ocr():
    path = "bag_debug_preprocessed.png"
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run debug_bag_capture.py first!")
        return
        
    img = cv2.imread(path)
    
    # Use the bot's exact Tesseract settings
    config = '--psm 6 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(img, lang='eng', config=config).strip()
    
    print("\n--- OCR Test Results ---")
    print(f"File: {path}")
    print(f"Detected Text: '{text}'")
    print(f"Length of text: {len(text)}")
    
    if text in ["0", "1"]:
        print("RESULT: This WOULD trigger a sell routine!")
    else:
        print("RESULT: This would NOT trigger a sell routine.")

if __name__ == "__main__":
    test_bag_ocr()
