import cv2
import pytesseract
import numpy as np
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_text(text):
    text = text.replace(".l", "1").replace(".1", "1").replace(".2", "2").replace(".s", " s")
    return re.sub(r'[^a-zA-Z0-9ąęćłńóśźżĄĘĆŁŃÓŚŹŻ\s]', '', text).strip()

def test_on_samples(image_path):
    img = cv2.imread(image_path)
    if img is None: return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    
    raw_text = pytesseract.image_to_string(thresh, lang='pol+eng', config='--psm 6')
    cleaned = clean_text(raw_text)
    
    print("\n--- " + image_path + " ---")
    print("Raw Tesseract: '" + raw_text.strip() + "'")
    print("Cleaned Text:  '" + cleaned + "'")

if __name__ == "__main__":
    test_on_samples("location_tooltip.png")
    test_on_samples("location_tooltip_2.png")