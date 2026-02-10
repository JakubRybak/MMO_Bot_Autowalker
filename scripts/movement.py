import time
import numpy as np
import keyboard
from scripts.vision_engine import get_vision_data

def wait_until_stopped(sct, monitor, player_pos, interrupt_if_mob=False, ignored_mobs=None):
    """Returns True if stopped, False if stuck, or 'monster' if interrupted."""
    last_pos = player_pos
    last_move_time = time.time()
    stable_count = 0
    while stable_count < 5:
        if keyboard.is_pressed('esc'): return True
        time.sleep(0.05)
        new_player, new_mobs, _ = get_vision_data(sct, monitor)
        
        # INTERRUPTION LOGIC: If we are walking to an exit and see a valid monster
        if interrupt_if_mob and new_mobs:
            valid_mobs = [m for m in new_mobs if not any(np.linalg.norm(np.array(m)-np.array(i)) < 15 for i in (ignored_mobs or {}))]
            if valid_mobs:
                return "monster"

        if new_player:
            if np.linalg.norm(np.array(new_player) - np.array(last_pos)) >= 1.5:
                last_move_time = time.time()
                stable_count = 0
            else:
                stable_count += 1
            last_pos = new_player
        
        if time.time() - last_move_time > 5.0: return False
    return True
