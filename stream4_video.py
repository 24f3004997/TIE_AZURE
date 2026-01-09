# import cv2
# import numpy as np

# # --- SAFETY BLOCK: Handle Broken MediaPipe on Python 3.12 ---
# try:
#     import mediapipe as mp
#     mp_available = True
#     print("✅ MediaPipe Library Loaded Successfully.")
# except ImportError:
#     mp_available = False
#     print("⚠️ MediaPipe Library NOT found. Using Backup Mode.")
# except AttributeError:
#     mp_available = False
#     print("⚠️ MediaPipe Incompatible (Python 3.12 Error). Using Backup Mode.")

# class VideoEngine:
#     def __init__(self):
#         self.active = False
#         if mp_available:
#             try:
#                 # Attempt to initialize solutions
#                 self.mp_face = mp.solutions.face_mesh.FaceMesh(max_num_faces=1)
#                 self.mp_pose = mp.solutions.pose.Pose()
#                 self.active = True
#                 print("👁️ Vision AI Engine: ONLINE")
#             except AttributeError:
#                 print("⚠️ Vision AI Engine: OFFLINE (Library Error).")
#                 self.active = False
#         else:
#             print("⚠️ Vision AI Engine: OFFLINE (Missing Library).")

#     def analyze(self, video_path):
#         # 1. If AI is broken, return "Safe" Mock Data (Prevent Crash)
#         if not self.active:
#             print("⚠️ Skipping detailed vision analysis (Using Fallback Data)")
#             return {
#                 "eye_contact_score": 75,   # Default "Good" score
#                 "gesture_energy_score": 60 # Default "Active" score
#             }

#         # 2. If AI works, run the real analysis
#         cap = cv2.VideoCapture(video_path)
#         frames_analyzed = 0
#         eye_contact = 0
#         energy_list = []
#         prev_y = None
        
#         while cap.isOpened():
#             success, img = cap.read()
#             if not success: break
            
#             frames_analyzed += 1
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             img.flags.writeable = False
            
#             # Face
#             try:
#                 res = self.mp_face.process(img)
#                 if res.multi_face_landmarks:
#                     lm = res.multi_face_landmarks[0].landmark
#                     if lm[133].x < lm[4].x < lm[362].x:
#                         eye_contact += 1
#             except: pass
            
#             # Body
#             try:
#                 res_pose = self.mp_pose.process(img)
#                 if res_pose.pose_landmarks:
#                     y = res_pose.pose_landmarks.landmark[15].y
#                     if prev_y: energy_list.append(abs(y - prev_y))
#                     prev_y = y
#             except: pass
                
#         cap.release()
        
#         score_eye = int((eye_contact / frames_analyzed * 100)) if frames_analyzed else 0
#         score_energy = int(min(sum(energy_list) * 500, 100)) if energy_list else 0
        
#         return {
#             "eye_contact_score": score_eye,
#             "gesture_energy_score": score_energy
#         }






# import cv2
# import numpy as np
# import time

# # --- SAFETY BLOCK: Handle MediaPipe Imports ---
# try:
#     import mediapipe as mp
#     mp_available = True
#     print("✅ MediaPipe Library Loaded Successfully.")
# except ImportError:
#     mp_available = False
#     print("⚠️ MediaPipe Library NOT found. Using Backup Mode.")
# except AttributeError:
#     mp_available = False
#     print("⚠️ MediaPipe Incompatible (Python 3.12 Error). Using Backup Mode.")

# class VideoEngine:
#     def __init__(self):
#         self.active = False
#         if mp_available:
#             try:
#                 # Initialize Face Mesh (High accuracy for eyes/head)
#                 self.mp_face_mesh = mp.solutions.face_mesh
#                 self.face_mesh = self.mp_face_mesh.FaceMesh(
#                     min_detection_confidence=0.5, 
#                     min_tracking_confidence=0.5,
#                     max_num_faces=1
#                 )
#                 self.active = True
#                 print("👁️ Vision AI Engine: ONLINE (Distraction Tracking Enabled)")
#             except AttributeError:
#                 print("⚠️ Vision AI Engine: OFFLINE (Library Error).")
#                 self.active = False
#         else:
#             print("⚠️ Vision AI Engine: OFFLINE (Missing Library).")

#     def analyze(self, video_path):
#         # 1. FAILSAFE: If AI is broken, return safe mock data
#         if not self.active:
#             print("⚠️ Skipping detailed vision analysis (Using Fallback Data)")
#             return {
#                 "eye_contact_score": 75,
#                 "gesture_energy_score": 60,
#                 "distraction_events": 2 # Mock data for demo
#             }

#         # 2. REAL ANALYSIS
#         cap = cv2.VideoCapture(str(video_path))
        
#         # Metrics Counters
#         total_frames = 0
#         looking_at_camera_frames = 0
#         movement_energy = 0
#         prev_nose_coords = None
        
#         # Distraction Logic Variables
#         distraction_events = 0
#         consecutive_look_away_frames = 0
#         fps = cap.get(cv2.CAP_PROP_FPS) or 30
#         # Threshold: 1.5 seconds of looking away counts as 1 "Distraction Event"
#         frames_for_distraction = int(fps * 1.5) 

#         while cap.isOpened():
#             success, image = cap.read()
#             if not success:
#                 break

#             total_frames += 1
#             image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#             image_rgb.flags.writeable = False
            
#             # Process Face Mesh
#             results = self.face_mesh.process(image_rgb)
            
#             height, width, _ = image.shape
#             current_nose_coords = None

#             if results.multi_face_landmarks:
#                 landmarks = results.multi_face_landmarks[0].landmark
                
#                 # Metric 1: Gesture Energy (Head Movement)
#                 nose = landmarks[1] # Tip of nose
#                 current_nose_coords = np.array([nose.x * width, nose.y * height])

#                 if prev_nose_coords is not None:
#                     dist = np.linalg.norm(current_nose_coords - prev_nose_coords)
#                     movement_energy += dist
#                 prev_nose_coords = current_nose_coords

#                 # Metric 2 & 3: Eye Contact & Distraction
#                 # Logic: If nose is in the center 40% of the screen, they are looking at camera/class
#                 # (Simple, robust heuristic for competitions)
#                 is_looking_center = (0.3 < nose.x < 0.7) and (0.3 < nose.y < 0.7)

#                 if is_looking_center:
#                     looking_at_camera_frames += 1
#                     consecutive_look_away_frames = 0 # Reset distraction counter
#                 else:
#                     consecutive_look_away_frames += 1
                    
#                     # If they look away for too long continuously...
#                     if consecutive_look_away_frames == frames_for_distraction:
#                         distraction_events += 1
#                         # We don't reset immediately so we don't count the same long look-away twice
#                         # But you could reset here if you want to count every 1.5s block.

#         cap.release()

#         # 3. Calculate Final Scores (0-100 Scale)
#         eye_contact_score = int((looking_at_camera_frames / total_frames) * 100) if total_frames > 0 else 0
        
#         # Normalize energy (experimental multiplier based on typical movement)
#         gesture_score = min(100, int(movement_energy / total_frames * 20)) if total_frames > 0 else 0
        
#         print(f"✅ Video Analysis Done: {distraction_events} distractions detected.")

#         return {
#             "eye_contact_score": eye_contact_score,
#             "gesture_energy_score": gesture_score,
#             "distraction_events": distraction_events # <--- Critical for Imagine Cup feature
#         }




import cv2
import numpy as np
import time

# --- CONFIGURATION ---
# We use OpenCV's built-in face detector (No MediaPipe needed!)
# This ensures your project works even if MediaPipe is broken.
class VideoEngine:
    def __init__(self):
        # Load the pre-trained face detector inside OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.active = True
        print("👁️ Universal Vision Engine: ONLINE (Using OpenCV Native)")

    def analyze(self, video_path):
        cap = cv2.VideoCapture(str(video_path))
        
        # Metrics Counters
        total_frames = 0
        looking_at_camera_frames = 0
        movement_energy = 0
        prev_center = None
        
        # Distraction Logic
        distraction_events = 0
        consecutive_look_away_frames = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frames_for_distraction = int(fps * 1.5) # 1.5 seconds threshold

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            total_frames += 1
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect Faces (This is the "Haar Cascade" method)
            # scaleFactor=1.1, minNeighbors=5 are standard settings
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) > 0:
                # Face Detected! 
                # We assume if the camera sees a face, they are looking at the audience.
                (x, y, w, h) = faces[0] # Get coordinates of the first face
                
                # 1. Update Eye Contact Counter
                looking_at_camera_frames += 1
                consecutive_look_away_frames = 0 # Reset distraction
                
                # 2. Update Gesture/Movement Energy
                current_center = np.array([x + w//2, y + h//2])
                if prev_center is not None:
                    dist = np.linalg.norm(current_center - prev_center)
                    movement_energy += dist
                prev_center = current_center
                
            else:
                # No Face Detected (Turned away or left frame) -> DISTRACTION
                consecutive_look_away_frames += 1
                
                # If they look away for 1.5 seconds...
                if consecutive_look_away_frames == frames_for_distraction:
                    distraction_events += 1

        cap.release()

        # Final Scores
        eye_contact_score = int((looking_at_camera_frames / total_frames) * 100) if total_frames > 0 else 0
        gesture_score = min(100, int(movement_energy / total_frames * 5)) if total_frames > 0 else 0
        
        print(f"✅ Analysis Complete (OpenCV Mode). Distractions: {distraction_events}")

        return {
            "eye_contact_score": eye_contact_score,
            "gesture_energy_score": gesture_score,
            "distraction_events": distraction_events 
        }