"""
app.py — Maison Sentix | Main Streamlit Orchestrator
Routes pages, manages session state, starts AI thread.
"""

import streamlit as st
import threading
import time
import pandas as pd
import textwrap
import requests
import os
from datetime import datetime

# SaaS Backend Config
BACKEND_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Frontend ──────────────────────────────────────────────────
from frontend.layout import init_page, page_content_wrapper, close_page_content
from frontend.components import inject_global_css
from frontend.dashboard import (
    render_dashboard, render_dashboard_sidebar,
    render_dashboard_live, render_dashboard_charts
)
from backend.services.mjpeg_server import get_stream_html
from frontend.zone_designer import (
    render_camera_list, render_new_camera_modal
)
from frontend.admin_equipment import render_equipment_page
from frontend.training_markup import render_training_page

# ── Backend (import guard — graceful if not installed yet) ────
try:
    from backend.core.ai_engine import start_ai_thread, stop_ai_thread
    from backend.core.state_manager import get_shared_state, reset_state
    from backend.core.database import init_db, get_equipment_df
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════

def init_session_state():
    """Initialize all session state keys with safe defaults."""
    defaults = {
        # ── System ──────────────────────────────────────────────
        "run_system":         False,
        "ai_thread":          None,
        "frame_lock":         threading.Lock(),

        # ── Shared state (written by AI thread, read by UI) ─────
        "shared_state": {
            "frame":          None,
            "fps":            0.0,
            "live_count":     0,
            "worker_count":   0,
            "client_count":   0,
            "angry_count":    0,
            "unknown_count":  0,
            "mood_score":     50.0,
            "team_happiness": 0.0,
            "emotion_data":   {"happy": 0, "neutral": 0, "angry": 0, "sad": 0},
            "camera_url":     "0",
            "backend_is_active": False,
            "fps":            0.0,
            "system_status":  "Initializing...",
        },

        # ── Analytics ────────────────────────────────────────────
        "df_analytics": pd.DataFrame(columns=[
            "timestamp", "worker_count", "client_count",
            "total_count", "happy_pct", "angry_pct",
            "neutral_pct", "mood_score", "avg_happiness",
        ]),

        # ── Worker of Day ────────────────────────────────────────
        "worker_happiness":   {},
        "emotion_cache":      {},
        "session_start":      datetime.now(),

        # ── Equipment ─────────────────────────────────────────────
        "equipment_df":       None,
        "selected_equipment": None,

        # ── Camera / Zone Designer ────────────────────────────────
        "cameras":            _default_cameras(),
        "selected_camera":    None,
        "zone_config":        {},
        "show_new_camera_modal": False,
        "show_new_equipment_modal": False,

        # ── Training & Markup ─────────────────────────────────────
        "tm_sections":        [
            {"id": 0, "name": "Machining 1", "status": "green",  "has_img": True},
            {"id": 1, "name": "Machining 2", "status": "yellow", "has_img": True},
            {"id": 2, "name": "Machining 3", "status": "red",    "has_img": True},
        ],
        "tm_active_section":  1,
        "tm_annotations":     [],
        "tm_show_annotations":True,

        # ── UI ────────────────────────────────────────────────────
        "eq_page":            1,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _default_cameras():
    return [
        {"id": i+1, "name": f"Camera {i+1}", "url": "0",
         "location": f"Zone {chr(65+i)}",
         "tracker": "ByteTrack", "zone_count": 2,
         "status": "active", "humans": {}}
        for i in range(5)
    ]


# ═══════════════════════════════════════════════════════════════
# AI THREAD CONTROL
# ═══════════════════════════════════════════════════════════════

def handle_start_stop(controls: dict):
    """Handle START / STOP / RESET actions from sidebar via SaaS API."""
    if controls.get("start") and not st.session_state["run_system"]:
        st.session_state["run_system"]    = True
        st.session_state["session_start"] = datetime.now()
        st.session_state["mjpeg_rendered"] = False 

        # Forward command to SaaS Backend
        try:
            config = {
                "url": controls["camera_url"],
                "conf": controls["conf_threshold"],
                "model": controls["yolo_model"]
            }
            requests.post(f"{BACKEND_URL}/cameras/1/start", json=config, timeout=5)
            st.session_state["mjpeg_rendered"] = False
            st.toast("🚀 AI Compute Started on Backend", icon="✅")
        except Exception as e:
            st.error(f"Backend Offline: {e}")

    if controls.get("stop") and st.session_state["run_system"]:
        st.session_state["run_system"] = False
        try:
            requests.post(f"{BACKEND_URL}/cameras/1/stop", timeout=5)
            st.session_state["mjpeg_rendered"] = False
            st.toast("🛑 AI Compute Stopped", icon="⏹️")
        except:
            pass

    if controls.get("reset"):
        st.session_state["df_analytics"] = pd.DataFrame(columns=[
            "timestamp", "worker_count", "client_count",
            "total_count", "happy_pct", "angry_pct",
            "neutral_pct", "mood_score", "avg_happiness",
        ])
        st.session_state["worker_happiness"] = {}
        st.session_state["emotion_cache"]    = {}
        st.session_state["session_start"]    = datetime.now()


def _start_mock_ai_thread(controls: dict):
    """Demo mode — generates synthetic metrics when AI libs unavailable."""
    import random, math

    def mock_loop():
        import numpy as np
        import cv2
        frame_n = 0
        while st.session_state.get("run_system", False):
            t = frame_n / 30
            state = st.session_state["shared_state"]
            state["fps"]            = 24 + random.uniform(-2, 2)
            state["live_count"]     = max(0, int(8 + 3*math.sin(t/5)))
            state["worker_count"]   = max(0, int(3 + math.sin(t/8)))
            state["client_count"]   = max(0, state["live_count"] - state["worker_count"])
            state["angry_count"]    = 1 if frame_n % 120 == 0 else 0
            state["mood_score"]     = max(0, min(100, 60 + 15*math.sin(t/12)))
            state["team_happiness"] = max(0, min(100, 55 + 20*math.sin(t/10)))
            state["emotion_data"]   = {
                "happy":   max(0, int(40 + 15*math.sin(t/7))),
                "neutral": 35,
                "angry":   max(0, int(10 + 5*math.cos(t/5))),
                "sad":     max(0, 15 - int(5*math.sin(t/9))),
            }
            
            # Create a mock frame (dark grey with moving circle)
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            img[:] = [15, 23, 42] # var(--bg-surface) approx
            cv2.putText(img, f"SENTIX LIVE FEED - CAM {st.session_state['shared_state'].get('camera_url','0')}", 
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (45, 212, 191), 2)
            cv2.putText(img, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (138, 155, 194), 1)
            
            # Moving object
            cx = int(320 + 200 * math.sin(t))
            cy = int(240 + 100 * math.cos(t*1.5))
            cv2.circle(img, (cx, cy), 30, (45, 212, 191), -1)
            cv2.putText(img, "HUMAN", (cx-20, cy+50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
            
            state["frame"] = img
            
            # PRO: Sync with global manager for MJPEG server support in demo mode
            mgr = get_shared_state()
            mgr.latest_frame = img
            
            # Ensure MJPEG server is running for demo mode too
            from backend.services.mjpeg_server import start_mjpeg_server
            start_mjpeg_server(mgr)
            
            frame_n += 1
            time.sleep(0.033)

    thread = threading.Thread(target=mock_loop, daemon=True)
    from streamlit.runtime.scriptrunner import add_script_run_ctx
    add_script_run_ctx(thread)
    thread.start()
    st.session_state["ai_thread"] = thread


# ═══════════════════════════════════════════════════════════════
# ANALYTICS RECORDER
# ═══════════════════════════════════════════════════════════════

_last_record_time = [0.0]
RECORD_INTERVAL   = 2.0  # seconds

def record_analytics():
    """Append a row to df_analytics every RECORD_INTERVAL seconds."""
    now = time.time()
    if now - _last_record_time[0] < RECORD_INTERVAL:
        return
    _last_record_time[0] = now

    state = st.session_state.get("shared_state", {})
    emotion = state.get("emotion_data", {})
    total = max(1, sum(emotion.values()))

    happy_pct   = emotion.get("happy",   0) / total * 100
    angry_pct   = emotion.get("angry",   0) / total * 100
    neutral_pct = emotion.get("neutral", 0) / total * 100
    mood_score  = max(0, min(100, 50 + happy_pct - angry_pct * 2))

    new_row = {
        "timestamp":    datetime.now(),
        "worker_count": state.get("worker_count", 0),
        "client_count": state.get("client_count", 0),
        "total_count":  state.get("live_count",   0),
        "happy_pct":    round(happy_pct,   1),
        "angry_pct":    round(angry_pct,   1),
        "neutral_pct":  round(neutral_pct, 1),
        "mood_score":   round(mood_score,  1),
        "avg_happiness":round(happy_pct / 100, 3),
    }

    df = st.session_state["df_analytics"]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state["df_analytics"] = df.tail(1000)  # bound memory


# ═══════════════════════════════════════════════════════════════
# STATE SYNCHRONIZER
# ═══════════════════════════════════════════════════════════════

def sync_backend_state():
    """Bridges the SaaS Backend API with Streamlit session_state."""
    if not st.session_state["run_system"]:
        return

    try:
        # Fetch latest metrics from SaaS Backend
        # Short timeout to prevent blocking the UI thread
        resp = requests.get(f"{BACKEND_URL}/analytics/realtime", timeout=0.5)
        if resp.status_code == 200:
            data = resp.json()
            ss = st.session_state.get("shared_state", {})
            if ss:
                ss["live_count"]     = data.get("live_count", 0)
                ss["worker_count"]   = data.get("worker_count", 0)
                ss["client_count"]   = data.get("client_count", 0)
                ss["mood_score"]     = data.get("mood_score", 50)
                ss["emotion_data"]   = data.get("emotion_data", {})
                ss["backend_is_active"] = data.get("is_active", False)
                ss["fps"]            = float(data.get("fps", 0.0))
                ss["system_status"]  = str(data.get("status", "Unknown") or "Unknown")
    except Exception as e:
        # Silently fail and keep previous state during transient network drops
        pass
    # ss["fps"] is not yet provided by mgr.avg_fps specifically but good for future


# ═══════════════════════════════════════════════════════════════
# METRICS BUILDER
# ═══════════════════════════════════════════════════════════════

def build_metrics() -> dict:
    """Assemble the metrics dict for dashboard rendering from shared_state."""
    state = st.session_state.get("shared_state", {})

    # Worker of the Day
    wh = st.session_state.get("worker_happiness", {})
    wotd_id    = max(wh, key=wh.get) if wh else "—"
    wotd_score = wh.get(wotd_id, 0)

    # Avg wait time
    elapsed = (datetime.now() - st.session_state.get("session_start", datetime.now())).seconds
    total   = max(1, state.get("live_count", 1))

    return {
        "live_count":        state.get("live_count",      0),
        "worker_count":      state.get("worker_count",    0),
        "client_count":      state.get("client_count",    0),
        "angry_count":       state.get("angry_count",     0),
        "unknown_count":     state.get("unknown_count",   0),
        "mood_score":        state.get("mood_score",      50),
        "team_happiness":    state.get("team_happiness",  0),
        "fps":               state.get("fps",             0),
        "camera_url":        state.get("camera_url",     "—"),
        "emotion_data":      state.get("emotion_data",   {}),
        "worker_of_day":     wotd_id,
        "worker_of_day_score": wotd_score,
        "avg_wait_sec":      elapsed // total,
        "live_count_delta":  None,
        "happiness_delta":   None,
        "system_status":     str(state.get("system_status", "Connecting...") or "Connecting..."),
    }


# ═══════════════════════════════════════════════════════════════
# PAGE RENDERERS
# ═══════════════════════════════════════════════════════════════

def page_dashboard():
    """Live dashboard page."""
    controls = render_dashboard_sidebar()
    handle_start_stop(controls)

    page_content_wrapper()

    # ── STABLE LAYOUT SLOTS (Created once per full page load) ────────────
    # Each small UI element has its own st.empty() slot to prevent Protobuf crashes.
    
    # KPI Row 1
    k_cols = st.columns(4, gap="small")
    slot_k1, slot_k2, slot_k3, slot_k4 = [k_cols[i].empty() for i in range(4)]
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    
    # KPI Row 2
    sk_cols = st.columns(4, gap="small")
    slot_sk1, slot_sk2, slot_sk3, slot_sk4 = [sk_cols[i].empty() for i in range(4)]
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    
    # Alerts
    slot_alert = st.empty()
    
    # Video + Stats
    v_col, s_col = st.columns([3, 1], gap="small")
    with v_col:
        slot_vid_header = st.empty()
        slot_vid_frame  = st.empty()
    with s_col:
        slot_stats = st.empty()
        
    # Charts
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c_cols = st.columns([2, 1], gap="small")
    slot_chart1, slot_chart2 = [c_cols[i].empty() for i in range(2)]

    slots = {
        "kpis":   [slot_k1, slot_k2, slot_k3, slot_k4],
        "sec_k":  [slot_sk1, slot_sk2, slot_sk3, slot_sk4],
        "alert":  slot_alert,
        "header": slot_vid_header,
        "video":  slot_vid_frame,
        "stats":  slot_stats,
        "charts": [slot_chart1, slot_chart2],
    }

    render_live_components(slots)
    render_analytics_charts_fragment(slots)

    close_page_content()


@st.fragment(run_every="1000ms")
def render_live_components(slts):
    # 0. Sync from backend
    sync_backend_state()
    
    state = st.session_state.get("shared_state", {})
    metrics = build_metrics()
    
    if st.session_state.get("run_system"):
        record_analytics()

    # Render KPI/Alerts and Video into specific slots
    render_dashboard_live(metrics=metrics, slots=slts)

@st.fragment(run_every="3s")
def render_analytics_charts_fragment(slts):
    render_dashboard_charts(df_analytics=st.session_state["df_analytics"], slots=slts)

    # Fragments handle the refreshing now


def page_environment():
    """Environment Designer page."""
    page_content_wrapper()
    cameras = st.session_state.get("cameras", _default_cameras())
    render_camera_list(cameras)
    render_new_camera_modal()
    close_page_content()


def page_training():
    """Training & Markup page."""
    page_content_wrapper()
    render_training_page()
    close_page_content()


def page_admin_equipment():
    """Administration → Equipment page."""
    page_content_wrapper()
    render_equipment_page()
    close_page_content()


# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════

PAGE_MAP = {
    "dashboard":   page_dashboard,
    "environment": page_environment,
    "training":    page_training,
    "admin":       page_admin_equipment,
    "alerts":      lambda: st.info("Alerts page — coming soon"),
    "reporting":   lambda: st.info("Reporting page — coming soon"),
}


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    init_session_state()
    active_page = init_page("Dashboard")

    # Route to correct page
    renderer = PAGE_MAP.get(active_page, page_dashboard)
    renderer()


if __name__ == "__main__":
    main()