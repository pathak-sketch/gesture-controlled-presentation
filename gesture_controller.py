import time
import pyautogui
import math

class GestureController:
    def __init__(self):
        self.prev_x = None
        self.last_action_time = 0
        self.cooldown = 1.0  # Cooldown between gestures in seconds

    def detect_gesture(self, landmarks):
        """
        Detects gestures based on hand landmarks.
        Returns the action name if a gesture is detected, else None.
        """
        if not landmarks:
            self.prev_x = None
            return None

        # Use index finger tip (landmark 8) for tracking
        # Landmarks are normalized [0, 1]
        x = landmarks[8].x
        y = landmarks[8].y

        current_time = time.time()
        
        # Debounce/Cooldown
        if current_time - self.last_action_time < self.cooldown:
            # Update prev_x while in cooldown to have fresh start reference
            self.prev_x = x 
            return None

        action = None

        if self.prev_x is not None:
            dx = x - self.prev_x
            
            # Swipe Right (Next Slide)
            # Experimentally, a swipe across screen is > 0.1 or 0.2 change in x
            if dx > 0.15: 
                action = "Next"
                pyautogui.press('right')
                
            # Swipe Left (Previous Slide)
            elif dx < -0.15:
                action = "Previous"
                pyautogui.press('left')

        self.prev_x = x

        if action:
            self.last_action_time = current_time
            return action
        
        return None
