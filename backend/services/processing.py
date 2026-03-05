import cv2
import time
import numpy as np
from backend.core.ai_engine import AIEngine

# ── Haar cascade for face detection ──────────────────────────────────────────
_face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# ── MediaPipe Hands (Tasks API) ─────────────────────────────────────────────
_MODEL_PATH = "data/hand_landmarker.task"
try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    
    _base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
    _hand_options = mp_vision.HandLandmarkerOptions(
        base_options=_base_options,
        running_mode=mp_vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    _HAND_LANDMARKER = mp_vision.HandLandmarker.create_from_options(_hand_options)
    _MEDIAPIPE_OK = True
    print("[Processor] MediaPipe HandLandmarker ready.")
except Exception as _mp_err:
    _MEDIAPIPE_OK = False
    _HAND_LANDMARKER = None
    print(f"[Processor] MediaPipe status: {type(_mp_err).__name__} - check if model exists at {_MODEL_PATH}")

# Zone colours (BGR)
ZONE_FACE_COLOR  = (55,  175, 212)   # Teal  — Zone 1: Face
ZONE_HAND_COLOR  = (55,  212, 130)   # Mint  — Zone 2: Object in hand
ZONE_TRACK_COLOR = (212, 175,  55)   # Gold  — Tracked person body


class CoutureProcessor:
    def __init__(self, state_manager):
        self.mgr = state_manager
        self.ai  = AIEngine()
        self.frame_count = 0

    # ── Main Loop ─────────────────────────────────────────────────────────────
    def run_loop(self, stop_event=None):
        print("[Processor] Started.")
        while True:
            # Check if thread should terminate
            if stop_event and stop_event.is_set():
                print("[Processor] Terminating gracefully.")
                break

            if not self.mgr.run:
                time.sleep(0.1)
                continue

            # Clear older frames if queue is backing up to prevent lag
            if self.mgr.frame_queue.qsize() > 1:
                while self.mgr.frame_queue.qsize() > 1:
                    try:
                        self.mgr.frame_queue.get_nowait()
                    except:
                        break

            if self.mgr.frame_queue.empty():
                time.sleep(0.01)
                continue

            raw_frame = self.mgr.frame_queue.get()
            if raw_frame is None:
                continue

            if self.frame_count % 30 == 0:
                print(f"[Processor] Processing frame {self.frame_count}. Queued: {self.mgr.frame_queue.qsize()}")

            self.frame_count += 1
            self.mgr.update_fps()

            # 1. Person tracking
            frame, detections = self.ai.track_objects(raw_frame.copy())

            # 2. Zone assignment on tracked persons
            current_metrics = {}
            for d in detections:
                center = d['center']
                assigned_zone = "None"
                for z_name, poly in self.mgr.zones.items():
                    if cv2.pointPolygonTest(poly, center, False) >= 0:
                        assigned_zone = z_name
                        break
                d['zone'] = assigned_zone

                if self.frame_count % 10 == 0 and assigned_zone != "None":
                    d['emotion'] = self.ai.analyze_emotion(frame, d['bbox'])

                if assigned_zone != "None":
                    tid = d['id']
                    current_metrics[tid] = {'time': 1, 'positive': 0}
                    if d.get('emotion') in ['happy', 'surprise']:
                        current_metrics[tid]['positive'] = 1

            # 3. Privacy: face blur
            if getattr(self.mgr, 'privacy_mode', False):
                for d in detections:
                    x1, y1, x2, y2 = d['bbox']
                    roi = frame[y1:y2, x1:x2]
                    if roi.size > 0:
                        frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (99, 99), 30)

            # 4. Zone 1 — Face detection (Haar cascade)
            faces = self._detect_faces(frame)

            # 5. Zone 2 — Precise hand + held-object bounding box (MediaPipe)
            hand_boxes = self._detect_hand_objects(frame)

            # 6. Draw everything
            annotated = self._draw_overlay(frame, detections, faces, hand_boxes)

            # 7. Push annotated frame to MJPEG stream
            self.mgr.latest_frame = annotated

            # 8. Push AI result for metrics (non-blocking, always fresh)
            while not self.mgr.result_queue.empty():
                try:
                    self.mgr.result_queue.get_nowait()
                except Exception:
                    break
            try:
                self.mgr.result_queue.put_nowait({'frame': annotated, 'metrics': current_metrics})
            except Exception:
                pass

            # 9. Update Aggregate State (Sync for UI)
            self._update_manager_metrics(detections)

    def _update_manager_metrics(self, detections):
        """Calculates and stores aggregate counts in the manager singleton."""
        live_count = len(detections)
        worker_count = sum(1 for d in detections if d['zone'] == 'Cutting Table' or d['zone'] == 'Sewing Station')
        client_count = live_count - worker_count
        
        # Simple emotion aggregation
        emotions = {"happy": 0, "neutral": 0, "angry": 0, "sad": 0}
        for d in detections:
            e = d.get('emotion', 'neutral')
            if e in emotions: emotions[e] += 1
            elif e in ['surprise', 'happy']: emotions['happy'] += 1
            elif e in ['fear', 'angry']: emotions['angry'] += 1
            elif e in ['sad', 'disgust']: emotions['sad'] += 1
            else: emotions['neutral'] += 1

        total_e = max(1, sum(emotions.values()))
        mood = max(0, min(100, 50 + (emotions['happy'] - emotions['angry']*2) / total_e * 50))

        self.mgr.live_count = live_count
        self.mgr.worker_count = worker_count
        self.mgr.client_count = client_count
        self.mgr.emotion_data = emotions
        self.mgr.mood_score = mood

    # ── Zone 1: Face Detection ────────────────────────────────────────────────
    def _detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = _face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(40, 40), flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces if len(faces) > 0 else []

    # ── Zone 2: Hand + Object Detection ──────────────────────────────────────
    def _detect_hand_objects(self, frame):
        """
        Uses MediaPipe HandLandmarker (Tasks API, mediapipe >= 0.10) to get
        21 precise landmarks per hand. The bounding box wraps the hand tightly
        and extends 30px sideways + 60px downward to encompass the held object.
        """
        h, w = frame.shape[:2]
        boxes = []

        if not _MEDIAPIPE_OK or _HAND_LANDMARKER is None:
            return boxes

        try:
            # MediaPipe Tasks expects an mp.Image object
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )
            result = _HAND_LANDMARKER.detect(mp_image)

            for hand_landmarks in result.hand_landmarks:
                xs = [int(lm.x * w) for lm in hand_landmarks]
                ys = [int(lm.y * h) for lm in hand_landmarks]

                x1, y1 = max(0, min(xs)), max(0, min(ys))
                x2, y2 = min(w, max(xs)), min(h, max(ys))

                # Expand: 30px sides, 60px below to include held object
                x1 = max(0, x1 - 30)
                y1 = max(0, y1 - 30)
                x2 = min(w, x2 + 30)
                y2 = min(h, y2 + 60)

                boxes.append((x1, y1, x2, y2))

        except Exception as e:
            pass  # Silently skip bad frames

        return boxes

    # ── Overlay Drawing ───────────────────────────────────────────────────────
    def _draw_overlay(self, frame, detections, faces, hand_boxes):
        h, w = frame.shape[:2]

        # Work zones (user-defined polygons)
        for z_name, poly in self.mgr.zones.items():
            cv2.polylines(frame, [poly], True, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.putText(frame, z_name.upper(),
                        (poly[0][0], poly[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

        # Zone 1 — Face boxes
        for (fx, fy, fw, fh) in faces:
            _draw_corners(frame, fx, fy, fx + fw, fy + fh, ZONE_FACE_COLOR, length=14)
            cv2.putText(frame, "ZONE 1 | FACE",
                        (fx, fy - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, ZONE_FACE_COLOR, 1, cv2.LINE_AA)

        # Zone 2 — Hand + object boxes (MediaPipe-derived, resizes to actual object)
        for idx, (hx1, hy1, hx2, hy2) in enumerate(hand_boxes):
            # Filled translucent overlay so the zone is clearly visible
            overlay = frame.copy()
            cv2.rectangle(overlay, (hx1, hy1), (hx2, hy2), ZONE_HAND_COLOR, -1)
            cv2.addWeighted(overlay, 0.08, frame, 0.92, 0, frame)
            # Border
            cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), ZONE_HAND_COLOR, 1, cv2.LINE_AA)
            _draw_corners(frame, hx1, hy1, hx2, hy2, ZONE_HAND_COLOR, length=12)
            cv2.putText(frame, f"ZONE 2 | HAND #{idx+1}",
                        (hx1, hy1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, ZONE_HAND_COLOR, 1, cv2.LINE_AA)

        # Tracked person bodies
        for d in detections:
            x1, y1, x2, y2 = d['bbox']
            color = ZONE_TRACK_COLOR if d['zone'] != "None" else (180, 180, 180)
            _draw_corners(frame, x1, y1, x2, y2, color, length=16)
            label = f"ARTISAN #{d['id']}"
            if d.get('zone') and d['zone'] != "None":
                label += f" | {d['zone'][:8].upper()}"
            if d.get('emotion'):
                label += f" | {d['emotion'].upper()}"
            cv2.putText(frame, label, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

        # HUD
        cv2.putText(frame,
                    f"FACES: {len(faces)}  |  HANDS: {len(hand_boxes)}",
                    (10, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (160, 160, 160), 1, cv2.LINE_AA)

        return frame


# ── Corner-bracket helper ─────────────────────────────────────────────────────
def _draw_corners(frame, x1, y1, x2, y2, color, length=15, thickness=1):
    for corner, h_pt, v_pt in [
        ((x1, y1), (x1 + length, y1), (x1, y1 + length)),
        ((x2, y1), (x2 - length, y1), (x2, y1 + length)),
        ((x1, y2), (x1 + length, y2), (x1, y2 - length)),
        ((x2, y2), (x2 - length, y2), (x2, y2 - length)),
    ]:
        cv2.line(frame, corner, h_pt, color, thickness, cv2.LINE_AA)
        cv2.line(frame, corner, v_pt, color, thickness, cv2.LINE_AA)