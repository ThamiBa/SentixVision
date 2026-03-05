import cv2
import os
import time
import numpy as np
from backend.core.state_manager import get_shared_state

# Set a global 5-second timeout for all FFMPEG-based network captures.
# Must be set BEFORE any cv2.VideoCapture is created.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;5000000"

class FrameCapture:
    def __init__(self, source):
        self.source = source.strip() if source else ""
        self.cap = None
        self.retries = 0
        self.max_retries = 2
        self.is_dummy = not self.source or self.source.upper() == "DUMMY"
        if not self.is_dummy:
            self._connect()

    def _connect(self):
        if not self.source or self.is_dummy:
            return
        try:
            print(f"[CoutureCam] Connecting to: {self.source}")
            mgr = get_shared_state()
            mgr.system_status = f"Connecting to {self.source}..."
            src = int(self.source) if str(self.source).isdigit() else self.source
            
            # FORCE TCP for RTSP (crucial for stability/IP cameras)
            if isinstance(src, str) and src.startswith("rtsp"):
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;5000000"
                cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
            else:
                cap = cv2.VideoCapture(src)
            
            if cap.isOpened():
                # Verify we can actually read a frame (streams can be fake-open)
                for attempt in range(15):
                    ret, frame = cap.read()
                    if ret and frame is not None and frame.size > 0:
                        self.cap = cap
                        self.retries = 0
                        print(f"[CoutureCam] Connected (Frame verified on attempt {attempt+1}).")
                        return
                    time.sleep(0.3)
                
                cap.release()
                get_shared_state().system_status = "Connection timeout: No data"
                print(f"[CoutureCam] Connection timeout: No data received from {self.source}")
            else:
                get_shared_state().system_status = "Source unreachable"
                print(f"[CoutureCam] Source unreachable: {self.source}")
        except Exception as e:
            get_shared_state().system_status = f"Connection Error: {str(e)}"
            print(f"[CoutureCam] Connection Error: {e}")
        self.cap = None

    def get_frame(self):
        if self.is_dummy:
            return self._generate_dummy_frame()

        if self.cap is None or not self.cap.isOpened():
            if self.retries < self.max_retries:
                self.retries += 1
                self._connect()
                return None
            # Max retries reached — fall permanently to dummy
            self.is_dummy = True
            get_shared_state().system_status = "Fallback to DEMO Mode"
            return self._generate_dummy_frame()

        ret, frame = self.cap.read()
        if not ret:
            print(f"[CoutureCam] Stream lost.")
            self.cap.release()
            self.cap = None
            return None
        return frame

    def _generate_dummy_frame(self):
        """Generates a synthetic artisan workshop frame for testing."""
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        frame[:] = (17, 20, 18)

        cv2.putText(frame, "SIMULATED ATELIER FEED", (430, 340),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "NO CAMERA DETECTED  |  TYPE A SOURCE & CLICK INITIATE",
                    (300, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1, cv2.LINE_AA)

        # Moving simulated artisan for tracking tests
        t = time.time()
        x = int(600 + 200 * np.sin(t))
        y = int(280 + 100 * np.cos(t * 0.8))
        cv2.rectangle(frame, (x, y), (x + 80, y + 140), (212, 175, 55), 1)
        cv2.putText(frame, "ARTISAN #1", (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (212, 175, 55), 1)

        return frame
