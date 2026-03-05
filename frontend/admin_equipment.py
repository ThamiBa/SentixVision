"""
admin_equipment.py — Equipment Management Screen
Mirrors sentixvision1.webp: equipment list, new equipment modal,
maintenance history panel with procedures log.
"""

import streamlit as st
import textwrap
import pandas as pd
from datetime import datetime, date
from frontend.components import (
    section_header, status_badge, alert_banner, PALETTE
)


# ═══════════════════════════════════════════════════════════════
# SAMPLE DATA HELPERS
# ═══════════════════════════════════════════════════════════════

EQUIPMENT_TYPES = [
    "Forklifts", "CNC Machines", "Water Jets", "Milling Machines",
    "Automatic Welders", "Loaders", "Conveyor Belts", "Presses",
]

OPERATIONS = [
    "Oil Change", "Belt Replacement", "Calibration", "Lubrication",
    "Filter Swap", "Software Update", "Electrical Check", "Sensor Alignment",
]


def _mock_equipment() -> pd.DataFrame:
    """Return mock equipment list if DB is unavailable."""
    return pd.DataFrame([
        {"id": 1,  "name": "Forklift 1",          "type": "Forklifts",          "status": "Operational", "location": "Manufacturing #1, Main Entrance", "last_service": "Jun 1, 2021"},
        {"id": 2,  "name": "CNC Machine 1",        "type": "CNC Machines",       "status": "Operational", "location": "Workshop B",                      "last_service": "Mar 15, 2024"},
        {"id": 3,  "name": "Water Jet 1",           "type": "Water Jets",         "status": "Maintenance", "location": "Workshop A",                      "last_service": "Jan 10, 2024"},
        {"id": 4,  "name": "Milling Machine 1",     "type": "Milling Machines",   "status": "Operational", "location": "Workshop C",                      "last_service": "Dec 5, 2023"},
        {"id": 5,  "name": "Automatic Welders 1",   "type": "Automatic Welders",  "status": "Operational", "location": "Assembly Line 2",                 "last_service": "Feb 20, 2024"},
        {"id": 6,  "name": "Loader 1",              "type": "Loaders",            "status": "Offline",     "location": "Warehouse East",                  "last_service": "Nov 30, 2023"},
        {"id": 7,  "name": "Loader 2",              "type": "Loaders",            "status": "Operational", "location": "Warehouse West",                  "last_service": "Apr 5, 2024"},
        {"id": 8,  "name": "Automatic Welders 2",   "type": "Automatic Welders",  "status": "Maintenance", "location": "Assembly Line 1",                 "last_service": "May 1, 2024"},
        {"id": 9,  "name": "Forklift 2",            "type": "Forklifts",          "status": "Operational", "location": "Shipping Bay",                    "last_service": "Jun 10, 2024"},
        {"id": 10, "name": "Loader 3",              "type": "Loaders",            "status": "Operational", "location": "Manufacturing #2",                "last_service": "Jun 12, 2024"},
    ])


def _mock_maintenance_logs(equipment_id: int) -> list:
    return [
        {"id": 1, "name": "Maintenance 1", "date": "Jun 1, 2020",   "ops": ["Operation 1", "Operation 2", "Operation 3"]},
        {"id": 2, "name": "Maintenance 2", "date": "Sep 5, 2020",   "ops": ["Operation 1", "Operation 2"]},
        {"id": 3, "name": "Maintenance 3", "date": "Dec 16, 2020",  "ops": ["Operation 1", "Operation 2", "Operation 3", "Operation 4"]},
        {"id": 4, "name": "Maintenance 4", "date": "Feb 1, 2021",   "ops": ["Operation 1"]},
        {"id": 5, "name": "Maintenance 5", "date": "Jun 10, 2021",  "ops": ["Operation 1"]},
    ]


# ═══════════════════════════════════════════════════════════════
# MAIN EQUIPMENT PAGE
# ═══════════════════════════════════════════════════════════════

def render_equipment_page():
    """
    Main Equipment management page.
    Layout: Equipment list (left) | Maintenance History (right)
    """
    section_header(
        "Equipment Management",
        "Manage machines, assign to cameras, track maintenance.",
        action_label="New Equipment",
    )

    # Trigger new modal from section header button click
    if st.session_state.get("_section_action_clicked"):
        st.session_state["show_new_equipment_modal"] = True
        st.session_state["_section_action_clicked"] = False

    # Modals
    if st.session_state.get("show_new_equipment_modal"):
        render_new_equipment_modal()

    # Main content
    with st.sidebar:
        _render_equipment_list()

    selected = st.session_state.get("selected_equipment")
    if selected:
        _render_maintenance_history(selected)
    else:
        _render_empty_state()


# ═══════════════════════════════════════════════════════════════
# EQUIPMENT LIST
# ═══════════════════════════════════════════════════════════════

def _render_equipment_list():
    """Left column: searchable, paginated equipment list."""
    df = st.session_state.get("equipment_df")
    if df is None:
        df = _mock_equipment()

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
                font-weight:700;color:var(--text-primary);">Equipment</span>
        </div>
    """), unsafe_allow_html=True)

    # Search + New button row
    col_s, col_n = st.columns([3, 1])
    with col_s:
        search = st.text_input("Search Equipment", placeholder="🔍  Search...",
                               key="eq_search", label_visibility="collapsed")
    with col_n:
        if st.button("+ New", key="eq_new", width="stretch"):
            st.session_state["show_new_equipment_modal"] = True
            st.rerun()

    # Filter by search
    if search:
        df = df[df["name"].str.lower().str.contains(search.lower())]

    # Pagination
    page_size = 10
    total     = len(df)
    page      = st.session_state.get("eq_page", 1)
    start     = (page - 1) * page_size
    end       = min(start + page_size, total)
    page_df   = df.iloc[start:end]

    st.markdown(textwrap.dedent(f"""
    <div style="padding:4px 16px;font-size:11px;color:var(--text-dim);
        font-family:var(--font-mono);text-align:right;">
        {start+1}–{end} of {total}
    </div>
    """), unsafe_allow_html=True)

    # Type filter dropdown (column header)
    st.markdown(textwrap.dedent("""
    <table style="width:100%;border-collapse:collapse;">
        <thead>
            <tr style="background:var(--bg-elevated);">
                <th style="padding:8px 14px;font-size:11px;font-weight:700;
                    letter-spacing:0.07em;text-transform:uppercase;
                    color:var(--text-secondary);font-family:var(--font-sans);
                    text-align:left;border-bottom:1px solid var(--border);">
                    Equipment Type ▾
                </th>
                <th style="width:36px;border-bottom:1px solid var(--border);"></th>
            </tr>
        </thead>
        <tbody>
    """), unsafe_allow_html=True)

    for i, row in page_df.iterrows():
        bg = "var(--bg-card)" if i % 2 == 0 else "var(--bg-surface)"
        is_sel = st.session_state.get("_selected_eq_id") == row["id"]
        bg = "var(--teal-glow)" if is_sel else bg

        st.markdown(textwrap.dedent(f"""
            <tr style="background:{bg};cursor:pointer;transition:background 0.12s;"
                onmouseover="this.style.background='var(--bg-elevated)'"
                onmouseout="this.style.background='{bg}'">
                <td style="padding:10px 14px;font-size:13px;color:var(--text-primary);
                    font-family:var(--font-sans);border-bottom:1px solid var(--border);">
                    {row['name']}
                </td>
                <td style="padding:10px 8px;border-bottom:1px solid var(--border);
                    text-align:right;">
                    <span style="color:var(--text-dim);font-size:15px;cursor:pointer;">⋯</span>
                </td>
            </tr>
        """), unsafe_allow_html=True)

        # Invisible click target
        if st.button(f"", key=f"sel_eq_{row['id']}", help=row['name'],
                     use_container_width=False):
            st.session_state["_selected_eq_id"] = row["id"]
            st.session_state["selected_equipment"] = row.to_dict()
            st.rerun()

    st.markdown(textwrap.dedent("""
        </tbody>
    </table>
    """), unsafe_allow_html=True)

    # Pagination controls
    col_p, col_info, col_n2 = st.columns([1, 3, 1])
    with col_p:
        if st.button("←", key="eq_pg_prev") and page > 1:
            st.session_state["eq_page"] = page - 1
            st.rerun()
    with col_n2:
        if st.button("→", key="eq_pg_next") and end < total:
            st.session_state["eq_page"] = page + 1
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# MAINTENANCE HISTORY PANEL
# ═══════════════════════════════════════════════════════════════

def _render_maintenance_history(equipment: dict):
    """Right panel — equipment detail + maintenance log."""
    eq_id = equipment.get("id", 1)
    logs  = _mock_maintenance_logs(eq_id)

    # Header card
    st.markdown(textwrap.dedent(f"""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);padding:20px;
        margin-bottom:16px;
        box-shadow:var(--shadow-card);
    ">
        <div style="
            display:flex;align-items:center;gap:10px;
            margin-bottom:16px;padding-bottom:12px;
            border-bottom:1px solid var(--border);
        ">
            <div style="
                width:28px;height:28px;
                background:var(--teal-glow);border:1px solid var(--teal);
                border-radius:6px;display:flex;align-items:center;
                justify-content:center;font-size:14px;
            ">⊙</div>
            <span style="font-family:var(--font-display);font-size:15px;
                font-weight:700;color:var(--text-primary);">Maintenance History</span>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;">
    """), unsafe_allow_html=True)

    detail_rows = [
        ("Equipment ID",    equipment.get("id", "—")),
        ("Location",        equipment.get("location", "—")),
        ("Equipment Type",  equipment.get("type", "—")),
        ("Maintenance Period", "3 Months"),
        ("Description",     "Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
        ("Last Maintenance", f"{equipment.get('last_service','—')} ✓"),
    ]

    # Left column (3 items)
    left_html = ""
    for label, val in detail_rows[:3]:
        left_html += textwrap.dedent(f"""
        <div style="padding:8px 0;border-bottom:1px solid var(--border);">
            <div style="font-size:11px;color:var(--text-dim);
                font-family:var(--font-sans);margin-bottom:2px;">{label}</div>
            <div style="font-size:13px;color:var(--text-primary);
                font-family:var(--font-sans);font-weight:500;">{val}</div>
        </div>
        """)

    # Right column (3 items)
    right_html = ""
    for label, val in detail_rows[3:]:
        right_html += textwrap.dedent(f"""
        <div style="padding:8px 0;border-bottom:1px solid var(--border);padding-left:20px;">
            <div style="font-size:11px;color:var(--text-dim);
                font-family:var(--font-sans);margin-bottom:2px;">{label}</div>
            <div style="font-size:13px;color:var(--text-primary);
                font-family:var(--font-sans);font-weight:500;">{val}</div>
        </div>
        """)

    st.markdown(textwrap.dedent(f"""
            <div>{left_html}</div>
            <div>{right_html}</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # Maintenance Procedures table
    st.markdown(textwrap.dedent(f"""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);overflow:hidden;
    ">
        <div style="
            display:flex;align-items:center;justify-content:space-between;
            padding:12px 16px;border-bottom:1px solid var(--border);
        ">
            <span style="font-family:var(--font-display);font-size:14px;
                font-weight:700;color:var(--text-primary);">Maintenance Procedures</span>
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:11px;color:var(--text-dim);
                    font-family:var(--font-mono);">1–5 of 5</span>
            </div>
        </div>

        <!-- Pagination nav -->
        <table style="width:100%;border-collapse:collapse;">
            <thead>
                <tr style="background:var(--bg-elevated);">
                    <th style="padding:9px 14px;font-size:11px;font-weight:700;
                        letter-spacing:0.07em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);
                        width:35%;">Name</th>
                    <th style="padding:9px 14px;font-size:11px;font-weight:700;
                        letter-spacing:0.07em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);
                        width:25%;">Date</th>
                    <th style="padding:9px 14px;font-size:11px;font-weight:700;
                        letter-spacing:0.07em;text-transform:uppercase;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        text-align:left;border-bottom:1px solid var(--border);">Operation</th>
                    <th style="width:36px;border-bottom:1px solid var(--border);"></th>
                </tr>
            </thead>
            <tbody>
    """), unsafe_allow_html=True)

    for i, log in enumerate(logs):
        ops_html = "<br>".join(
            f'<span style="color:var(--text-secondary);font-size:12px;">{op}</span>'
            for op in log["ops"]
        )
        bg = "var(--bg-card)" if i % 2 == 0 else "var(--bg-surface)"

        st.markdown(textwrap.dedent(f"""
                <tr style="background:{bg};">
                    <td style="padding:10px 14px;font-size:13px;
                        color:var(--text-primary);font-family:var(--font-sans);
                        font-weight:600;border-bottom:1px solid var(--border);
                        vertical-align:top;">
                        {log['name']}
                    </td>
                    <td style="padding:10px 14px;font-size:13px;
                        color:var(--text-secondary);font-family:var(--font-sans);
                        border-bottom:1px solid var(--border);vertical-align:top;">
                        {log['date']}
                    </td>
                    <td style="padding:10px 14px;
                        border-bottom:1px solid var(--border);
                        vertical-align:top;line-height:1.8;">
                        {ops_html}
                    </td>
                    <td style="padding:10px 8px;text-align:center;
                        border-bottom:1px solid var(--border);vertical-align:top;">
                        <span style="color:var(--text-dim);font-size:15px;
                            cursor:pointer;">⋯</span>
                    </td>
                </tr>
        """), unsafe_allow_html=True)

    st.markdown(textwrap.dedent("""
            </tbody>
        </table>

        <!-- Table pagination -->
        <div style="
            display:flex;align-items:center;justify-content:flex-end;
            padding:10px 16px;gap:8px;border-top:1px solid var(--border);
        ">
            <span style="cursor:pointer;color:var(--text-secondary);
                font-size:14px;padding:4px 8px;border-radius:4px;
                transition:var(--transition);">‹</span>
            <span style="cursor:pointer;color:var(--text-secondary);
                font-size:14px;padding:4px 8px;border-radius:4px;
                transition:var(--transition);">›</span>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # Action buttons
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.button("+ New Procedure", key="new_proc", width="stretch")
    with col_b:
        st.button("✎ Edit Equipment", key="edit_eq", width="stretch")
    with col_c:
        st.button("⊗ Delete", key="del_eq", width="stretch")


def _render_empty_state():
    st.markdown(textwrap.dedent("""
    <div style="
        background:var(--bg-card);border:1px solid var(--border);
        border-radius:var(--radius-lg);padding:60px 20px;
        text-align:center;min-height:300px;
        display:flex;flex-direction:column;
        align-items:center;justify-content:center;
    ">
        <div style="font-size:48px;opacity:0.2;margin-bottom:12px;">⚙</div>
        <div style="font-family:var(--font-display);font-size:16px;
            font-weight:700;color:var(--text-primary);margin-bottom:6px;">
            No equipment selected
        </div>
        <div style="font-size:13px;color:var(--text-secondary);
            font-family:var(--font-sans);max-width:280px;">
            Select a piece of equipment from the list to view its maintenance history and details.
        </div>
    </div>
    """), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# NEW EQUIPMENT MODAL
# ═══════════════════════════════════════════════════════════════

def render_new_equipment_modal():
    """New Equipment form modal — mirrors sentixvision1.webp."""
    with st.form("new_equipment_form", clear_on_submit=True):
        st.markdown(textwrap.dedent("""
        <div style="
            display:flex;align-items:center;gap:10px;margin-bottom:16px;
            padding-bottom:12px;border-bottom:1px solid var(--border);
        ">
            <span style="font-family:var(--font-display);font-size:15px;
                font-weight:700;color:var(--text-primary);">New Equipment</span>
        </div>
        """), unsafe_allow_html=True)

        col_a, col_b = st.columns([3, 1])
        with col_a:
            eq_id = st.text_input("Equipment ID", placeholder="e.g. EQ-2024-001")
        with col_b:
            aruco = st.number_input("Aruco Marker", min_value=0, max_value=999, value=24)

        description = st.text_area("Description", placeholder="Describe this equipment...",
                                   height=80)
        location    = st.text_input("Location", placeholder="e.g. Workshop A, Bay 3")

        col_type, col_role = st.columns([2, 1])
        with col_type:
            eq_type = st.selectbox("Type", EQUIPMENT_TYPES)
        with col_role:
            role = st.radio("Role", ["Active", "Passive"], horizontal=True)

        allowed_items = st.text_input(
            "Allowed Production Items",
            placeholder="e.g. Bolt, Panel, Casing..."
        )

        iot_connected = st.toggle("IOT Connected", value=True)
        if iot_connected:
            col_c, col_d = st.columns(2)
            with col_c:
                data_protocol = st.text_input("Data Exchange Protocol",
                                              placeholder="MQTT / OPC-UA")
            with col_d:
                conn_params = st.text_input("Connection Parameters",
                                            placeholder="host:port")

        col_period, col_date = st.columns(2)
        with col_period:
            maintenance_period = st.selectbox(
                "Maintenance Period (Months)",
                [1, 2, 3, 6, 12],
            )
        with col_date:
            last_maint = st.date_input("Last Maintenance", value=date.today())

        col_cancel, col_save = st.columns([1, 1])
        with col_cancel:
            cancel = st.form_submit_button("Cancel", width="stretch")
        with col_save:
            saved = st.form_submit_button("Save", width="stretch")

        if saved:
            new_entry = {
                "id":                 len(st.session_state.get("equipment_df") if st.session_state.get("equipment_df") is not None else _mock_equipment()) + 1,
                "name":               eq_id or "Unnamed",
                "type":               eq_type,
                "status":             "Operational",
                "location":           location,
                "last_service":       last_maint.strftime("%b %-d, %Y"),
            }
            df = st.session_state.get("equipment_df")
            if df is None:
                df = _mock_equipment()
            st.session_state["equipment_df"] = pd.concat(
                [df, pd.DataFrame([new_entry])], ignore_index=True
            )
            st.session_state["show_new_equipment_modal"] = False
            st.success(f"Equipment '{eq_id}' saved successfully.")
            st.rerun()

        if cancel:
            st.session_state["show_new_equipment_modal"] = False
            st.rerun()