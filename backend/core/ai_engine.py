import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace

class AIEngine:
    def __init__(self):
        # PRO UPGRADE: Placeholder for High-Performance Inference Engines
        # Move to TensorRT (NVIDIA) or OpenVINO (Intel) for 30+ FPS in production
        self.engine_type = "Standard (CPU)" 
        self.yolo = YOLO("yolov8n.pt")
        # Define your zones here (Coordinates based on 1280x720 resolution)
        self.zones = {
            'Cutting Table': np.array([[50, 50], [600, 50], [600, 700], [50, 700]], np.int32),
            'Sewing Station': np.array([[650, 50], [1200, 50], [1200, 700], [650, 700]], np.int32)
        }

    def track_objects(self, frame):
        # 1. Resize for speed consistent with zone coordinates
        frame_small = cv2.resize(frame, (1280, 720))
        results = self.yolo.track(frame_small, persist=True, tracker="botsort.yaml", verbose=False)
        
        detections = []
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy()
            clss = results[0].boxes.cls.cpu().numpy()
            
            for box, track_id, cls in zip(boxes, ids, clss):
                # Filter ONLY for 'person' class (index 0 in COCO/YOLOv8)
                if int(cls) != 0:
                    continue
                    
                x1, y1, x2, y2 = map(int, box)
                # The "Center" point used to check if they are in a zone
                # Using the bottom-center (y2) is more accurate for floor-standing people
                center = (int((x1+x2)/2), int(y2)) 
                
                # 2. Check which zone the person is in
                assigned_zone = "None"
                for z_name, poly in self.zones.items():
                    # pointPolygonTest checks if 'center' is inside the 'poly'
                    if cv2.pointPolygonTest(poly, center, False) >= 0:
                        assigned_zone = z_name
                        break
                
                detections.append({
                    'id': int(track_id),
                    'bbox': (x1, y1, x2, y2),
                    'zone': assigned_zone,
                    'center': center
                })
        return frame_small, detections

    def analyze_emotion(self, frame, bbox):
        # ... (Your existing emotion code is fine) ...
        try:
            x1, y1, x2, y2 = bbox
            face_img = frame[max(0, y1):y2, max(0, x1):x2]
            if face_img.size == 0: return None
            obj = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False, silent=True)
            return obj[0]['dominant_emotion']
        except: return None


# ── GLUE FUNCTIONS FOR ORCHESTRATOR ───────────────────────────────────────────
import threading
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx
from backend.services.camera_mgr import FrameCapture
from backend.services.processing import CoutureProcessor
from backend.services.mjpeg_server import start_mjpeg_server
from backend.core.state_manager import get_shared_state

_STOP_EVENT = threading.Event()

def start_ai_thread(camera_url, conf_threshold, yolo_model, emotion_engine, emotion_skip):
    """
    Main entry point for the AI processing thread.
    Initializes capture, processor, and starts the loop.
    """
    global _STOP_EVENT
    _STOP_EVENT.clear()
    
    mgr = get_shared_state()
    capture = FrameCapture(camera_url)
    processor = CoutureProcessor(mgr)
    
    # Start MJPEG server for high-stability video display
    start_mjpeg_server(mgr)
    
    # ACTIVATE the processor loop
    mgr.run = True
    
    # Add script context to current thread to avoid "missing ScriptRunContext" warning
    add_script_run_ctx(threading.current_thread())
    
    # We need a way to feed frames from capture to processor via manager
    def pusher():
        while not _STOP_EVENT.is_set():
            frame = capture.get_frame()
            if frame is not None:
                mgr.frame_queue.put(frame)
            else:
                time.sleep(0.1) # Wait for reconnect
                
    push_thread = threading.Thread(target=pusher, daemon=True)
    add_script_run_ctx(push_thread)
    push_thread.start()
    
    processor.run_loop(stop_event=_STOP_EVENT)

def stop_ai_thread():
    """Signals the AI thread to terminate."""
    global _STOP_EVENT
    _STOP_EVENT.set()
    mgr = get_shared_state()
    mgr.run = False