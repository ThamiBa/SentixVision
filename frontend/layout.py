"""
layout.py — Maison Sentix Page Shell & Navigation
FIXED: All HTML built via string concatenation — no f-string CSS brace conflicts.
"""

import streamlit as st
import textwrap
from frontend.components import inject_global_css, PALETTE


# ═══════════════════════════════════════════════════════════════
# PAGE WRAPPERS
# ═══════════════════════════════════════════════════════════════

def page_content_wrapper():
    """Opening tag for consistent page padding."""
    st.markdown(textwrap.dedent('<div style="padding:16px 24px;">'), unsafe_allow_html=True)

def close_page_content():
    """Closing tag for consistent page padding."""
    st.markdown(textwrap.dedent('</div>'), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# NAV CONFIG
# ═══════════════════════════════════════════════════════════════

NAV_ITEMS = [
    {"id": "dashboard",   "icon": "⊞", "label": "Dashboard"},
    {"id": "environment", "icon": "⊙", "label": "Environment Designer"},
    {"id": "training",    "icon": "⟳", "label": "Training & Markup"},
    {"id": "admin",       "icon": "⊛", "label": "Administration", "dropdown": True,
     "subitems": [
         {"id": "admin",      "icon": "⚙", "label": "Equipment"},
         {"id": "admin_users", "icon": "👤", "label": "Users"},
     ]},
    {"id": "alerts",      "icon": "⊘", "label": "Alerts",         "dropdown": True,
     "subitems": [
         {"id": "alerts",     "icon": "🔔", "label": "Live Alerts"},
         {"id": "history",    "icon": "📜", "label": "History"},
     ]},
    {"id": "reporting",   "icon": "⊟", "label": "Reporting",      "dropdown": True,
     "subitems": [
         {"id": "reporting",   "icon": "📊", "label": "Analytics"},
         {"id": "export",      "icon": "📥", "label": "Export Data"},
     ]},
]

LOGO_SVG = (
    '<svg width="28" height="28" viewBox="0 0 28 28" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="14" cy="14" r="13" stroke="#2DD4BF" stroke-width="1.5"/>'
    '<circle cx="14" cy="14" r="7"  stroke="#2DD4BF" stroke-width="1"/>'
    '<circle cx="14" cy="14" r="2"  fill="#2DD4BF"/>'
    '<line x1="14" y1="1"  x2="14" y2="6"  stroke="#2DD4BF" stroke-width="1.2"/>'
    '<line x1="14" y1="22" x2="14" y2="27" stroke="#2DD4BF" stroke-width="1.2"/>'
    '<line x1="1"  y1="14" x2="6"  y2="14" stroke="#2DD4BF" stroke-width="1.2"/>'
    '<line x1="22" y1="14" x2="27" y2="14" stroke="#2DD4BF" stroke-width="1.2"/>'
    '</svg>'
)


# ═══════════════════════════════════════════════════════════════
# TOP NAVIGATION BAR
# ═══════════════════════════════════════════════════════════════

def render_topnav(active_page: str = "dashboard"):
    """
    Sticky top nav bar. Built with string concatenation only —
    no f-strings with CSS curly braces.
    """
    bg     = PALETTE["bg_surface"]    # "#111827"
    border = PALETTE["border"]        # "#1E2D45"

    # ── Build nav link items ───────────────────────────────────
    links_html = ""
    for item in NAV_ITEMS:
        is_active  = item["id"] == active_page
        txt_color  = "#E8EDF5" if is_active else "#8A9BC2"
        bot_border = "2px solid #2DD4BF" if is_active else "2px solid transparent"
        arrow      = " &#x25BE;" if item.get("dropdown") else ""

        links_html += (
            f'<a href="?page={item["id"]}" target="_self" class="nav-link" style="'
            'text-decoration:none;'
            'display:inline-flex;align-items:center;gap:5px;'
            'font-family:\'DM Sans\',sans-serif;'
            'font-size:13px;font-weight:500;'
            'color:' + txt_color + ';'
            'border-bottom:' + bot_border + ';'
            'padding:0 2px;height:100%;'
            'white-space:nowrap;'
            'transition:all 0.2s ease;">'
            '<span style="font-size:12px;opacity:0.6;">' + item["icon"] + '</span>'
            + item["label"] + arrow +
            '</a>'
        )

    # ── Assemble full nav ──────────────────────────────────────
    html = (
        '<nav class="main-topnav" style="'
        'position:sticky;top:0;z-index:9999;'
        'background:' + bg + ';'
        'border-bottom:1px solid ' + border + ';'
        'padding:0 24px;height:52px;'
        'display:flex;align-items:center;justify-content:space-between;'
        'backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);">'

        # Logo
        '<div style="display:flex;align-items:center;gap:10px;flex-shrink:0;">'
        + LOGO_SVG +
        '<span style="'
        'font-family:\'Syne\',sans-serif;'
        'font-size:15px;font-weight:700;'
        'color:#E8EDF5;letter-spacing:-0.02em;">'
        'Maison Sentix'
        '</span>'
        '</div>'

        # Nav links
        '<div style="display:flex;align-items:center;gap:20px;height:100%;">'
        + links_html +
        '</div>'

        # Right: bell + avatar
        '<div style="display:flex;align-items:center;gap:14px;flex-shrink:0;">'

        # Bell icon — no position:absolute (Streamlit sanitizes it)
        '<div style="'
        'cursor:pointer;width:32px;height:32px;'
        'display:flex;align-items:center;justify-content:center;'
        'border-radius:8px;">'
        '<span style="font-size:15px;color:#8A9BC2;">&#x1F514;</span>'
        '</div>'

        # Vertical divider
        '<div style="width:1px;height:20px;background:' + border + ';"></div>'

        # User avatar
        '<div style="'
        'width:30px;height:30px;'
        'background:linear-gradient(135deg,#2DD4BF,#3B82F6);'
        'border-radius:50%;'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:12px;font-weight:700;color:#0A0E17;'
        'cursor:pointer;'
        'font-family:\'Syne\',sans-serif;'
        'border:2px solid ' + border + ';">'
        'MS'
        '</div>'

        '</div>'  # end right actions
        '</nav>'
    )

    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# PAGE INIT
# ═══════════════════════════════════════════════════════════════

def init_page(page_title: str = "Dashboard"):
    """
    Call at the very top of every page before any other st.* calls.
    Sets page config, injects global CSS, renders nav bar.
    Returns the active page ID string.
    """
    st.set_page_config(
        page_title="Maison Sentix — " + page_title,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_css()

    params = st.query_params
    active = params.get("page", "dashboard")
    st.session_state["_active_page"] = active

    render_topnav(active_page=active)
    render_sidebar_nav(NAV_ITEMS, active=active)
    return active


# ═══════════════════════════════════════════════════════════════
# BREADCRUMB
# ═══════════════════════════════════════════════════════════════

def breadcrumb(crumbs: list):
    """
    crumbs: [("Administration", False), ("Equipment", True)]
    Last item is highlighted as active.
    """
    parts = ""
    for i, (label, is_active) in enumerate(crumbs):
        color = "#E8EDF5" if is_active else "#4A5A7A"
        sep   = "" if i == len(crumbs) - 1 else (
            '<span style="color:#4A5A7A;margin:0 6px;">/</span>'
        )
        parts += (
            '<span style="color:' + color + ';font-size:12px;'
            'font-family:\'DM Sans\',sans-serif;">' + label + '</span>'
            + sep
        )

    st.markdown(textwrap.dedent(f"""
        <div style="display:flex;align-items:center;margin-bottom:16px;padding:8px 0;">
        {parts}</div>"""),
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════

def page_header(icon: str, title: str, subtitle: str = None, back_href: str = None):
    """Styled page title block with optional back link."""
    back_html = (
        '<a href="' + back_href + '" style="'
        'display:inline-flex;align-items:center;gap:6px;'
        'color:#8A9BC2;text-decoration:none;'
        'font-size:12px;font-family:\'DM Sans\',sans-serif;'
        'font-weight:500;margin-bottom:12px;">'
        '&#x2190; Back'
        '</a>'
    ) if back_href else ""

    sub_html = (
        '<p style="color:#8A9BC2;font-size:13px;'
        'margin:4px 0 0;font-family:\'DM Sans\',sans-serif;">'
        + subtitle + '</p>'
    ) if subtitle else ""

    html = (
        '<div style="padding:20px 0 16px;border-bottom:1px solid #1E2D45;margin-bottom:24px;">'
        + back_html +
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<div style="'
        'width:36px;height:36px;'
        'background:rgba(45,212,191,0.15);'
        'border:1px solid #2DD4BF;'
        'border-radius:8px;'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:16px;flex-shrink:0;">'
        + icon + '</div>'
        '<div>'
        '<h1 style="'
        'font-family:\'Syne\',sans-serif;'
        'font-size:20px;font-weight:700;'
        'color:#E8EDF5;margin:0;letter-spacing:-0.02em;">'
        + title + '</h1>'
        + sub_html +
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SIDEBAR NAV
# ═══════════════════════════════════════════════════════════════

def render_sidebar_nav(items: list, active: str = None):
    """Vertical left sidebar navigation links."""
    with st.sidebar:
        st.markdown(
            '<div style="padding:16px 12px 8px;">'
            '<div style="font-size:10px;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:#4A5A7A;'
            'font-family:\'DM Sans\',sans-serif;margin-bottom:8px;">'
            'Navigation</div></div>',
            unsafe_allow_html=True,
        )

        for item in items:
            is_active = (active == item["id"])
            bg    = "var(--teal-glow)" if is_active else "transparent"
            color = "var(--teal)"      if is_active else "var(--text-secondary)"
            left_bord = "3px solid var(--teal)" if is_active else "3px solid transparent"

            st.markdown(textwrap.dedent(f"""
                <a href="?page={item["id"]}" target="_self" style="
                display:flex;align-items:center;gap:10px;
                padding:9px 14px;margin:1px 8px;
                background:{bg};
                border-left:{left_bord};
                border-radius:0 8px 8px 0;
                text-decoration:none;color:{color};
                font-family:'DM Sans',sans-serif;
                font-size:13px;font-weight:500;">
                <span style="font-size:14px;">{item["icon"]}</span>
                {item["label"]}</a>"""),
                unsafe_allow_html=True,
            )

            # Render sub-items if active or if it's a dropdown category
            if "subitems" in item and (is_active or item.get("dropdown")):
                for sub in item["subitems"]:
                    sub_active = (active == sub["id"])
                    s_color = "var(--teal)" if sub_active else "var(--text-dim)"
                    st.markdown(textwrap.dedent(f"""
                        <a href="?page={sub["id"]}" target="_self" style="
                        display:flex;align-items:center;gap:10px;
                        padding:6px 14px 6px 40px;margin:1px 8px;
                        text-decoration:none;color:{s_color};
                        font-family:'DM Sans',sans-serif;
                        font-size:12px;font-weight:400;">
                        <span style="font-size:12px;">{sub["icon"]}</span>
                        {sub["label"]}</a>"""),
                        unsafe_allow_html=True,
                    )