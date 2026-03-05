"""
components.py — Maison Sentix Design System
Premium CSS tokens, reusable card components, metric elements.
"""

import streamlit as st
import textwrap


# ═══════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ═══════════════════════════════════════════════════════════════

PALETTE = {
    "bg_deep":      "#0A0E17",
    "bg_surface":   "#111827",
    "bg_card":      "#161D2E",
    "bg_elevated":  "#1C2537",
    "bg_modal":     "#1A2235",
    "border":       "#1E2D45",
    "border_light": "#2A3A55",
    "teal":         "#2DD4BF",
    "teal_dim":     "#1A7A70",
    "teal_glow":    "rgba(45,212,191,0.15)",
    "blue_accent":  "#3B82F6",
    "text_primary": "#E8EDF5",
    "text_secondary":"#8A9BC2",
    "text_dim":     "#4A5A7A",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "info":         "#3B82F6",
    "yellow_box":   "rgba(234,179,8,0.6)",
    "pink_box":     "rgba(236,72,153,0.6)",
    "cyan_box":     "rgba(6,182,212,0.6)",
}

FONTS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@300;400;500&family=Syne:wght@400;500;600;700;800&display=swap');
"""


# ═══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════

def inject_global_css():
    st.markdown(textwrap.dedent(f"""
    <style>
    {FONTS}

    /* ── Root ─────────────────────────────────────────────── */
    :root {{
        --bg-deep:       {PALETTE['bg_deep']};
        --bg-surface:    {PALETTE['bg_surface']};
        --bg-card:       {PALETTE['bg_card']};
        --bg-elevated:   {PALETTE['bg_elevated']};
        --bg-modal:      {PALETTE['bg_modal']};
        --border:        {PALETTE['border']};
        --border-light:  {PALETTE['border_light']};
        --teal:          {PALETTE['teal']};
        --teal-dim:      {PALETTE['teal_dim']};
        --teal-glow:     {PALETTE['teal_glow']};
        --blue:          {PALETTE['blue_accent']};
        --text-primary:  {PALETTE['text_primary']};
        --text-secondary:{PALETTE['text_secondary']};
        --text-dim:      {PALETTE['text_dim']};
        --success:       {PALETTE['success']};
        --warning:       {PALETTE['warning']};
        --danger:        {PALETTE['danger']};
        --font-sans:     'DM Sans', sans-serif;
        --font-mono:     'DM Mono', monospace;
        --font-display:  'Syne', sans-serif;
        --radius-sm:     6px;
        --radius-md:     10px;
        --radius-lg:     14px;
        --radius-xl:     20px;
        --shadow-card:   0 4px 24px rgba(0,0,0,0.4);
        --shadow-glow:   0 0 24px rgba(45,212,191,0.12);
        --transition:    all 0.2s cubic-bezier(0.4,0,0.2,1);
    }}

    /* ── App shell ────────────────────────────────────────── */
    html, body, .stApp {{
        background: var(--bg-deep) !important;
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
    }}

    /* ── Hide Streamlit chrome ────────────────────────────── */
    #MainMenu, footer {{ display: none !important; }}
    header {{ 
        background: transparent !important;
        z-index: 100 !important; /* Move below topnav */
    }}
    .main-topnav {{
        z-index: 9999 !important;
    }}
    .nav-link:hover {{
        color: var(--teal) !important;
        border-bottom-color: var(--teal) !important;
    }}
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* ── Scrollbar ────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-surface); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border-light); border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--teal-dim); }}

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stSidebar"] > div {{
        padding: 0 !important;
    }}

    /* ── Streamlit inputs → dark theme ───────────────────── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > textarea {{
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > textarea:focus {{
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 3px var(--teal-glow) !important;
        outline: none !important;
    }}
    .stSelectbox > div > div:focus-within {{
        border-color: var(--teal) !important;
    }}

    /* ── Streamlit buttons ────────────────────────────────── */
    .stButton > button {{
        background: var(--teal) !important;
        color: #0A0E17 !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 20px !important;
        transition: var(--transition) !important;
        letter-spacing: 0.01em !important;
    }}
    .stButton > button:hover {{
        background: #25B5A3 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(45,212,191,0.3) !important;
    }}
    .stButton.secondary > button {{
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-light) !important;
    }}
    .stButton.secondary > button:hover {{
        border-color: var(--teal) !important;
        color: var(--teal) !important;
    }}

    /* ── Streamlit toggle ─────────────────────────────────── */
    .stToggle > div {{
        background: var(--bg-elevated) !important;
    }}

    /* ── Streamlit tabs ───────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background: var(--bg-card) !important;
        border-radius: var(--radius-md) !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid var(--border) !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: var(--radius-sm) !important;
        padding: 6px 16px !important;
        border: none !important;
        transition: var(--transition) !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--teal) !important;
        color: #0A0E17 !important;
        font-weight: 600 !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding: 0 !important;
    }}

    /* ── Streamlit dataframe ──────────────────────────────── */
    .stDataFrame {{
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border) !important;
        overflow: hidden !important;
    }}
    .stDataFrame thead tr th {{
        background: var(--bg-elevated) !important;
        color: var(--text-secondary) !important;
        font-family: var(--font-sans) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid var(--border) !important;
    }}
    .stDataFrame tbody tr td {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        border-bottom: 1px solid var(--border) !important;
    }}
    .stDataFrame tbody tr:hover td {{
        background: var(--bg-elevated) !important;
    }}

    /* ── Slider ───────────────────────────────────────────── */
    .stSlider > div > div > div {{
        background: var(--teal) !important;
    }}
    .stSlider > div > div > div > div {{
        background: var(--teal) !important;
        border: 2px solid var(--bg-deep) !important;
        box-shadow: 0 0 8px var(--teal-glow) !important;
    }}

    /* ── Radio ────────────────────────────────────────────── */
    .stRadio > div {{
        gap: 8px !important;
        flex-direction: row !important;
    }}
    .stRadio label {{
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }}

    /* ── Checkbox ─────────────────────────────────────────── */
    .stCheckbox label span {{
        color: var(--text-secondary) !important;
        font-size: 13px !important;
    }}

    /* ── Metric ───────────────────────────────────────────── */
    [data-testid="metric-container"] {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 16px 20px !important;
    }}
    [data-testid="metric-container"] label {{
        color: var(--text-secondary) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }}
    [data-testid="stMetricValue"] {{
        color: var(--text-primary) !important;
        font-family: var(--font-display) !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 12px !important;
    }}

    /* ── Plotly charts ────────────────────────────────────── */
    .js-plotly-plot {{
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border) !important;
        overflow: hidden !important;
    }}

    /* ── Divider ──────────────────────────────────────────── */
    hr {{
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 12px 0 !important;
    }}

    /* ── Expander ─────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }}
    .streamlit-expanderContent {{
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    }}

    /* ── Form ─────────────────────────────────────────────── */
    [data-testid="stForm"] {{
        background: var(--bg-modal) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-xl) !important;
        padding: 24px !important;
    }}

    /* ── Label text ───────────────────────────────────────── */
    .stTextInput label,
    .stSelectbox label,
    .stTextArea label,
    .stSlider label,
    .stNumberInput label {{
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }}

    /* ── Page content wrapper ─────────────────────────────── */
    .page-content {{
        padding: 24px 28px;
        min-height: calc(100vh - 56px);
    }}

    /* ── Animations ───────────────────────────────────────── */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulse-teal {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(45,212,191,0.4); }}
        50%       {{ box-shadow: 0 0 0 6px rgba(45,212,191,0); }}
    }}
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}

    .fade-in {{ animation: fadeInUp 0.35s ease both; }}
    .fade-in-2 {{ animation: fadeInUp 0.35s 0.05s ease both; }}
    .fade-in-3 {{ animation: fadeInUp 0.35s 0.10s ease both; }}
    .fade-in-4 {{ animation: fadeInUp 0.35s 0.15s ease both; }}

    </style>
    """), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# COMPONENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def kpi_card(icon: str, label: str, value: str, delta: str = None,
             delta_positive: bool = True, accent_color: str = None,
             animate_class: str = "fade-in"):
    """
    KPI card — NO position:absolute anywhere.
    Streamlit's HTML sanitizer strips position:absolute divs and renders them as raw text.
    """
    color      = accent_color or PALETTE["teal"]
    border_top = "3px solid " + color
    d_color    = "#10B981" if delta_positive else "#EF4444"
    d_arrow    = "&#x2191;" if delta_positive else "&#x2193;"

    delta_p = (
        "<p style='margin:6px 0 0;padding:0;"
        "color:" + d_color + ";font-size:11px;font-weight:600;"
        "font-family:DM Sans,sans-serif;'>"
        + d_arrow + "&nbsp;" + str(delta) + "</p>"
    ) if delta else ""

    html = (
        "<div style='"
        "background:#161D2E;"
        "border:1px solid #1E2D45;"
        "border-top:" + border_top + ";"
        "border-radius:10px;"
        "padding:18px 20px 16px;"
        "box-shadow:0 4px 24px rgba(0,0,0,0.35);'>"

        "<p style='margin:0 0 8px 0;padding:0;"
        "font-size:10px;font-weight:700;letter-spacing:0.10em;"
        "text-transform:uppercase;color:#4A5A7A;"
        "font-family:DM Sans,sans-serif;'>"
        + icon + "&nbsp;&nbsp;" + label + "</p>"

        "<p style='margin:0;padding:0;"
        "font-size:32px;font-weight:700;color:#E8EDF5;line-height:1;"
        "font-family:Syne,sans-serif;'>"
        + str(value) + "</p>"

        + delta_p +
        "</div>"
    )
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def status_badge(status: str):
    """Colored status pill: Operational / Maintenance / Offline."""
    configs = {
        "operational": ("#10B981", "#052E16", "● Operational"),
        "maintenance":  ("#F59E0B", "#1C1400", "⚙ Maintenance"),
        "offline":      ("#EF4444", "#1F0808", "✕ Offline"),
        "active":       ("#10B981", "#052E16", "● Active"),
        "passive":      ("#8A9BC2", "#1C2537", "○ Passive"),
    }
    key = status.lower()
    color, bg, label = configs.get(key, ("#8A9BC2", "#1C2537", status))
    return textwrap.dedent(f"""
    <span style="
        display: inline-flex; align-items: center; gap: 4px;
        background: {bg}; color: {color};
        border: 1px solid {color}40;
        border-radius: 20px; padding: 3px 10px;
        font-size: 11px; font-weight: 600;
        font-family: var(--font-sans); letter-spacing: 0.03em;
    ">{label}</span>
    """)


def section_header(title: str, subtitle: str = None, action_label: str = None):
    """Page section heading with optional subtitle and CTA."""
    sub_html = f"""
        <p style="
            color: var(--text-secondary); font-size: 13px;
            margin: 4px 0 0; font-family: var(--font-sans);
        ">{subtitle}</p>
    """ if subtitle else ""

    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown(textwrap.dedent(f"""
        <div class="fade-in" style="margin-bottom: 20px;">
            <h2 style="
                font-family: var(--font-display);
                font-size: 22px; font-weight: 700;
                color: var(--text-primary);
                margin: 0; letter-spacing: -0.01em;
            ">{title}</h2>
            {sub_html}
        </div>
        """), unsafe_allow_html=True)
    
    if action_label:
        with col2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button(action_label, key=f"btn_{title}"):
                st.session_state["_section_action_clicked"] = True



def data_table_row(cells: list, is_header: bool = False,
                   actions: bool = True, row_idx: int = 0):
    """Render a single styled table row."""
    bg = "var(--bg-card)" if row_idx % 2 == 0 else "var(--bg-surface)"
    cell_style = f"""
        padding: 11px 14px;
        font-size: {'11px' if is_header else '13px'};
        font-weight: {'700' if is_header else '400'};
        color: {'var(--text-secondary)' if is_header else 'var(--text-primary)'};
        letter-spacing: {'0.06em' if is_header else '0'};
        text-transform: {'uppercase' if is_header else 'none'};
        font-family: var(--font-sans);
        border-bottom: 1px solid var(--border);
        white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
    """
    cells_html = "".join(f"<td style='{cell_style}'>{c}</td>" for c in cells)
    action_html = """
        <td style='padding:8px 14px; border-bottom:1px solid var(--border);'>
            <button style='background:none;border:none;color:var(--text-dim);
                cursor:pointer;font-size:16px;padding:2px 6px;
                border-radius:4px;transition:var(--transition);'>⋯</button>
        </td>
    """ if actions and not is_header else "<td></td>"

    row_bg = "var(--bg-elevated)" if is_header else bg
    return f"""
    <tr style='background:{row_bg};transition:background 0.15s;'
        onmouseover="if(this.style.background!='var(--bg-elevated)')this.style.background='#1C2537'"
        onmouseout="this.style.background='{row_bg}'">
        {cells_html}{action_html}
    </tr>
    """


def alert_banner(icon: str, message: str, severity: str = "warning"):
    """Top-of-page alert strip."""
    colors = {
        "warning": (PALETTE["warning"], "#1C1400"),
        "danger":  (PALETTE["danger"],  "#1F0808"),
        "info":    (PALETTE["info"],    "#0F1F3D"),
        "success": (PALETTE["success"], "#052E16"),
    }
    fg, bg = colors.get(severity, colors["info"])
    st.markdown(textwrap.dedent(f"""
    <div style="
        background: {bg}; border: 1px solid {fg}40;
        border-left: 3px solid {fg};
        border-radius: var(--radius-md);
        padding: 10px 16px; margin-bottom: 16px;
        display: flex; align-items: center; gap: 10px;
        font-family: var(--font-sans); font-size: 13px;
        color: var(--text-primary);
        animation: fadeInUp 0.3s ease;
    ">
        <span style="font-size:16px;">{icon}</span>
        <span>{message}</span>
    </div>
    """), unsafe_allow_html=True)


def modal_shell(title: str, icon: str = "⊕"):
    """Styled modal container header."""
    st.markdown(textwrap.dedent(f"""
    <div style="
        background: var(--bg-modal);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-xl);
        padding: 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6), var(--shadow-glow);
        animation: fadeInUp 0.25s ease;
    ">
        <div style="
            display: flex; align-items: center;
            justify-content: space-between;
            padding: 18px 24px;
            border-bottom: 1px solid var(--border);
        ">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="
                    width:28px;height:28px;
                    background:var(--teal-glow);
                    border:1px solid var(--teal);
                    border-radius:6px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:14px;
                ">{icon}</span>
                <span style="
                    font-family:var(--font-display);
                    font-size:15px;font-weight:700;
                    color:var(--text-primary);
                ">{title}</span>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)


def inline_label(text: str, color: str = None):
    """Small text label above inputs, styled consistently."""
    c = color or PALETTE["text_secondary"]
    st.markdown(textwrap.dedent(f"""
    <div style="
        font-size:11px;font-weight:600;
        letter-spacing:0.07em;text-transform:uppercase;
        color:{c};font-family:var(--font-sans);
        margin-bottom:4px;margin-top:8px;
    ">{text}</div>
    """), unsafe_allow_html=True)


def detection_overlay_legend():
    """Color-coded legend for video annotation overlays."""
    items = [
        (PALETTE["yellow_box"], "Zone 1 / Object"),
        (PALETTE["pink_box"],   "Zone 2 / Alert"),
        (PALETTE["cyan_box"],   "Zone 3 / Tracking"),
    ]
    chips = "".join(textwrap.dedent(f"""
        <div style="display:flex;align-items:center;gap:6px;">
            <div style="
                width:12px;height:12px;border-radius:2px;
                background:{c};flex-shrink:0;
            "></div>
            <span style="font-size:11px;color:var(--text-secondary);
                font-family:var(--font-sans);">{l}</span>
        </div>
    """) for c, l in items)

    st.markdown(textwrap.dedent(f"""
    <div style="
        display:flex;gap:16px;align-items:center;
        padding:8px 12px;
        background:var(--bg-card);
        border:1px solid var(--border);
        border-radius:var(--radius-md);
        margin-bottom:8px;
    ">{chips}</div>
    """), unsafe_allow_html=True)


def loading_spinner(message: str = "Processing…"):
    """Inline loading indicator."""
    st.markdown(textwrap.dedent(f"""
    <div style="
        display:flex;align-items:center;gap:12px;
        padding:16px;color:var(--text-secondary);
        font-family:var(--font-sans);font-size:13px;
    ">
        <div style="
            width:16px;height:16px;
            border:2px solid var(--border-light);
            border-top-color:var(--teal);
            border-radius:50%;
            animation:spin 0.8s linear infinite;
        "></div>
        {message}
    </div>
    """), unsafe_allow_html=True)


def toggle_row(label: str, key: str, default: bool = False,
               description: str = None):
    """Full-width toggle row with label and optional description."""
    desc_html = f"""
        <div style="font-size:11px;color:var(--text-dim);
            font-family:var(--font-sans);margin-top:1px;">{description}</div>
    """ if description else ""

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div style="padding:4px 0;">
            <div style="font-size:13px;font-weight:500;
                color:var(--text-primary);font-family:var(--font-sans);">{label}</div>
            {desc_html}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        return st.toggle("", key=key, value=default, label_visibility="collapsed")


def pagination_bar(current: int, total: int, per_page: int = 10):
    """Table pagination control."""
    start = (current - 1) * per_page + 1
    end   = min(current * per_page, total)
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        st.markdown(f"""
        <div style="
            display:flex;align-items:center;justify-content:center;gap:12px;
            padding:8px;font-family:var(--font-sans);
        ">
            <span style="font-size:12px;color:var(--text-secondary);">
                {start}–{end} of {total}
            </span>
        </div>
        """, unsafe_allow_html=True)
    return col1, col3


def card_shell(content_fn, padding: str = "20px", animate: str = "fade-in"):
    """Generic card wrapper — call content_fn() inside."""
    st.markdown(textwrap.dedent(f"""
    <div class="{animate}" style="
        background:var(--bg-card);
        border:1px solid var(--border);
        border-radius:var(--radius-lg);
        padding:{padding};
        box-shadow:var(--shadow-card);
    ">
    """), unsafe_allow_html=True)
    content_fn()
    st.markdown("</div>", unsafe_allow_html=True)