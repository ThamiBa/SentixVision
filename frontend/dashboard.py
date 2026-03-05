"""
dashboard.py — Maison Sentix Live Dashboard
KPI metrics, live video feed, mood trend chart, zone activity.
FIXED: No broken open/close div HTML mixing with Streamlit widgets.
"""

import streamlit as st
import textwrap
import pandas as pd
import plotly.graph_objects as go
from frontend.components import PALETTE


# ═══════════════════════════════════════════════════════════════
# PLOTLY CHART THEME
# ═══════════════════════════════════════════════════════════════

def _base_layout(height=260, title=""):
    return dict(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(family="DM Sans", color=PALETTE["text_secondary"], size=11),
        margin=dict(l=8, r=8, t=36 if title else 12, b=8),
        showlegend=True,
        height=height,
        title=dict(
            text=title,
            font=dict(size=12, color=PALETTE["text_primary"], family="Syne"),
            x=0.01,
        ) if title else None,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, family="DM Sans"),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
        ),
        xaxis=dict(gridcolor="#1E2D45", linecolor="#1E2D45",
                   tickfont=dict(size=9), showgrid=True),
        yaxis=dict(gridcolor="#1E2D45", linecolor="#1E2D45",
                   tickfont=dict(size=9), showgrid=True, zeroline=False),
    )


# ═══════════════════════════════════════════════════════════════
# KPI CARDS — pure st.markdown, no widget mixing
# ═══════════════════════════════════════════════════════════════

def _kpi_html(icon, label, value, color, delta=None, delta_up=True):
    """
    KPI card using only Streamlit-safe inline styles.
    NO position:absolute — Streamlit's sanitizer strips those divs and renders them as text.
    Uses border-top accent + box-shadow glow instead.
    """
    delta_color = "#10B981" if delta_up else "#EF4444"
    delta_arrow = "&#x2191;" if delta_up else "&#x2193;"   # ↑ ↓ as HTML entities
    glow        = color.replace("#", "")                    # strip # for rgba trick
    border_top  = "3px solid " + color

    delta_html = (
        '<p style="margin:6px 0 0;padding:0;'
        'color:' + delta_color + ';font-size:11px;font-weight:600;'
        'font-family:DM Sans,sans-serif;">'
        + delta_arrow + "&nbsp;" + str(delta) + "</p>"
    ) if delta and not str(delta).startswith("?") else ""

    # Card: no position:absolute anywhere
    card_html = (
        "<div style='"
        "background:#161D2E;"
        "border:1px solid #1E2D45;"
        "border-top:" + border_top + ";"
        "border-radius:10px;"
        "padding:18px 20px 16px 20px;"
        "box-shadow:0 4px 24px rgba(0,0,0,0.35);"
        "margin-bottom:0;'>"

        # Label
        "<p style='margin:0 0 8px 0;padding:0;"
        "font-size:10px;font-weight:700;letter-spacing:0.10em;"
        "text-transform:uppercase;color:#4A5A7A;"
        "font-family:DM Sans,sans-serif;'>"
        + icon + "&nbsp;&nbsp;" + label + "</p>"

        # Value
        "<p style='margin:0;padding:0;"
        "font-size:32px;font-weight:700;color:#E8EDF5;line-height:1;"
        "font-family:Syne,sans-serif;'>"
        + str(value) + "</p>"

        + delta_html +

        "</div>"
    )

    if delta is not None and isinstance(delta, str) and delta.startswith("?"):
        # Overload: if delta starts with ?, treat as a link
        return f'<a href="{delta}" target="_self" style="text-decoration:none;display:block;">{card_html}</a>'
    
    return card_html


def render_kpi_row(metrics: dict):
    """4 primary KPI cards in a row — all pure HTML, no widget mixing."""
    happy       = metrics.get("team_happiness", 0)
    happy_color = "#10B981" if happy >= 40 else "#F59E0B"

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown(_kpi_html("👥", "Live Detected",
                              str(metrics.get("live_count", 0)),   "#2DD4BF", delta="?page=environment"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_html("🏭", "Workers Active",
                              str(metrics.get("worker_count", 0)), "#3B82F6", delta="?page=admin"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_html("🛒", "Clients in Zone",
                              str(metrics.get("client_count", 0)), "#10B981", delta="?page=environment"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi_html("😊", "Team Happiness",
                              f"{happy:.0f}%", happy_color, delta="?page=reporting"),
                    unsafe_allow_html=True)


def render_secondary_kpis(metrics: dict):
    """4 secondary KPI cards."""
    mood  = metrics.get("mood_score", 50)
    angry = metrics.get("angry_count", 0)
    wait  = metrics.get("avg_wait_sec", 0)
    wotd  = metrics.get("worker_of_day", "—")
    wait_str = f"{int(wait)//60}m {int(wait)%60}s" if wait >= 60 else f"{int(wait)}s"

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown(_kpi_html("🌡️", "Store Mood Score",
                              f"{mood:.0f}/100", "#2DD4BF", delta="?page=reporting"),
                    unsafe_allow_html=True)
    with c2:
        angry_color = "#EF4444" if angry > 0 else "#334155"
        st.markdown(_kpi_html("😠", "Angry Alerts",
                              str(angry), angry_color, delta="?page=alerts"),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_html("⏱️", "Avg Session Time",
                              wait_str, "#3B82F6"),
                    unsafe_allow_html=True)
    with c4:
        wotd_label = f"ID #{wotd}" if wotd != "—" else "—"
        st.markdown(_kpi_html("🏆", "Worker of the Day",
                              wotd_label, "#F59E0B", delta="?page=admin"),
                    unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ALERT BANNERS
# ═══════════════════════════════════════════════════════════════

def render_alert_panel(angry_count: int, unknown_count: int, fps: float):
    if angry_count > 0:
        st.markdown(textwrap.dedent(f"""
        <div style="background:#1F0808;border:1px solid #EF444440;
            border-left:3px solid #EF4444;border-radius:8px;
            padding:10px 16px;margin-bottom:10px;
            display:flex;align-items:center;gap:10px;
            font-family:'DM Sans',sans-serif;font-size:13px;color:#E8EDF5;">
            <span style="font-size:16px;">😠</span>
            <span><b>{angry_count} ANGRY individual{'s' if angry_count > 1 else ''}</b>
            detected — attention required.</span>
        </div>
        """), unsafe_allow_html=True)

    if unknown_count > 2:
        st.markdown(textwrap.dedent(f"""
        <div style="background:#1C1400;border:1px solid #F59E0B40;
            border-left:3px solid #F59E0B;border-radius:8px;
            padding:10px 16px;margin-bottom:10px;
            display:flex;align-items:center;gap:10px;
            font-family:'DM Sans',sans-serif;font-size:13px;color:#E8EDF5;">
            <span style="font-size:16px;">⚠️</span>
            <span>{unknown_count} persons detected outside defined zones.</span>
        </div>
        """), unsafe_allow_html=True)

    if 0 < fps < 10:
        st.markdown(textwrap.dedent(f"""
        <div style="background:#0F1F3D;border:1px solid #3B82F640;
            border-left:3px solid #3B82F6;border-radius:8px;
            padding:10px 16px;margin-bottom:10px;
            display:flex;align-items:center;gap:10px;
            font-family:'DM Sans',sans-serif;font-size:13px;color:#E8EDF5;">
            <span style="font-size:16px;">⚡</span>
            <span>Low FPS ({fps:.0f}) — increase Skip Frames or switch to yolov8n.pt.</span>
        </div>
        """), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# VIDEO PANEL
# ═══════════════════════════════════════════════════════════════

def render_video_header(fps: float, camera_url: str, status: str = ""):
    """Pure HTML header bar above video. No position:absolute."""
    fps_color = "#10B981" if fps >= 15 else "#F59E0B" if fps >= 8 else "#EF4444"
    dot_color = "#EF4444" if fps > 0 else "#334155"

    html = (
        "<div style='"
        "background:#1C2537;border:1px solid #1E2D45;"
        "border-bottom:none;border-radius:10px 10px 0 0;"
        "padding:9px 14px;"
        "display:flex;align-items:center;justify-content:space-between;'>"

        # Left: live indicator
        "<div style='display:flex;align-items:center;gap:8px;'>"
        "<div style='width:8px;height:8px;border-radius:50%;background:"
        + dot_color + ";flex-shrink:0;'></div>"
        "<span style='font-size:12px;font-weight:600;color:#E8EDF5;"
        "font-family:DM Sans,sans-serif;letter-spacing:0.05em;'>LIVE FEED</span>"
        "<span style='color:#4A5A7A;font-size:11px;margin-left:5px;'>(" + str(status or "") + ")</span>"
        "</div>"

        # Right: FPS + camera URL
        "<div style='display:flex;align-items:center;gap:10px;'>"
        "<span style='font-size:11px;font-family:DM Mono,monospace;color:"
        + fps_color + ";'>" + str(int(fps or 0)) + " FPS</span>"
        "<span style='color:#334155;'>|</span>"
        "<span style='font-size:11px;color:#4A5A7A;font-family:DM Mono,monospace;'>"
        + str(camera_url) + "</span>"
        "</div>"

        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_video_placeholder_box():
    """Empty state when no camera frame available."""
    st.markdown(textwrap.dedent("""
    <div style="
        background:#0A0E17;border:1px solid #1E2D45;
        border-top:none;border-radius:0 0 10px 10px;
        min-height:340px;
        display:flex;flex-direction:column;
        align-items:center;justify-content:center;
        color:#4A5A7A;font-family:'DM Sans',sans-serif;font-size:13px;gap:8px;
    ">
        <span style="font-size:36px;opacity:0.25;">📹</span>
        <span>Click ▶ START to begin the live feed</span>
    </div>
    """), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# STATS SIDEBAR — only st.metric + st.markdown, no open div mixing
# ═══════════════════════════════════════════════════════════════

def render_stats_sidebar(metrics: dict, emotion_data: dict):
    """Right column: session stats + emotion progress bars."""
    st.markdown(textwrap.dedent("""
    <div style="font-size:10px;font-weight:700;letter-spacing:0.10em;
        text-transform:uppercase;color:#4A5A7A;
        font-family:'DM Sans',sans-serif;margin-bottom:8px;">
        Session Stats
    </div>
    """), unsafe_allow_html=True)

    wotd       = metrics.get("worker_of_day", "—")
    wotd_score = metrics.get("worker_of_day_score", 0)
    angry      = metrics.get("angry_count", 0)
    wait       = metrics.get("avg_wait_sec", 0)

    st.metric("🏆 Worker of Day",
              f"ID #{wotd}" if wotd != "—" else "—",
              delta=f"{wotd_score} happy" if wotd != "—" else None)
    st.metric("😠 Angry Alerts", angry)
    st.metric("⏱️ Avg Session",  f"{int(wait)}s")

    st.markdown(textwrap.dedent("""
    <div style="height:1px;background:#1E2D45;margin:10px 0;"></div>
    <div style="font-size:10px;font-weight:700;letter-spacing:0.10em;
        text-transform:uppercase;color:#4A5A7A;
        font-family:'DM Sans',sans-serif;margin-bottom:8px;">
        Emotion Breakdown
    </div>
    """), unsafe_allow_html=True)

    if emotion_data and sum(emotion_data.values()) > 0:
        _render_emotion_bars(emotion_data)
    else:
        st.markdown(textwrap.dedent("""
        <div style="color:#4A5A7A;font-size:12px;
            font-family:'DM Sans',sans-serif;text-align:center;padding:12px 0;">
            No emotion data yet
        </div>
        """), unsafe_allow_html=True)


def _render_emotion_bars(emotion_data: dict):
    """Horizontal progress bars for each emotion label."""
    colors = {
        "happy":    "#10B981",
        "neutral":  "#3B82F6",
        "angry":    "#EF4444",
        "sad":      "#64748B",
        "surprise": "#F59E0B",
    }
    total = sum(emotion_data.values()) or 1
    bars  = ""
    for emotion, count in emotion_data.items():
        pct   = count / total * 100
        color = colors.get(emotion, "#64748B")
        bars += textwrap.dedent(f"""
        <div style="margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="font-size:11px;color:#8A9BC2;
                    font-family:'DM Sans',sans-serif;text-transform:capitalize;">
                    {emotion}
                </span>
                <span style="font-size:11px;color:#E8EDF5;
                    font-family:'DM Mono',monospace;">{pct:.0f}%</span>
            </div>
            <div style="height:4px;background:#1C2537;border-radius:2px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:{color};
                    border-radius:2px;"></div>
            </div>
        </div>
        """)
    st.markdown(bars, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════

def render_mood_trend(df: pd.DataFrame, height: int = 260):
    """Real-time mood trend line chart."""
    if df is None or len(df) == 0:
        st.markdown(textwrap.dedent(f"""
        <div style="height:{height}px;display:flex;align-items:center;
            justify-content:center;background:#111827;
            border:1px solid #1E2D45;border-radius:10px;
            color:#4A5A7A;font-family:'DM Sans',sans-serif;font-size:13px;">
            No data yet — start the system to see the mood trend
        </div>
        """), unsafe_allow_html=True)
        return

    df  = df.tail(200).copy()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["mood_score"],
        name="Mood Score", mode="lines",
        line=dict(color="#2DD4BF", width=2, shape="spline"),
        fill="tozeroy", fillcolor="rgba(45,212,191,0.07)",
        hovertemplate="Mood: %{y:.0f}<extra></extra>",
    ))

    if "client_count" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["client_count"],
            name="Clients", mode="lines",
            line=dict(color="#3B82F6", width=1.5, dash="dot", shape="spline"),
            yaxis="y2",
            hovertemplate="Clients: %{y}<extra></extra>",
        ))

    layout = _base_layout(height=height, title="Store Mood Trend")
    layout["yaxis"].update(range=[0, 100])
    layout["yaxis2"] = dict(
        overlaying="y", side="right", showgrid=False,
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(size=9, color=PALETTE["text_secondary"]),
    )
    fig.update_layout(**layout)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def render_zone_activity(df: pd.DataFrame, height: int = 260):
    """Stacked bar chart of zone occupancy."""
    if df is None or len(df) < 2:
        st.markdown(textwrap.dedent(f"""
        <div style="height:{height}px;display:flex;align-items:center;
            justify-content:center;background:#111827;
            border:1px solid #1E2D45;border-radius:10px;
            color:#4A5A7A;font-family:'DM Sans',sans-serif;font-size:13px;">
            No occupancy data
        </div>
        """), unsafe_allow_html=True)
        return

    df  = df.tail(60)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["timestamp"], y=df.get("worker_count", []),
                         name="Workers", marker_color="#3B82F6"))
    fig.add_trace(go.Bar(x=df["timestamp"], y=df.get("client_count", []),
                         name="Clients",  marker_color="#2DD4BF"))

    layout           = _base_layout(height=height, title="Zone Occupancy")
    layout["barmode"] = "stack"
    layout["bargap"]  = 0.15
    fig.update_layout(**layout)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════
# SIDEBAR CONTROLS
# ═══════════════════════════════════════════════════════════════

def render_dashboard_sidebar() -> dict:
    """Sidebar controls. Returns settings dict."""
    with st.sidebar:
        st.markdown(textwrap.dedent("""
        <div style="padding:16px 12px 4px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4A5A7A;
                font-family:'DM Sans',sans-serif;margin-bottom:8px;">
                📹 Camera Source
            </div>
        </div>
        """), unsafe_allow_html=True)
        camera_url = st.text_input("Camera URL", value="0",
                                   placeholder="rtsp://... or 0",
                                   label_visibility="collapsed")

        st.markdown(textwrap.dedent("""
        <div style="padding:8px 12px 2px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4A5A7A;
                font-family:'DM Sans',sans-serif;">⚙ AI Settings</div>
        </div>
        """), unsafe_allow_html=True)
        conf_threshold = st.slider("Confidence",        0.10, 0.95, 0.40, 0.05)
        emotion_skip   = st.slider("Emotion Skip Frames", 5,   30,   10,    1)

        st.markdown(textwrap.dedent("""
        <div style="padding:4px 12px 2px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4A5A7A;
                font-family:'DM Sans',sans-serif;">🎛 Mode</div>
        </div>
        """), unsafe_allow_html=True)
        op_mode = st.radio("Mode", ["Analytics", "Security"],
                           horizontal=True, label_visibility="collapsed")

        st.markdown(textwrap.dedent("""
        <div style="padding:4px 12px 2px;">
            <div style="font-size:10px;font-weight:700;letter-spacing:0.12em;
                text-transform:uppercase;color:#4A5A7A;
                font-family:'DM Sans',sans-serif;">🧠 Model</div>
        </div>
        """), unsafe_allow_html=True)
        yolo_model     = st.selectbox("YOLO",    ["yolov8n.pt","yolov8s.pt","yolov8m.pt"],
                                       label_visibility="collapsed")
        emotion_engine = st.selectbox("Emotion", ["DeepFace","FER"],
                                       label_visibility="collapsed")
        st.divider()
        show_fps = st.checkbox("Show FPS counter", value=True)

        c1, c2 = st.columns(2)
        with c1:
            start = st.button("▶ START", width="stretch")
        with c2:
            stop  = st.button("■ STOP",  width="stretch")
        reset = st.button("↺ Reset Analytics", width="stretch")

    return dict(
        camera_url=camera_url, conf_threshold=conf_threshold,
        emotion_skip=emotion_skip, op_mode=op_mode,
        yolo_model=yolo_model, emotion_engine=emotion_engine,
        show_fps=show_fps, start=start, stop=stop, reset=reset,
    )


# ═══════════════════════════════════════════════════════════════
# ORCHESTRATOR — called from app.py
# ═══════════════════════════════════════════════════════════════

# ── Fragment-ready components for high/low frequency refresh ─────

def render_dashboard_live(metrics: dict, slots: dict):
    """
    Renders KPIs, Alerts, and Video/Stats layout into pre-created st.empty() slots.
    """
    # 1. KPIs Row 1
    k_slots = slots.get("kpis", [])
    if len(k_slots) >= 4:
        happy       = metrics.get("team_happiness", 0)
        happy_color = "#10B981" if happy >= 40 else "#F59E0B"
        
        k_slots[0].markdown(_kpi_html("👥", "Live Detected",
                                      str(metrics.get("live_count", 0)),   "#2DD4BF", delta="?page=environment"),
                            unsafe_allow_html=True)
        k_slots[1].markdown(_kpi_html("🏭", "Workers Active",
                                      str(metrics.get("worker_count", 0)), "#3B82F6", delta="?page=admin"),
                            unsafe_allow_html=True)
        k_slots[2].markdown(_kpi_html("🛒", "Clients in Zone",
                                      str(metrics.get("client_count", 0)), "#10B981", delta="?page=environment"),
                            unsafe_allow_html=True)
        k_slots[3].markdown(_kpi_html("😊", "Team Happiness",
                                      f"{happy:.0f}%", happy_color, delta="?page=reporting"),
                            unsafe_allow_html=True)

    # 2. KPIs Row 2
    sk_slots = slots.get("sec_k", [])
    if len(sk_slots) >= 4:
        mood  = metrics.get("mood_score", 50)
        angry = metrics.get("angry_count", 0)
        wait  = metrics.get("avg_wait_sec", 0)
        wotd  = metrics.get("worker_of_day", "—")
        wait_str = f"{int(wait)//60}m {int(wait)%60}s" if wait >= 60 else f"{int(wait)}s"
        
        sk_slots[0].markdown(_kpi_html("🌡️", "Store Mood Score",
                                       f"{mood:.0f}/100", "#2DD4BF", delta="?page=reporting"),
                             unsafe_allow_html=True)
        sk_slots[1].markdown(_kpi_html("😠", "Angry Alerts",
                                       str(angry), "#EF4444" if angry > 0 else "#334155", delta="?page=alerts"),
                             unsafe_allow_html=True)
        sk_slots[2].markdown(_kpi_html("⏱️", "Avg Session Time",
                                       wait_str, "#3B82F6"),
                             unsafe_allow_html=True)
        sk_slots[3].markdown(_kpi_html("🏆", "Worker of the Day",
                                       f"ID #{wotd}" if wotd != "—" else "—", "#F59E0B", delta="?page=admin"),
                             unsafe_allow_html=True)

    # 3. Alerts
    slot_alert = slots.get("alert")
    if slot_alert:
        with slot_alert:
            render_alert_panel(
                angry_count=metrics.get("angry_count", 0),
                unknown_count=metrics.get("unknown_count", 0),
                fps=metrics.get("fps", 0),
            )

    # 4. Video Header
    slot_header = slots.get("header")
    if slot_header:
        with slot_header:
            render_video_header(
                fps=metrics.get("fps", 0),
                camera_url=metrics.get("camera_url", "—"),
                status=metrics.get("system_status", ""),
            )

    # 5. Stats Sidebar
    slot_stats = slots.get("stats")
    if slot_stats:
        with slot_stats:
            render_stats_sidebar(
                metrics=metrics,
                emotion_data=metrics.get("emotion_data", {}),
            )

    # 6. Video Frame Slot
    slot_video = slots.get("video")
    if slot_video:
        state = st.session_state.get("shared_state", {})
        
        if not st.session_state.get("run_system"):
            with slot_video:
                render_video_placeholder_box()
                st.session_state["mjpeg_rendered"] = False
        else:
            if not metrics.get("backend_is_active"):
                with slot_video:
                    import textwrap
                    st.markdown(textwrap.dedent("""
                    <div style='background:#0A0E17;border:1px solid #1E2D45;border-radius:10px;
                         height:480px;display:flex;flex-direction:column;align-items:center;justify-content:center;'>
                        <div class='spinner' style='width:30px;height:30px;border:3px solid #1E2D45;
                             border-top-color:#2DD4BF;border-radius:50%;animation:spin 1s linear infinite;'></div>
                        <p style='color:#4A5A7A;font-family:Syne;font-size:14px;margin-top:15px;'>Connecting to Camera Feed...</p>
                    </div>
                    """), unsafe_allow_html=True)
                st.session_state["mjpeg_rendered"] = False
            else:
                # Backend is active. Only render the HTML component once to avoid flickering.
                if not st.session_state.get("mjpeg_rendered"):
                    with slot_video:
                        from backend.services.mjpeg_server import get_stream_html
                        st.components.v1.html(get_stream_html(), height=480)
                    st.session_state["mjpeg_rendered"] = True

def render_dashboard_charts(df_analytics: pd.DataFrame, slots: dict):
    """Renders the mood and occupancy charts into pre-created st.empty() slots."""
    c_slots = slots.get("charts", [])
    if len(c_slots) >= 2:
        with c_slots[0]:
            render_mood_trend(df_analytics)
        with c_slots[1]:
            render_zone_activity(df_analytics)


def render_dashboard(metrics: dict, df_analytics: pd.DataFrame,
                     video_placeholder, chart_placeholder,
                     emotion_placeholder):
    """
    Legacy/Full dashboard layout (Legacy/Non-fragment version).
    """
    # Re-implementing original layout for non-fragment use
    render_kpi_row(metrics)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    render_secondary_kpis(metrics)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    render_alert_panel(
        angry_count=metrics.get("angry_count", 0),
        unknown_count=metrics.get("unknown_count", 0),
        fps=metrics.get("fps", 0),
    )
    vid_col, stat_col = st.columns([3, 1], gap="small")
    with vid_col:
        render_video_header(fps=metrics.get("fps", 0), camera_url=metrics.get("camera_url", "—"), 
                            status=metrics.get("system_status", ""))
        state = st.session_state.get("shared_state", {})
        if not state.get("backend_is_active"): render_video_placeholder_box()
    with stat_col:
        render_stats_sidebar(metrics=metrics, emotion_data=metrics.get("emotion_data", {}))
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    cc1, cc2 = st.columns([2, 1], gap="small")
    with cc1: render_mood_trend(df_analytics)
    with cc2: render_zone_activity(df_analytics)