"""
training_markup.py — Training & Markup Tool
Neural network training, video annotation, section/segmentation markup.
Mirrors sentixvision2.webp.
"""

import streamlit as st
import textwrap
import pandas as pd
from frontend.components import section_header, PALETTE


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

TRACKER_OPTIONS  = ["ByteTrack", "Boosting", "MIL", "KCF", "CSRT", "MOSSE"]
MARKUP_MODES     = ["Section", "Segmentation"]
ANNOTATION_COLORS = {
    "Machining 1": "#06B6D4",   # Cyan
    "Machining 2": "#EAB308",   # Yellow
    "Machining 3": "#EC4899",   # Pink
}

SECTION_ICONS = {
    "green":  "#10B981",
    "yellow": "#F59E0B",
    "red":    "#EF4444",
}


# ═══════════════════════════════════════════════════════════════
# MAIN PAGE
# ═══════════════════════════════════════════════════════════════

def render_training_page():
    """
    Full Training & Markup page layout.
    Left sidebar (settings) | Main video annotation canvas | (no right panel)
    """
    section_header(
        "Training & Markup",
        "Annotate video datasets and train custom neural network models."
    )

    with st.sidebar:
        config = _render_training_sidebar()

    _render_annotation_canvas(config)


# ═══════════════════════════════════════════════════════════════
# LEFT SIDEBAR — PROJECT SETTINGS
# ═══════════════════════════════════════════════════════════════

def _render_training_sidebar():
    """
    Left panel matching sentixvision2.webp:
    Project/Import/Export actions, Sections list,
    Tracker settings, DNN upload, Project settings, Transformations.
    """
    config = {}

    st.markdown(textwrap.dedent("""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);overflow:hidden;
    ">
    """), unsafe_allow_html=True)

    # ── Action buttons row ─────────────────────────────────────
    st.markdown(textwrap.dedent("""
    <div style="
        padding:10px 12px;border-bottom:1px solid var(--border);
        display:flex;gap:6px;flex-wrap:wrap;
    ">
    """), unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.button("Project ▾",  key="tm_project",  width="stretch")
    with col_b:
        st.button("Import ▾",   key="tm_import",   width="stretch")
    with col_c:
        st.button("Export ▾",   key="tm_export",   width="stretch")

    # ── Sections ───────────────────────────────────────────────
    st.markdown(textwrap.dedent("""
    <div style="
        padding:10px 14px 4px;
        font-size:10px;font-weight:700;letter-spacing:0.12em;
        text-transform:uppercase;color:var(--text-dim);
        font-family:var(--font-sans);
    ">Sections</div>
    """), unsafe_allow_html=True)

    sections = st.session_state.get("tm_sections", [
        {"id": 0, "name": "Machining 1", "status": "green",  "has_img": True},
        {"id": 1, "name": "Machining 2", "status": "yellow", "has_img": True},
        {"id": 2, "name": "Machining 3", "status": "red",    "has_img": True},
    ])

    active_section = st.session_state.get("tm_active_section", 1)

    for sec in sections:
        is_active = sec["id"] == active_section
        bg    = "var(--teal-glow)"      if is_active else "transparent"
        color = SECTION_ICONS[sec["status"]]
        border_l = "2px solid var(--teal)" if is_active else "2px solid transparent"

        col_icon, col_name, col_num = st.columns([1, 4, 1])
        with col_icon:
            st.markdown(textwrap.dedent(f"""
            <div style="
                width:10px;height:10px;border-radius:50%;
                background:{color};margin:10px auto;
            "></div>
            """), unsafe_allow_html=True)
        with col_name:
            if st.button(
                f"{sec['id']}  {sec['name']}",
                key=f"tm_sec_{sec['id']}",
                width="stretch",
            ):
                st.session_state["tm_active_section"] = sec["id"]
                st.rerun()
        with col_num:
            st.markdown(textwrap.dedent(f"""
            <div style="
                font-size:10px;color:var(--text-dim);
                font-family:var(--font-mono);
                padding:8px 0;text-align:center;
            ">{'⊞' if sec['has_img'] else ''}</div>
            """), unsafe_allow_html=True)

    config["active_section"] = active_section

    st.markdown("<hr style='margin:8px 0;border-color:var(--border);'>",
                unsafe_allow_html=True)

    # ── Tracker ────────────────────────────────────────────────
    st.markdown(textwrap.dedent("""
    <div style="padding:4px 14px;font-size:10px;font-weight:700;
        letter-spacing:0.12em;text-transform:uppercase;
        color:var(--text-dim);font-family:var(--font-sans);">Tracker</div>
    """), unsafe_allow_html=True)

    tracker = st.selectbox("Tracker type", TRACKER_OPTIONS, key="tm_tracker",
                            label_visibility="collapsed")
    config["tracker"] = tracker

    enable_dnn = st.checkbox("Enable DNN model prediction", value=True, key="tm_dnn")
    config["enable_dnn"] = enable_dnn

    if enable_dnn:
        st.button("⬆ Upload DNN model", key="tm_upload_dnn", width="stretch")

    st.markdown("<hr style='margin:8px 0;border-color:var(--border);'>",
                unsafe_allow_html=True)

    # ── Project Settings ───────────────────────────────────────
    st.markdown(textwrap.dedent("""
    <div style="padding:4px 14px;font-size:10px;font-weight:700;
        letter-spacing:0.12em;text-transform:uppercase;
        color:var(--text-dim);font-family:var(--font-sans);">Project Settings</div>
    """), unsafe_allow_html=True)

    frame_id_name = st.text_input("Frame ID-name",
                                   value="machining-repair-2021-07-28-1-g",
                                   key="tm_frame_id")
    config["frame_id_name"] = frame_id_name

    show_class_id = st.checkbox("Show classes ID", value=True, key="tm_show_class")
    config["show_class_id"] = show_class_id

    st.markdown(textwrap.dedent("""
    <div style="padding:4px 14px;font-size:10px;font-weight:700;
        letter-spacing:0.12em;text-transform:uppercase;
        color:var(--text-dim);font-family:var(--font-sans);
        margin-top:8px;">Transformation</div>
    """), unsafe_allow_html=True)

    col_r, col_u = st.columns(2)
    col_a2, col_c2 = st.columns(2)
    with col_r:  st.button("⤡ Resize",       key="tm_resize",     width="stretch")
    with col_u:  st.button("⟡ Undistortion", key="tm_undistort",  width="stretch")
    with col_a2: st.button("⊕ Align",         key="tm_align",      width="stretch")
    with col_c2: st.button("⊡ Crop",          key="tm_crop",       width="stretch")

    st.markdown("</div>", unsafe_allow_html=True)

    return config


# ═══════════════════════════════════════════════════════════════
# MAIN CANVAS — VIDEO ANNOTATION
# ═══════════════════════════════════════════════════════════════

def _render_annotation_canvas(config: dict):
    """
    Main video annotation area:
    - Mode toggle (Section / Segmentation)
    - Video frame display with overlay boxes
    - Frame navigation controls
    - Frame counter
    """
    # ── Mode toggle bar ────────────────────────────────────────
    st.markdown(textwrap.dedent("""
    <div style="
        display:flex;align-items:center;justify-content:center;
        gap:6px;margin-bottom:12px;
    ">
    """), unsafe_allow_html=True)

    col_l, col_mode, col_r = st.columns([2, 2, 2])
    with col_mode:
        mode = st.radio(
            "Markup Mode", MARKUP_MODES,
            key="tm_mode", horizontal=True,
            label_visibility="collapsed",
        )

    # ── Video canvas ───────────────────────────────────────────
    # ── Video canvas ───────────────────────────────────────────
    # We'll use a single container for the video slot and overlays
    
    # Annotation overlay legend — rendered as a floating-like header
    legend_html = ""
    for section_name, color in ANNOTATION_COLORS.items():
        legend_html += textwrap.dedent(f"""
        <div style="
            display:flex;align-items:center;gap:5px;
            background:rgba(22,29,46,0.8);
            border:1px solid {color}60;
            border-radius:4px;padding:3px 8px;
        ">
            <div style="width:10px;height:10px;
                background:{color}80;border:1px solid {color};
                border-radius:2px;"></div>
            <span style="font-size:11px;color:#fff;
                font-family:var(--font-sans);">{section_name}</span>
        </div>
        """)
    
    st.markdown(textwrap.dedent(f"""
    <div style="
        display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;
    ">
        {legend_html}
    </div>
    """), unsafe_allow_html=True)

    # Simulated annotated frame display
    if st.session_state.get("tm_show_annotations", True):
        _render_mock_annotation_frame(mode)
    else:
        st.markdown(textwrap.dedent("""
        <div style="
            background:#000;border:1px solid var(--border);
            border-radius:var(--radius-lg);overflow:hidden;
            min-height:380px;display:flex;
            align-items:center;justify-content:center;
            color:var(--text-dim);font-family:var(--font-sans);
        ">Video Stream (Paused)</div>
        """), unsafe_allow_html=True)

    # ── Frame navigation controls ──────────────────────────────
    _render_frame_controls()

    # ── Annotation table ───────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    _render_annotation_table(config)


def _render_mock_annotation_frame(mode: str):
    """
    Renders a visual representation of an annotated video frame.
    In production this is replaced by the actual camera frame with OpenCV overlays.
    """
    annotation_style = "border" if mode == "Section" else "filled"

    st.markdown(textwrap.dedent(f"""
    <div style="
        position:relative;width:100%;
        background:linear-gradient(135deg,#1a2035,#0d1520);
        min-height:380px;display:flex;
        align-items:center;justify-content:center;
        border-radius:0;
    ">
        <!-- Frame counter badge -->
        <div style="
            position:absolute;bottom:16px;right:16px;
            background:rgba(0,0,0,0.7);border-radius:4px;
            padding:4px 10px;font-family:var(--font-mono);
            font-size:12px;color:var(--text-secondary);
        ">8741 / 151167</div>

        <!-- Mock annotation boxes -->
        <!-- Box 1 — Machining 1 (cyan) -->
        <div style="
            position:absolute;top:30%;left:25%;
            width:22%;height:35%;
            border:2px solid #06B6D4;
            border-radius:2px;
            background:rgba(6,182,212,0.08);
        ">
            <div style="
                position:absolute;top:-18px;left:0;
                background:#06B6D4;color:#000;
                font-size:10px;font-weight:700;padding:2px 6px;
                font-family:var(--font-sans);border-radius:2px 2px 0 0;
            ">1</div>
        </div>

        <!-- Box 2 — Machining 2 (yellow) -->
        <div style="
            position:absolute;top:15%;left:52%;
            width:20%;height:28%;
            border:2px solid #EAB308;
            border-radius:2px;
            background:rgba(234,179,8,0.15);
        ">
            <div style="
                position:absolute;top:-18px;left:0;
                background:#EAB308;color:#000;
                font-size:10px;font-weight:700;padding:2px 6px;
                font-family:var(--font-sans);border-radius:2px 2px 0 0;
            ">2</div>
        </div>

        <!-- Box 3 — Machining 3 (pink) -->
        <div style="
            position:absolute;bottom:20%;right:6%;
            width:18%;height:30%;
            border:2px solid #EC4899;
            border-radius:2px;
            background:rgba(236,72,153,0.15);
        ">
            <div style="
                position:absolute;top:-18px;left:0;
                background:#EC4899;color:#fff;
                font-size:10px;font-weight:700;padding:2px 6px;
                font-family:var(--font-sans);border-radius:2px 2px 0 0;
            ">3</div>
        </div>

        <!-- Center message -->
        <div style="
            display:flex;flex-direction:column;
            align-items:center;justify-content:center;
            color:rgba(255,255,255,0.15);
            font-family:var(--font-sans);font-size:13px;
            text-align:center;
        ">
            <div style="font-size:32px;margin-bottom:8px;">🎬</div>
            <div>Load a video to begin annotation</div>
            <div style="font-size:11px;margin-top:4px;color:rgba(255,255,255,0.08);">
                Mode: {mode}
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)


def _render_frame_controls():
    """
    Video playback / frame navigation controls.
    Mirrors the -10 / -1 / 1 / +1 / +10 / Predict bar from the screenshot.
    """
    st.markdown(textwrap.dedent("""
    <div style="
        display:flex;align-items:center;justify-content:space-between;
        padding:10px 16px;
        background:var(--bg-card);
        border:1px solid var(--border);
        border-radius:var(--radius-md);
        margin-top:8px;
    ">
        <!-- Play button -->
        <div style="
            width:32px;height:32px;
            border-radius:50%;
            background:var(--bg-elevated);border:1px solid var(--border-light);
            display:flex;align-items:center;justify-content:center;
            cursor:pointer;font-size:12px;color:var(--text-primary);
            transition:var(--transition);
        ">▶</div>

        <!-- Progress bar -->
        <div style="
            flex:1;margin:0 16px;height:3px;
            background:var(--border-light);
            border-radius:2px;position:relative;cursor:pointer;
        ">
            <div style="
                width:5.8%;height:100%;
                background:var(--teal);border-radius:2px;
            "></div>
            <div style="
                position:absolute;top:50%;left:5.8%;
                transform:translate(-50%,-50%);
                width:10px;height:10px;border-radius:50%;
                background:var(--teal);cursor:grab;
                border:2px solid var(--bg-card);
            "></div>
        </div>

        <!-- Frame navigation buttons -->
        <div style="display:flex;align-items:center;gap:4px;">
    """), unsafe_allow_html=True)

    # Frame step buttons
    frame_steps = [("-10", "tm_f_m10"), ("-1", "tm_f_m1"),
                   ("1", "tm_f_cur"),
                   ("+1", "tm_f_p1"), ("+10", "tm_f_p10")]
    cols = st.columns(len(frame_steps) + 1)

    for i, (label, key) in enumerate(frame_steps):
        with cols[i]:
            is_current = label == "1"
            bg = "var(--bg-elevated)" if not is_current else "var(--bg-surface)"
            border = "var(--teal)" if is_current else "var(--border-light)"
            st.button(
                label, key=key,
                width="stretch",
            )

    with cols[-1]:
        st.button("▶▶ Predict", key="tm_predict", width="stretch")

    st.markdown(textwrap.dedent("""
        </div>
    </div>
    """), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ANNOTATION LOG TABLE
# ═══════════════════════════════════════════════════════════════

def _render_annotation_table(config: dict):
    """Table showing all annotations in the current project."""
    annotations = st.session_state.get("tm_annotations", [
        {"section": "Machining 1", "frame_start": 1020, "frame_end": 1240, "class": "Equipment", "annotator": "Admin"},
        {"section": "Machining 2", "frame_start": 3100, "frame_end": 4500, "class": "Worktable", "annotator": "Admin"},
        {"section": "Machining 3", "frame_start": 8000, "frame_end": 8741, "class": "Tools",     "annotator": "Admin"},
    ])

    st.markdown(textwrap.dedent("""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);overflow:hidden;
    ">
        <div style="
            padding:10px 16px;border-bottom:1px solid var(--border);
            display:flex;align-items:center;justify-content:space-between;
        ">
            <span style="font-family:var(--font-display);font-size:13px;
                font-weight:700;color:var(--text-primary);">Annotations</span>
            <span style="font-size:11px;color:var(--text-dim);
                font-family:var(--font-mono);">{} entries</span>
        </div>
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:var(--bg-elevated);">
                    <th style="padding:8px 14px;font-size:10px;font-weight:700;
                        letter-spacing:0.08em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);">Section</th>
                    <th style="padding:8px 14px;font-size:10px;font-weight:700;
                        letter-spacing:0.08em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);">Frame Range</th>
                    <th style="padding:8px 14px;font-size:10px;font-weight:700;
                        letter-spacing:0.08em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);">Class</th>
                    <th style="padding:8px 14px;font-size:10px;font-weight:700;
                        letter-spacing:0.08em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);">Annotator</th>
                    <th style="width:36px;border-bottom:1px solid var(--border);"></th>
                </tr>
            </thead>
            <tbody>
    """).format(len(annotations)), unsafe_allow_html=True)

    for i, ann in enumerate(annotations):
        color = ANNOTATION_COLORS.get(ann["section"], PALETTE["teal"])
        bg = "var(--bg-card)" if i % 2 == 0 else "var(--bg-surface)"
        st.markdown(textwrap.dedent(f"""
                <tr style="background:{bg};">
                    <td style="padding:9px 14px;border-bottom:1px solid var(--border);">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div style="width:8px;height:8px;border-radius:2px;
                                background:{color};flex-shrink:0;"></div>
                            <span style="font-size:13px;color:var(--text-primary);
                                font-family:var(--font-sans);">{ann['section']}</span>
                        </div>
                    </td>
                    <td style="padding:9px 14px;font-size:13px;
                        color:var(--text-secondary);font-family:var(--font-mono);
                        border-bottom:1px solid var(--border);">
                        {ann['frame_start']} → {ann['frame_end']}
                    </td>
                    <td style="padding:9px 14px;font-size:13px;
                        color:var(--text-primary);font-family:var(--font-sans);
                        border-bottom:1px solid var(--border);">{ann['class']}</td>
                    <td style="padding:9px 14px;font-size:13px;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        border-bottom:1px solid var(--border);">{ann['annotator']}</td>
                    <td style="padding:9px 8px;text-align:center;
                        border-bottom:1px solid var(--border);">
                        <span style="color:var(--text-dim);font-size:15px;">⋯</span>
                    </td>
                </tr>
        """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent("""
            </tbody>
        </table>
    </div>
    """), unsafe_allow_html=True)