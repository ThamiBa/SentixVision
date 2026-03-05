import cv2
import time
import queue
import numpy as np
import json
import os
from collections import defaultdict

class StateManager:
    """
    Holds state shared between Main Thread (UI) and Background Threads.
    """
    def __init__(self):
        self.run = False
        self.privacy_mode = False

        # latest_frame: always the most recent raw frame for zero-latency display.
        # The UI reads this directly instead of going through the AI result queue.
        self.latest_frame = None

        # Small queues — maxsize=2 ensures old frames never accumulate.
        self.frame_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue(maxsize=2)

        self.config_path = "data/config/zones.json"
        self.zones = self._load_zones()

        # Artisan Scores: {track_id: {time, positive, last_seen, role}}
        self.worker_scores = defaultdict(lambda: {
            'time': 0,
            'positive': 0,
            'last_seen': 0,
            'role': 'Apprentice'
        })
        self.source = "DUMMY"

        # ── Aggregate Metrics (Read by UI) ──────────────────────────
        self.live_count = 0
        self.worker_count = 0
        self.client_count = 0
        self.avg_fps = 0.0
        self.emotion_data = {"happy": 0, "neutral": 0, "angry": 0, "sad": 0}
        self.mood_score = 50.0
        self.system_status = "System initialized"
        self.last_frame_time = time.time()
        self.avg_fps = 0.0

    def update_fps(self):
        now = time.time()
        dt = now - self.last_frame_time
        if dt > 0:
            current_fps = 1.0 / dt
            # Exponential moving average for smoothness
            self.avg_fps = self.avg_fps * 0.9 + current_fps * 0.1
        self.last_frame_time = now


    def _load_zones(self):
        """Loads zones from JSON or returns defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    z_data = json.load(f)
                return {k: np.array(v, np.int32) for k, v in z_data.items()}
            except Exception as e:
                print(f"[StateManager] Error loading zones: {e}")
        
        # Default Couture Zones
        return {
            'Cutting Table': np.array([[50, 50], [600, 50], [600, 700], [50, 700]], np.int32),
            'Sewing Station': np.array([[650, 50], [1200, 50], [1200, 700], [650, 700]], np.int32)
        }
# ── GLUE FUNCTIONS FOR ORCHESTRATOR ───────────────────────────────────────────

_GLOBAL_STATE = None

def get_shared_state():
    """Returns (or initializes) the global StateManager instance."""
    global _GLOBAL_STATE
    if _GLOBAL_STATE is None:
        _GLOBAL_STATE = StateManager()
    return _GLOBAL_STATE

def reset_state():
    """Force re-initialization of the global state."""
    global _GLOBAL_STATE
    _GLOBAL_STATE = StateManager()
    return _GLOBAL_STATE
