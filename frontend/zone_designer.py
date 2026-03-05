"""
zone_designer.py — Environment Designer
Camera setup modal, zone polygon editor, line/queue config.
Mirrors the 'New Camera' modal in sentixvision3.webp.
"""

import streamlit as st
import textwrap
import numpy as np
import json
from frontend.components import (
    section_header, modal_shell, toggle_row,
    inline_label, PALETTE
)


# ═══════════════════════════════════════════════════════════════
# DEFAULT ZONE CONFIGS
# ═══════════════════════════════════════════════════════════════

DEFAULT_ZONES = {
    "worker_zone": {
        "name": "Worker Zone",
        "color": "#3B82F6",
        "points_rel": [[0.0, 0.0], [0.30, 0.0], [0.30, 1.0], [0.0, 1.0]],
        "enabled": True,
    },
    "client_zone": {
        "name": "Client Zone",
        "color": "#2DD4BF",
        "points_rel": [[0.35, 0.0], [1.0, 0.0], [1.0, 1.0], [0.35, 1.0]],
        "enabled": True,
    },
}

RECOGNITION_TABS = ["General", "Humans", "Objects", "Areas"]

TRACKER_OPTIONS = ["ByteTrack", "Boosting", "MIL", "KCF", "CSRT", "MOSSE"]


# ═══════════════════════════════════════════════════════════════
# CAMERA LIST PAGE
# ═══════════════════════════════════════════════════════════════

def render_camera_list(cameras: list):
    """
    Left panel: paginated list of configured cameras.
    cameras: list of dicts with keys: id, name, url, status, zone_count
    """
    section_header("Environment Designer", "Configure cameras, zones, and detection settings")

    with st.sidebar:
        _render_camera_sidebar_list(cameras)

    if st.session_state.get("selected_camera"):
        render_camera_detail(st.session_state["selected_camera"])
    else:
        _render_empty_detail()


def _render_camera_sidebar_list(cameras: list):
    """Scrollable list of camera entries matching the image design."""
    st.markdown(textwrap.dedent("""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);overflow:hidden;
    ">
        <div style="
            padding:12px 16px;border-bottom:1px solid var(--border);
            display:flex;align-items:center;justify-content:space-between;
        ">
            <span style="font-family:var(--font-display);font-size:14px;
                font-weight:700;color:var(--text-primary);">Cameras</span>
            <span style="font-size:11px;color:var(--text-dim);
                font-family:var(--font-mono);">1–15 of 15</span>
        </div>
    """), unsafe_allow_html=True)

    # Pagination nav
    _col1, _col2, _col3 = st.columns([1, 4, 1])
    with _col1:
        st.button("←", width="stretch", key="cam_prev")
    with _col3:
        st.button("→", width="stretch", key="cam_next")

    # Camera rows
    for cam in cameras:
        is_selected = st.session_state.get("_selected_cam_id") == cam["id"]
        bg = "var(--teal-glow)" if is_selected else "transparent"
        border_left = f"border-left:2px solid var(--teal);" if is_selected else "border-left:2px solid transparent;"

        clicked = st.button(
            cam["name"],
            key=f"cam_{cam['id']}",
            width="stretch",
        )
        if clicked:
            st.session_state["_selected_cam_id"] = cam["id"]
            st.session_state["selected_camera"] = cam
            st.rerun()

    st.markdown(textwrap.dedent("""
    </div>
    """), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("+ New Camera", width="stretch", key="open_new_cam"):
        st.session_state["show_new_camera_modal"] = True
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# NEW CAMERA MODAL
# ═══════════════════════════════════════════════════════════════

def render_new_camera_modal():
    """
    'New Camera' modal — mirrors sentixvision3.webp exactly.
    Tabs: General | Humans | Objects | Areas
    """
    if not st.session_state.get("show_new_camera_modal", False):
        return

    # Modal overlay
    st.markdown(textwrap.dedent("""
    <div style="
        position:fixed;inset:0;
        background:rgba(0,0,0,0.7);
        z-index:999;
        backdrop-filter:blur(4px);
    "></div>
    """), unsafe_allow_html=True)

    # Modal box
    st.markdown(textwrap.dedent("""
    <div class="fade-in" style="
        position:fixed;
        top:50%;left:50%;
        transform:translate(-50%,-50%);
        z-index:1000;
        width:560px;max-height:85vh;overflow-y:auto;
        background:var(--bg-modal);
        border:1px solid var(--border-light);
        border-radius:var(--radius-xl);
        box-shadow:0 20px 80px rgba(0,0,0,0.8), 0 0 40px rgba(45,212,191,0.08);
    ">
    """), unsafe_allow_html=True)

    # Modal header
    st.markdown(textwrap.dedent("""
    <div style="
        display:flex;align-items:center;justify-content:space-between;
        padding:16px 20px;border-bottom:1px solid var(--border);
    ">
        <span style="font-family:var(--font-display);font-size:15px;
            font-weight:700;color:var(--text-primary);">New Camera</span>
    </div>
    """), unsafe_allow_html=True)

    # Camera preview
    st.markdown(textwrap.dedent("""
    <div style="
        margin:16px 20px;
        background:var(--bg-elevated);
        border:1px solid var(--border);
        border-radius:var(--radius-md);
        height:200px;
        display:flex;align-items:center;justify-content:center;
        overflow:hidden;position:relative;
    ">
        <span style="font-size:40px;opacity:0.3;">📹</span>
        <div style="
            position:absolute;bottom:8px;right:8px;
            background:rgba(0,0,0,0.6);
            border-radius:4px;padding:3px 8px;
            font-size:10px;color:var(--teal);font-family:var(--font-mono);
        ">PREVIEW</div>
    </div>
    """), unsafe_allow_html=True)

    # Tabs: General | Humans | Objects | Areas
    with st.container():
        st.markdown("<div style='padding:0 20px;'>", unsafe_allow_html=True)
        tab_labels = RECOGNITION_TABS
        tabs = st.tabs(tab_labels)

        # ── GENERAL TAB ───────────────────────────────────────
        with tabs[0]:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            cam_name = st.text_input("Camera Name", placeholder="e.g. Workshop Floor Cam 1",
                                     key="nc_name")
            cam_url  = st.text_input("Stream URL", placeholder="rtsp:// or 0 for webcam",
                                     key="nc_url")
            col_a, col_b = st.columns(2)
            with col_a:
                location = st.text_input("Location", placeholder="Zone A / Entrance",
                                         key="nc_location")
            with col_b:
                resolution = st.selectbox("Resolution", ["1920×1080", "1280×720", "640×480"],
                                          key="nc_res")

            tracker = st.selectbox("Tracker Algorithm", TRACKER_OPTIONS, key="nc_tracker")
            enable_dnn = st.checkbox("Enable DNN model prediction", value=True, key="nc_dnn")
            if enable_dnn:
                st.button("⬆ Upload DNN model", key="nc_upload_dnn", width="stretch")

            st.markdown(textwrap.dedent("""
            <div style="
                background:var(--bg-elevated);border:1px solid var(--border);
                border-radius:var(--radius-md);padding:10px 12px;margin-top:8px;
            ">
                <div style="font-size:11px;color:var(--text-dim);
                    font-family:var(--font-sans);margin-bottom:4px;font-weight:600;">
                    PROJECT SETTINGS
                </div>
            </div>
            """), unsafe_allow_html=True)

            frame_id = st.text_input("Frame ID-name", placeholder="cam-1-2024-01-01",
                                     key="nc_frameid")
            show_class_id = st.checkbox("Show classes ID", value=True, key="nc_showclass")

            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1: st.button("⤡ Resize",      key="nc_resize",     width="stretch")
            with col_t2: st.button("⟡ Undistortion", key="nc_undistort",  width="stretch")
            with col_t3: st.button("⊕ Align",        key="nc_align",      width="stretch")

        # ── HUMANS TAB ────────────────────────────────────────
        with tabs[1]:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _render_humans_tab()

        # ── OBJECTS TAB ───────────────────────────────────────
        with tabs[2]:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _render_objects_tab()

        # ── AREAS TAB ─────────────────────────────────────────
        with tabs[3]:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _render_areas_tab()

        st.markdown("</div>", unsafe_allow_html=True)

    # Modal footer
    st.markdown(textwrap.dedent("""
    <div style="border-top:1px solid var(--border);padding:16px 20px;
        display:flex;justify-content:flex-end;gap:10px;">
    </div>
    """), unsafe_allow_html=True)

    col_cancel, col_save = st.columns([1, 1])
    with col_cancel:
        if st.button("Cancel", key="nc_cancel", width="stretch"):
            st.session_state["show_new_camera_modal"] = False
            st.rerun()
    with col_save:
        if st.button("Save", key="nc_save", width="stretch"):
            _save_new_camera()
            st.session_state["show_new_camera_modal"] = False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_humans_tab():
    """Humans tab — mirrors sentixvision3.webp Humans panel."""
    st.markdown(textwrap.dedent("""
    <div style="
        display:flex;align-items:center;justify-content:space-between;
        margin-bottom:8px;
    ">
        <span style="font-size:13px;font-weight:600;color:var(--text-primary);
            font-family:var(--font-sans);">FACE RECOGNITION</span>
    </div>
    """), unsafe_allow_html=True)

    face_rec = st.toggle("Enable Face Recognition", value=True, key="nc_face_rec")

    if face_rec:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(textwrap.dedent("""<div style='font-size:11px;color:var(--text-dim);font-family:var(--font-sans);margin-bottom:4px;'>Recognition</div>"""), unsafe_allow_html=True)
            recog_mode = st.radio("Recognition Mode", ["Multiple", "Single"],
                                  key="nc_recog_mode", horizontal=True,
                                  label_visibility="collapsed")
        with col_b:
            st.markdown(textwrap.dedent("""<div style='font-size:11px;color:var(--text-dim);font-family:var(--font-sans);margin-bottom:4px;'>Gender Filter</div>"""), unsafe_allow_html=True)
            gender = st.radio("Gender Filter", ["All", "Women", "Men"],
                              key="nc_gender", horizontal=True,
                              label_visibility="collapsed")

        st.checkbox("Select by Age", value=True, key="nc_age")
        col_age1, col_age2 = st.columns(2)
        with col_age1:
            st.number_input("Min Age", min_value=0, max_value=120, value=18, key="nc_min_age")
        with col_age2:
            st.number_input("Max Age", min_value=0, max_value=120, value=65, key="nc_max_age")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()

    # Other recognition toggles
    for label, key, desc in [
        ("EMOTIONS RECOGNITION",  "nc_emotions",  "Happy / Neutral / Angry / Sad"),
        ("MOVEMENTS RECOGNITION", "nc_movements", "Gesture and posture tracking"),
        ("GESTURES RECOGNITION",  "nc_gestures",  "Hand landmark detection via MediaPipe"),
        ("GROUPS TRACKING",       "nc_groups",    "Multi-person cluster analysis"),
    ]:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(textwrap.dedent(f"""
            <div style="padding:4px 0;">
                <div style="font-size:12px;font-weight:700;letter-spacing:0.05em;
                    text-transform:uppercase;color:var(--text-secondary);
                    font-family:var(--font-sans);">{label}</div>
                <div style="font-size:11px;color:var(--text-dim);
                    font-family:var(--font-sans);">{desc}</div>
            </div>
            """), unsafe_allow_html=True)
        with col2:
            st.toggle("Toggle", key=key, value=False, label_visibility="collapsed")


def _render_objects_tab():
    """Objects tab — equipment and product detection settings."""
    st.markdown(textwrap.dedent("""
    <div style="font-size:12px;font-weight:700;letter-spacing:0.05em;
        text-transform:uppercase;color:var(--text-secondary);
        font-family:var(--font-sans);margin-bottom:12px;">
        OBJECT DETECTION
    </div>
    """), unsafe_allow_html=True)

    for label, key, default in [
        ("Detect Equipment / Machines", "nc_obj_equip", True),
        ("Detect Hand Tools",           "nc_obj_tools", False),
        ("Detect Safety Gear (PPE)",    "nc_obj_ppe",   True),
        ("Detect Products / Inventory", "nc_obj_inv",   False),
        ("Custom Class Upload",         "nc_obj_custom",False),
    ]:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(textwrap.dedent(f"""
            <div style="padding:4px 0;font-size:12px;font-weight:600;
                color:var(--text-secondary);font-family:var(--font-sans);">{label}</div>
            """), unsafe_allow_html=True)
        with col2:
            st.toggle("Toggle", key=key, value=default, label_visibility="collapsed")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.text_input("Allowed Production Items",
                  placeholder="e.g. Bolt, Gear, Panel...",
                  key="nc_allowed_items")
    st.checkbox("IOT Connected", value=True, key="nc_iot")
    if st.session_state.get("nc_iot"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.text_input("Data Exchange Protocol",
                          placeholder="MQTT / OPC-UA / REST",
                          key="nc_protocol")
        with col_b:
            st.text_input("Connection Parameters",
                          placeholder="host:port",
                          key="nc_conn_params")


def _render_areas_tab():
    """Areas tab — zone polygon editor."""
    st.markdown(textwrap.dedent("""
    <div style="font-size:12px;font-weight:700;letter-spacing:0.05em;
        text-transform:uppercase;color:var(--text-secondary);
        font-family:var(--font-sans);margin-bottom:12px;">
        ZONE CONFIGURATION
    </div>
    """), unsafe_allow_html=True)

    if "zone_config" not in st.session_state:
        st.session_state["zone_config"] = DEFAULT_ZONES.copy()

    zones = st.session_state["zone_config"]

    for zone_id, zone in zones.items():
        with st.expander(f"📐 {zone['name']}", expanded=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                zones[zone_id]["name"] = st.text_input(
                    "Zone Name", value=zone["name"],
                    key=f"zn_{zone_id}_name",
                )
            with col_b:
                zones[zone_id]["enabled"] = st.toggle(
                    "Enabled", value=zone["enabled"],
                    key=f"zn_{zone_id}_enabled",
                )

            zones[zone_id]["color"] = st.color_picker(
                "Zone Color", value=zone["color"],
                key=f"zn_{zone_id}_color",
            )

            st.markdown(textwrap.dedent("""<div style="font-size:11px;color:var(--text-dim);
                font-family:var(--font-sans);margin-bottom:4px;">
                Zone Points (relative 0.0–1.0)</div>"""),
                unsafe_allow_html=True)

            pts = zone["points_rel"]
            col_pts = st.columns(len(pts))
            for i, (x, y) in enumerate(pts):
                with col_pts[i]:
                    nx = st.number_input(f"P{i+1} X", 0.0, 1.0, float(x),
                                         0.01, key=f"zn_{zone_id}_x{i}")
                    ny = st.number_input(f"P{i+1} Y", 0.0, 1.0, float(y),
                                         0.01, key=f"zn_{zone_id}_y{i}")
                    zones[zone_id]["points_rel"][i] = [nx, ny]

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Add new zone
    if st.button("+ Add Zone", key="add_zone"):
        new_id = f"zone_{len(zones)+1}"
        zones[new_id] = {
            "name": f"Zone {len(zones)+1}",
            "color": "#A855F7",
            "points_rel": [[0.5,0.0],[1.0,0.0],[1.0,1.0],[0.5,1.0]],
            "enabled": True,
        }
        st.rerun()

    # Lines config
    st.markdown(textwrap.dedent("""
    <div style="font-size:12px;font-weight:700;letter-spacing:0.05em;
        text-transform:uppercase;color:var(--text-secondary);
        font-family:var(--font-sans);margin:16px 0 8px;">
        CROSSING LINES / QUEUES
    </div>
    """), unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(textwrap.dedent("""
        <div style="font-size:12px;color:var(--text-secondary);
            font-family:var(--font-sans);">Count Line (horizontal)</div>
        """), unsafe_allow_html=True)
    with col2:
        st.toggle("Toggle", key="nc_count_line", value=False, label_visibility="collapsed")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(textwrap.dedent("""
        <div style="font-size:12px;color:var(--text-secondary);
            font-family:var(--font-sans);">Queue / Dwell detection</div>
        """), unsafe_allow_html=True)
    with col2:
        st.toggle("Toggle", key="nc_queue", value=False, label_visibility="collapsed")


def _save_new_camera():
    """Persist new camera config to session state."""
    cam_data = {
        "id":         len(st.session_state.get("cameras", [])) + 1,
        "name":       st.session_state.get("nc_name", "Unnamed Camera"),
        "url":        st.session_state.get("nc_url", "0"),
        "location":   st.session_state.get("nc_location", ""),
        "tracker":    st.session_state.get("nc_tracker", "ByteTrack"),
        "zone_count": len(st.session_state.get("zone_config", {})),
        "status":     "active",
        "humans": {
            "face_recognition": st.session_state.get("nc_face_rec", False),
            "emotions":         st.session_state.get("nc_emotions", False),
            "movements":        st.session_state.get("nc_movements", False),
            "gestures":         st.session_state.get("nc_gestures", False),
            "groups":           st.session_state.get("nc_groups", False),
        },
        "zones": st.session_state.get("zone_config", DEFAULT_ZONES),
    }
    if "cameras" not in st.session_state:
        st.session_state["cameras"] = []
    st.session_state["cameras"].append(cam_data)


# ═══════════════════════════════════════════════════════════════
# CAMERA DETAIL PANEL
# ═══════════════════════════════════════════════════════════════

def render_camera_detail(camera: dict):
    """Right panel — selected camera configuration summary."""
    st.markdown(textwrap.dedent(f"""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);padding:20px;
    ">
        <div style="
            display:flex;align-items:center;justify-content:space-between;
            margin-bottom:16px;padding-bottom:12px;
            border-bottom:1px solid var(--border);
        ">
            <div>
                <div style="font-family:var(--font-display);font-size:16px;
                    font-weight:700;color:var(--text-primary);">{camera.get('name','—')}</div>
                <div style="font-size:12px;color:var(--text-dim);
                    font-family:var(--font-mono);margin-top:2px;">{camera.get('url','—')}</div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # Detail rows
    rows = [
        ("Location",  camera.get("location", "—")),
        ("Tracker",   camera.get("tracker", "ByteTrack")),
        ("Zones",     str(camera.get("zone_count", 0))),
        ("Status",    camera.get("status", "active").capitalize()),
    ]
    for label, value in rows:
        st.markdown(textwrap.dedent(f"""
        <div style="
            display:flex;justify-content:space-between;
            padding:8px 0;border-bottom:1px solid var(--border);
        ">
            <span style="font-size:12px;color:var(--text-dim);
                font-family:var(--font-sans);">{label}</span>
            <span style="font-size:12px;font-weight:500;color:var(--text-primary);
                font-family:var(--font-sans);">{value}</span>
        </div>
        """), unsafe_allow_html=True)

    humans = camera.get("humans", {})
    enabled_features = [k.replace("_", " ").title()
                        for k, v in humans.items() if v]
    if enabled_features:
        st.markdown(textwrap.dedent("""
        <div style="margin-top:12px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:var(--text-dim);
                font-family:var(--font-sans);margin-bottom:8px;">
                Enabled Features
            </div>
        </div>
        """), unsafe_allow_html=True)
        chips = "".join(f"""
            <span style="
                background:var(--teal-glow);color:var(--teal);
                border:1px solid var(--teal-dim);
                border-radius:20px;padding:3px 10px;
                font-size:11px;font-family:var(--font-sans);
                margin:2px;display:inline-block;
            ">{f}</span>
        """ for f in enabled_features)
        st.markdown(f"<div style='margin-top:4px;'>{chips}</div>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("✎ Edit Camera", key="edit_cam", width="stretch"):
        st.session_state["show_new_camera_modal"] = True
        st.rerun()


def _render_empty_detail():
    """Placeholder when no camera is selected."""
    st.markdown(textwrap.dedent("""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);padding:40px 20px;
        display:flex;flex-direction:column;
        align-items:center;justify-content:center;
        text-align:center;min-height:300px;
    ">
        <div style="font-size:40px;margin-bottom:12px;opacity:0.3;">📷</div>
        <div style="font-family:var(--font-display);font-size:15px;
            font-weight:600;color:var(--text-primary);margin-bottom:6px;">
            No camera selected
        </div>
        <div style="font-size:13px;color:var(--text-secondary);
            font-family:var(--font-sans);max-width:240px;">
            Select a camera from the list or create a new one to view its configuration.
        </div>
    </div>
    """), unsafe_allow_html=True)