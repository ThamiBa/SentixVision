import threading
from typing import Dict
from backend.core.ai_engine import start_ai_thread, stop_ai_thread
from backend.core.state_manager import get_shared_state

class AICoordinator:
    """
    Manages multiple AI processing threads for different cameras.
    In a SaaS environment, this would scale across multiple workers.
    """
    def __init__(self):
        # camera_id -> thread object
        self.active_threads: Dict[int, threading.Thread] = {}
        # camera_id -> state manager instance (one per camera in multi-tenant)
        self.states: Dict[int, any] = {}

    def start_camera_processing(self, camera_id: int, camera_url: str, config: dict):
        if camera_id in self.active_threads and self.active_threads[camera_id].is_alive():
            print(f"[AICoordinator] Thread for Camera {camera_id} is already running.")
            return False
            
        print(f"[AICoordinator] Spawning background thread for Camera {camera_id}: {camera_url}")
        
        # We wrap start_ai_thread in another thread to ensure the API returns immediately
        # while the camera connection and model loading (which are slow) happen in background.
        thread = threading.Thread(
            target=start_ai_thread,
            args=(
                camera_url,
                config.get("conf", 0.4),
                config.get("model", "yolov8n.pt"),
                "DeepFace",
                10
            ),
            daemon=True
        )
        self.active_threads[camera_id] = thread
        thread.start()
        return True

    def stop_camera_processing(self, camera_id: int):
        print(f"[AICoordinator] Stopping AI for Camera {camera_id}")
        stop_ai_thread()
        if camera_id in self.active_threads:
            del self.active_threads[camera_id]
        return True

# Singleton coordinator
coordinator = AICoordinator()
