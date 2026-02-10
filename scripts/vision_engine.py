import cv2
import numpy as np

def clean_text(text):
    """Removes special characters and fixes common OCR errors."""
    import re
    text = text.replace(".l", "1").replace(".1", "1").replace(".2", "2").replace(".s", " s")
    return re.sub(r'[^a-zA-Z0-9ąęćłńóśźżĄĘĆŁŃÓŚŹŻ\s]', '', text).strip()

def get_vision_data(sct, monitor):
    """Captures screen and returns player position, monsters, exits."""
    img = np.array(sct.grab(monitor))
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = np.ones((3,3), np.uint8)

    # 1. Player Dot
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

    # 2. Monsters (Red/Orange) - Absolute Perfect Geometric Match
    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 70])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_mobs = cv2.bitwise_or(mask1, mask2)

    if player_pos:
        cv2.circle(mask_mobs, player_pos, 8, 0, -1) 
    
    contours_m, _ = cv2.findContours(mask_mobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mobs = []
    for cnt in contours_m:
        area = cv2.contourArea(cnt)
        if 30 < area < 400:
            x, y, sw, sh = cv2.boundingRect(cnt)
            aspect_ratio = float(sw)/sh
            extent = float(area)/(sw*sh)
            if extent > 0.4 and 0.7 <= aspect_ratio <= 1.4:
                mobs.append((x + sw//2, y + sh//2))

    # 3. Exits (Blue Squares) - Absolute Perfect Geometric Match
    lower_blue = np.array([110, 100, 100])
    upper_blue = np.array([125, 255, 255])
    mask_doors = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_doors = cv2.morphologyEx(mask_doors, cv2.MORPH_CLOSE, kernel)
    
    contours_e, _ = cv2.findContours(mask_doors, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    exits = []
    for cnt in contours_e:
        area = cv2.contourArea(cnt)
        if 35 < area < 400:
            x, y, sw, sh = cv2.boundingRect(cnt)
            aspect_ratio = float(sw)/sh
            extent = float(area)/(sw*sh)
            if extent > 0.4 and 0.3 < aspect_ratio < 4.0:
                exits.append((x + sw//2, y + sh//2))

    return player_pos, mobs, exits
