
import cv2
import numpy as np
from collections import deque
import time
import pyvirtualcam
from hand_tracker import HandTracker
from gesture_controller import GestureController
from voice_controller import VoiceController
from camera_manager import CameraManager

print("Initializing camera with robust recovery system...")
camera_manager = CameraManager(camera_indices=[0, 1, -1], width=640, height=480)

if camera_manager.cap is None or not camera_manager.cap.isOpened():
    print("""
    ⚠️  CAMERA ACCESS FAILED ⚠️
    
    Your camera could not be accessed. Common fixes:
    
    1. WINDOWS PRIVACY SETTINGS (Most Common):
       - Press Win+I to open Settings
       - Go to Privacy & Security → Camera
       - Enable "Let desktop apps access your camera"
       
    2. CLOSE OTHER APPS using the camera:
       - Teams, Zoom, Skype, Discord
       - Windows Camera app
       - Any browser tabs using webcam
       
    3. RESTART this application after fixing
    
    Exiting...
    """)
    exit(1)

cap = camera_manager.cap  # Use managed camera

tracker = HandTracker()
gesture = GestureController()
voice = VoiceController()

# Start voice listening
voice.start_listening()

# Visual feedback state
trail_points = deque(maxlen=20)
current_action = None
action_time = 0

# Get webcam resolution
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20

print(f"Webcam resolution: {width}x{height}")


# Try to initialize virtual camera
cam = None
try:
    cam = pyvirtualcam.Camera(width=width, height=height, fps=fps)
    print(f"Virtual Camera Output: {cam.device}")
except Exception as e:
    print(f"Warning: Command failed: {e}")
    print("Running in local mode only. Install OBS Studio for virtual camera support.")

try:
    while True:
        success, frame = camera_manager.read_frame()
        if not success or frame is None:
            # Wait briefly before retry
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape

        landmarks, frame = tracker.detect_hands(frame)

        if landmarks:
            # Get index finger tip (id 8) for trail
            index_x, index_y = int(landmarks[8].x * w), int(landmarks[8].y * h)
            trail_points.append((index_x, index_y))

            # Draw trail
            for i in range(1, len(trail_points)):
                thickness = int(np.sqrt(20 / float(len(trail_points) - i + 1)) * 5)
                cv2.line(frame, trail_points[i - 1], trail_points[i], (0, 255, 255), thickness)
        else:
            trail_points.clear()

        # Check for gestures
        action = gesture.detect_gesture(landmarks)
        
        # Check for voice commands
        voice_cmd = voice.get_latest_command()
        
        if voice_cmd:
            action = voice_cmd # Override/Use voice command

        if action:
            print(f"Action: {action}")
            current_action = action
            action_time = time.time()

        # Display action text for 1 second
        if current_action and time.time() - action_time < 1.0:
            cv2.putText(frame, current_action, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            current_action = None

        cv2.imshow("Gesture Presentation Control", frame)
        
        # Send to virtual camera if available
        if cam:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cam.send(frame_rgb)
            cam.sleep_until_next_frame()

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    voice.stop()
    if cam:
        cam.close()
    cap.release()
    cv2.destroyAllWindows()
