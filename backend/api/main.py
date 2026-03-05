from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from backend.api.auth import create_access_token, verify_password, get_password_hash
from backend.services.ai_coordinator import coordinator
from backend.core.state_manager import get_shared_state
from backend.database.init_db import init_db
from backend.services.mjpeg_server import start_mjpeg_server
import uvicorn
import asyncio

app = FastAPI(
    title="SentixVision SaaS API",
    description="Backend API for multi-cam vision analytics",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    # Ensure tables and initial data exist
    init_db()
    
    # Start MJPEG server early to avoid "Connection Lost" in UI
    mgr = get_shared_state()
    start_mjpeg_server(mgr)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SentixVision API is operational", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ── AUTHENTICATION ──────────────────────────────────────────────
@app.post("/auth/login")
async def login(credentials: dict):
    # This is a mock. In production, check against DB.
    if credentials["email"] == "admin@sentix.com" and credentials["password"] == "admin123":
        token = create_access_token(data={"sub": credentials["email"], "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    return {"error": "Invalid credentials"}

# ── CAMERA CONTROL ──────────────────────────────────────────────
@app.post("/cameras/{camera_id}/start")
async def start_camera(camera_id: int, config: dict):
    # In production, fetch URL from DB using camera_id
    mock_url = config.get("url", "0") 
    success = coordinator.start_camera_processing(camera_id, mock_url, config)
    return {"status": "started" if success else "already_running"}

@app.post("/cameras/{camera_id}/stop")
async def stop_camera(camera_id: int):
    coordinator.stop_camera_processing(camera_id)
    return {"status": "stopped"}

# ── ANALYTICS ───────────────────────────────────────────────────
@app.get("/analytics/realtime")
async def get_realtime_analytics():
    mgr = get_shared_state()
    return {
        "is_active": mgr.latest_frame is not None,
        "fps": mgr.avg_fps,
        "status": mgr.system_status,
        "live_count": mgr.live_count,
        "worker_count": mgr.worker_count,
        "client_count": mgr.client_count,
        "mood_score": mgr.mood_score,
        "emotion_data": mgr.emotion_data
    }

# ── WEBSOCKETS (RESOURCES) ──────────────────────────────────────
@app.websocket("/ws/analytics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            mgr = get_shared_state()
            await websocket.send_json({
                "type": "metric_update",
                "data": {
                    "live_count": mgr.live_count,
                    "worker_count": mgr.worker_count,
                    "mood": mgr.mood_score
                }
            })
            await asyncio.sleep(1)
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
