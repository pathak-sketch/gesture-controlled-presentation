"""Hand detection wrapper.

This file tries to import MediaPipe, but if it's not available or incompatible
we provide a lightweight fallback that keeps the web app usable (no detection,
just returns empty landmarks). This avoids hard-failing on import when the
server is started purely to manage shares or admin tasks.
"""
import cv2
try:
    import mediapipe as mp  # type: ignore
    _HAS_MEDIAPIPE = True
except Exception:
    mp = None
    _HAS_MEDIAPIPE = False


class HandTracker:
    def __init__(self):
        if not _HAS_MEDIAPIPE:
            # Lazy warning; avoid printing during import-heavy operations
            print("[warning] MediaPipe not available — hand detection disabled.")
            self.hands = None
            self.mp_hands = None
            self.mp_draw = None
            return

        # Old-style solutions API (if available)
        try:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7,
            )
            self.mp_draw = mp.solutions.drawing_utils
        except Exception:
            # If the installed MediaPipe uses a different API (Tasks),
            # gracefully disable detection here and avoid raising at import.
            print("[warning] MediaPipe import succeeded but Hands API not available — detection disabled.")
            self.hands = None
            self.mp_hands = None
            self.mp_draw = None

    def detect_hands(self, frame):
        """Return (landmarks, annotated_frame).

        If detection isn't available, return empty landmarks and the input frame.
        """
        if not self.hands:
            return [], frame

        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            landmarks = []
            if getattr(results, 'multi_hand_landmarks', None):
                for hand in results.multi_hand_landmarks:
                    for lm in hand.landmark:
                        landmarks.append(lm)
                    # draw landmarks for visual feedback
                    try:
                        self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)
                    except Exception:
                        pass
            return landmarks, frame
        except Exception:
            return [], frame
