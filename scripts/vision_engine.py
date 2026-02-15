import cv2
import numpy as np
import os
import glob

# --- Load Templates at Startup ---
MONSTER_TEMPLATES = []
for f in glob.glob("monster_templates/*.png"):
    t = cv2.imread(f)
    if t is not None:
        MONSTER_TEMPLATES.append(t)

DOOR_TEMPLATES = []
for f in glob.glob("doors_templates/*.png"):
    t = cv2.imread(f)
    if t is not None:
        DOOR_TEMPLATES.append(t)

def clean_text(text):
    """Removes special characters and fixes common OCR errors."""
    import re
    text = text.replace(".l", "1").replace(".1", "1").replace(".2", "2").replace(".s", " s")
    return re.sub(r'[^a-zA-Z0-9ąęćłńóśźżĄĘĆŁŃÓŚŹŻ\s]', '', text).strip()

def get_vision_data(sct, monitor):
    """Captures screen and returns player position, monsters, exits using Template Matching."""
    img = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 1. Player Dot (Keep Color-based detection as it is unique and works well)
    lower_cyan = np.array([80, 100, 200])
    upper_cyan = np.array([100, 255, 255])
    mask_cyan = cv2.inRange(hsv, lower_cyan, upper_cyan)
    contours_p, _ = cv2.findContours(mask_cyan, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    player_pos = None
    for cnt in contours_p:
        if cv2.contourArea(cnt) > 5:
            x, y, w, h = cv2.boundingRect(cnt)
            player_pos = (x + w//2, y + h//2)
            break
            
    if player_pos is None:
        mask_yellow = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([40, 255, 255]))
        contours_y, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_y:
            if cv2.contourArea(cnt) > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                player_pos = (x + w//2, y + h//2)
                break

    # 2. Monsters (Template Matching - Threshold 0.95)
    mobs = []
    for template in MONSTER_TEMPLATES:
        th, tw = template.shape[:2]
        res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.95)
        for pt in zip(*loc[::-1]):
            # Proximity check
            if not any(abs(pt[0] - m[0]) < 10 and abs(pt[1] - m[1]) < 10 for m in mobs):
                mobs.append((pt[0] + tw//2, pt[1] + th//2))

    # 3. Exits (Template Matching - Threshold 0.98)
    exits = []
    for template in DOOR_TEMPLATES:
        th, tw = template.shape[:2]
        res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.98)
        for pt in zip(*loc[::-1]):
            # Proximity check
            if not any(abs(pt[0] - e[0]) < 15 and abs(pt[1] - e[1]) < 15 for e in exits):
                exits.append((pt[0] + tw//2, pt[1] + th//2))

    return player_pos, mobs, exits
