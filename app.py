"""
=====================================================================================
  🍄  FACTORY ENERGY & COST MANAGEMENT DASHBOARD
  A world-class Streamlit + Plotly dashboard for an industrial mushroom cultivation
  factory (cooling systems, autoclaves, packing lines).
=====================================================================================
  Run with:  streamlit run app.py
=====================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# =====================================================================================
# PAGE CONFIGURATION
# =====================================================================================
st.set_page_config(
    page_title="Factory Energy & Cost Dashboard",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================================
# GLOBAL CONSTANTS
# =====================================================================================
COLOR_PALETTE = ["#2E86AB", "#06A77D", "#F1A208", "#D64550", "#5C4B99", "#1B998B",
                  "#E07A5F", "#3D5A80", "#8AB17D", "#B56576"]

MACHINE_COLUMNS = ["Machine Name", "Quantity", "kW", "Peak Hours/day", "Off-Peak Hours/day"]

VAT_RATE = 0.07  # 7% VAT, fixed per Thai tax regulations


# =====================================================================================
# CUSTOM CSS — premium, modern, corporate styling
# =====================================================================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* Hide default streamlit chrome for a cleaner corporate look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* ---------------- Sidebar ---------------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        }
        section[data-testid="stSidebar"] * {
            color: #F4F6F7 !important;
        }
        section[data-testid="stSidebar"] .stRadio > label {
            font-weight: 600;
        }

        /* ---------------- Section headers ---------------- */
        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1B2A4A;
            margin-top: 0.4rem;
            margin-bottom: 0.6rem;
            border-left: 5px solid #2E86AB;
            padding-left: 10px;
        }

        /* ---------------- KPI Cards ---------------- */
        .kpi-card {
            border-radius: 16px;
            padding: 22px 24px;
            box-shadow: 0 6px 18px rgba(16, 38, 73, 0.10);
            border: 1px solid rgba(46, 134, 171, 0.10);
            height: 100%;
        }
        .kpi-title {
            font-size: 0.82rem;
            font-weight: 600;
            color: #6B7A99;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 1.9rem;
            font-weight: 800;
            color: #14213D;
            margin-bottom: 6px;
        }
        .kpi-sub {
            font-size: 0.85rem;
            font-weight: 600;
        }
        .kpi-up { color: #D64550; }     /* cost increased -> bad -> red */
        .kpi-down { color: #06A77D; }   /* cost decreased -> good -> green */
        .kpi-flat { color: #6B7A99; }

        .kpi-primary { background: linear-gradient(135deg, #14213D 0%, #2E5090 100%); }
        .kpi-primary .kpi-title, .kpi-primary .kpi-value { color: #FFFFFF !important; }
        .kpi-primary .kpi-sub { color: #E8F0FE !important; }

        .kpi-white { background: #FFFFFF; }

        /* ---------------- Small metric chips ---------------- */
        .chip-card {
            background: #F8FAFC;
            border-radius: 12px;
            padding: 14px 16px;
            border: 1px solid #E9EEF5;
        }
        .chip-label { font-size: 0.75rem; color: #6B7A99; font-weight: 600; text-transform: uppercase; }
        .chip-value { font-size: 1.25rem; color: #14213D; font-weight: 700; margin-top: 2px;}

        /* ---------------- Dataframe polish ---------------- */
        [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

        hr { margin: 0.6rem 0 1.2rem 0; }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================================
# SESSION STATE INITIALIZATION
# =====================================================================================
def init_session_state():
    # --- Rate configuration & historical data (flat keys => auto persisted by widgets) ---
    defaults = {
        "peak_rate": 4.50,
        "offpeak_rate": 2.80,
        "ft_rate": 0.2000,
        "service_charge": 312.24,
        "billing_days": 30,
        "last_month_cost": 850000.0,
        "six_month_avg": 820000.0,
        "actual_peak_kwh": 52000.0,
        "actual_offpeak_kwh": 81000.0,
        "solar_kwh": 15000.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # --- Departments & machines (dict of DataFrames) ---
    if "departments" not in st.session_state:
        st.session_state.departments = {
            "Cooling System": pd.DataFrame([
                {"Machine Name": "Industrial Chiller Unit", "Quantity": 2, "kW": 75.0,
                 "Peak Hours/day": 9.0, "Off-Peak Hours/day": 15.0},
                {"Machine Name": "Cold Room Evaporator Fan", "Quantity": 6, "kW": 3.5,
                 "Peak Hours/day": 10.0, "Off-Peak Hours/day": 14.0},
            ]),
            "Autoclave & Sterilization": pd.DataFrame([
                {"Machine Name": "Autoclave Sterilizer", "Quantity": 3, "kW": 45.0,
                 "Peak Hours/day": 6.0, "Off-Peak Hours/day": 2.0},
                {"Machine Name": "Steam Boiler Feed Pump", "Quantity": 2, "kW": 7.5,
                 "Peak Hours/day": 6.0, "Off-Peak Hours/day": 2.0},
            ]),
            "Packing Line": pd.DataFrame([
                {"Machine Name": "Conveyor Motor", "Quantity": 4, "kW": 2.2,
                 "Peak Hours/day": 8.0, "Off-Peak Hours/day": 0.0},
                {"Machine Name": "Vacuum Sealing Machine", "Quantity": 5, "kW": 1.8,
                 "Peak Hours/day": 8.0, "Off-Peak Hours/day": 0.0},
            ]),
            "Utilities & Lighting": pd.DataFrame([
                {"Machine Name": "Factory LED Lighting", "Quantity": 120, "kW": 0.04,
                 "Peak Hours/day": 10.0, "Off-Peak Hours/day": 12.0},
                {"Machine Name": "Air Compressor", "Quantity": 2, "kW": 15.0,
                 "Peak Hours/day": 8.0, "Off-Peak Hours/day": 4.0},
            ]),
        }

    if "page" not in st.session_state:
        st.session_state.page = "📊 Dashboard"


# =====================================================================================
# CALCULATION ENGINE
# =====================================================================================
def compute_department_theoretical_kwh(departments: dict, billing_days: int) -> pd.DataFrame:
    """Compute theoretical Peak / Off-Peak / Total kWh per department."""
    rows = []
    for dept, df in departments.items():
        if df is None or df.empty:
            peak_kwh, offpeak_kwh = 0.0, 0.0
        else:
            d = df.fillna(0)
            peak_kwh = (d["Quantity"] * d["kW"] * d["Peak Hours/day"]).sum() * billing_days
            offpeak_kwh = (d["Quantity"] * d["kW"] * d["Off-Peak Hours/day"]).sum() * billing_days
        rows.append({
            "Department": dept,
            "Peak kWh": peak_kwh,
            "Off-Peak kWh": offpeak_kwh,
            "Total kWh": peak_kwh + offpeak_kwh,
        })
    return pd.DataFrame(rows)


def compute_net_bill(actual_peak, actual_offpeak, solar):
    """Deduct solar generation from Peak first, remainder from Off-Peak."""
    net_peak = max(actual_peak - solar, 0.0)
    remaining_solar = max(solar - actual_peak, 0.0)
    net_offpeak = max(actual_offpeak - remaining_solar, 0.0)
    solar_used_on_peak = min(solar, actual_peak)
    solar_used_on_offpeak = min(remaining_solar, actual_offpeak)
    return net_peak, net_offpeak, solar_used_on_peak, solar_used_on_offpeak


def compute_total_cost(net_peak, net_offpeak, peak_rate, offpeak_rate, ft_rate, service_charge):
    energy_cost = (net_peak * peak_rate) + (net_offpeak * offpeak_rate)
    net_total_kwh = net_peak + net_offpeak
    ft_cost = net_total_kwh * ft_rate
    subtotal = energy_cost + ft_cost + service_charge
    vat = subtotal * VAT_RATE
    grand_total = subtotal + vat
    return {
        "energy_cost": energy_cost,
        "ft_cost": ft_cost,
        "service_charge": service_charge,
        "subtotal": subtotal,
        "vat": vat,
        "grand_total": grand_total,
        "net_total_kwh": net_total_kwh,
    }


def allocate_cost(dept_theoretical: pd.DataFrame, grand_total: float) -> pd.DataFrame:
    """Allocate the grand total bill to departments by % share of theoretical kWh."""
    df = dept_theoretical.copy()
    total_theoretical = df["Total kWh"].sum()
    if total_theoretical > 0:
        df["Share %"] = df["Total kWh"] / total_theoretical * 100
    else:
        # Fallback: split evenly if no machine data entered yet
        df["Share %"] = 100 / len(df) if len(df) > 0 else 0
    df["Allocated Cost (THB)"] = df["Share %"] / 100 * grand_total
    return df


def run_full_calculation():
    """Central calculation pipeline used by the Dashboard page."""
    billing_days = int(st.session_state.billing_days)
    dept_theo = compute_department_theoretical_kwh(st.session_state.departments, billing_days)

    net_peak, net_offpeak, solar_peak, solar_offpeak = compute_net_bill(
        st.session_state.actual_peak_kwh,
        st.session_state.actual_offpeak_kwh,
        st.session_state.solar_kwh,
    )

    cost = compute_total_cost(
        net_peak, net_offpeak,
        st.session_state.peak_rate, st.session_state.offpeak_rate,
        st.session_state.ft_rate, st.session_state.service_charge,
    )

    allocation = allocate_cost(dept_theo, cost["grand_total"])

    return {
        "dept_theo": dept_theo,
        "net_peak": net_peak,
        "net_offpeak": net_offpeak,
        "solar_peak": solar_peak,
        "solar_offpeak": solar_offpeak,
        "cost": cost,
        "allocation": allocation,
    }


# =====================================================================================
# UI HELPER COMPONENTS
# =====================================================================================
def fmt_thb(value):
    return f"฿{value:,.2f}"


def fmt_kwh(value):
    return f"{value:,.0f} kWh"


def kpi_card(title, value_str, delta_val, delta_pct, invert_good=True, primary=False):
    """Render a single premium KPI card comparing current value to a reference."""
    if delta_val is None:
        sub_html = f'<div class="kpi-sub kpi-flat">— no comparison data —</div>'
    else:
        is_increase = delta_val > 0
        # For cost metrics, an increase is BAD (red), decrease is GOOD (green)
        css_class = "kpi-up" if is_increase else ("kpi-down" if delta_val < 0 else "kpi-flat")
        arrow = "▲" if is_increase else ("▼" if delta_val < 0 else "■")
        sub_html = (f'<div class="kpi-sub {css_class}">{arrow} {fmt_thb(abs(delta_val))} '
                    f'({delta_pct:+.1f}%) vs. reference</div>')

    card_class = "kpi-card kpi-primary" if primary else "kpi-card kpi-white"
    st.markdown(f"""
        <div class="{card_class}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value_str}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


def chip_metric(label, value):
    st.markdown(f"""
        <div class="chip-card">
            <div class="chip-label">{label}</div>
            <div class="chip-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


# =====================================================================================
# PAGE 1 — DASHBOARD
# =====================================================================================
def page_dashboard():
    st.markdown("## 📊 Factory Energy & Cost Dashboard")
    st.caption("Real-time overview of energy consumption, billing, and departmental cost allocation.")
    st.markdown("<hr/>", unsafe_allow_html=True)

    results = run_full_calculation()
    cost = results["cost"]
    dept_theo = results["dept_theo"]
    allocation = results["allocation"]

    grand_total = cost["grand_total"]
    last_month = st.session_state.last_month_cost
    six_avg = st.session_state.six_month_avg

    delta_vs_last = grand_total - last_month if last_month else None
    pct_vs_last = (delta_vs_last / last_month * 100) if last_month else 0

    delta_vs_avg = grand_total - six_avg if six_avg else None
    pct_vs_avg = (delta_vs_avg / six_avg * 100) if six_avg else 0

    # ------------------- Row 1: Primary KPI Cards -------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Total Net Cost (This Month)", fmt_thb(grand_total), None, None, primary=True)
    with c2:
        kpi_card("vs. Last Month's Cost", fmt_thb(last_month), delta_vs_last, pct_vs_last)
    with c3:
        kpi_card("vs. 6-Month Average", fmt_thb(six_avg), delta_vs_avg, pct_vs_avg)

    st.write("")

    # ------------------- Row 2: Secondary Chip Metrics -------------------
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        chip_metric("Net Peak kWh (billed)", fmt_kwh(results["net_peak"]))
    with s2:
        chip_metric("Net Off-Peak kWh (billed)", fmt_kwh(results["net_offpeak"]))
    with s3:
        chip_metric("Solar Offset Used", fmt_kwh(results["solar_peak"] + results["solar_offpeak"]))
    with s4:
        chip_metric("Theoretical Machine Usage", fmt_kwh(dept_theo["Total kWh"].sum()))

    st.write("")
    st.write("")

    # ------------------- Row 3: Donut Chart + Peak/Off-Peak Bar -------------------
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.markdown('<div class="section-title">Energy Consumption Share by Department</div>',
                    unsafe_allow_html=True)
        if dept_theo["Total kWh"].sum() > 0:
            fig_donut = go.Figure(data=[go.Pie(
                labels=dept_theo["Department"],
                values=dept_theo["Total kWh"],
                hole=0.58,
                marker=dict(colors=COLOR_PALETTE, line=dict(color="#FFFFFF", width=2)),
                textinfo="percent",
                textfont=dict(size=13, color="white"),
                hovertemplate="<b>%{label}</b><br>%{value:,.0f} kWh<br>%{percent}<extra></extra>",
            )])
            fig_donut.update_layout(
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=11)),
                annotations=[dict(text=f"{dept_theo['Total kWh'].sum():,.0f}<br>kWh Total",
                                   x=0.5, y=0.5, font_size=15, showarrow=False, font=dict(color="#14213D"))],
                margin=dict(t=10, b=10, l=10, r=10),
                height=380,
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No machine data entered yet. Add machines on the Data Entry page.")

    with col_right:
        st.markdown('<div class="section-title">Peak vs. Off-Peak Usage by Department</div>',
                    unsafe_allow_html=True)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Peak kWh", x=dept_theo["Department"], y=dept_theo["Peak kWh"],
            marker_color="#D64550",
            hovertemplate="<b>%{x}</b><br>Peak: %{y:,.0f} kWh<extra></extra>",
        ))
        fig_bar.add_trace(go.Bar(
            name="Off-Peak kWh", x=dept_theo["Department"], y=dept_theo["Off-Peak kWh"],
            marker_color="#2E86AB",
            hovertemplate="<b>%{x}</b><br>Off-Peak: %{y:,.0f} kWh<extra></extra>",
        ))
        fig_bar.update_layout(
            barmode="group",
            height=380,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="kWh / month", gridcolor="#EEF1F6"),
            xaxis=dict(title=None),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("")

    # ------------------- Row 4: Cost Allocation -------------------
    st.markdown('<div class="section-title">💰 Total Bill Cost Allocation by Department</div>',
                unsafe_allow_html=True)
    st.caption("The actual factory bill is distributed proportionally to each department's "
               "theoretical machine energy usage.")

    alloc_sorted = allocation.sort_values("Allocated Cost (THB)", ascending=True)

    col_chart, col_table = st.columns([1.1, 1])
    with col_chart:
        fig_alloc = go.Figure(go.Bar(
            x=alloc_sorted["Allocated Cost (THB)"],
            y=alloc_sorted["Department"],
            orientation="h",
            marker=dict(color=alloc_sorted["Allocated Cost (THB)"], colorscale="Tealgrn"),
            text=[fmt_thb(v) for v in alloc_sorted["Allocated Cost (THB)"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Allocated: %{x:,.2f} THB<extra></extra>",
        ))
        fig_alloc.update_layout(
            height=340,
            margin=dict(t=10, b=10, l=10, r=40),
            xaxis=dict(title="Allocated Cost (THB)", gridcolor="#EEF1F6"),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

    with col_table:
        display_df = allocation[["Department", "Total kWh", "Share %", "Allocated Cost (THB)"]].copy()
        display_df = display_df.sort_values("Allocated Cost (THB)", ascending=False)
        st.dataframe(
            display_df,
            column_config={
                "Total kWh": st.column_config.NumberColumn("Theoretical kWh", format="%.0f"),
                "Share %": st.column_config.NumberColumn("Share %", format="%.1f%%"),
                "Allocated Cost (THB)": st.column_config.NumberColumn("Allocated Cost", format="฿%.2f"),
            },
            hide_index=True,
            use_container_width=True,
            height=340,
        )

    # ------------------- Row 5: Bill Breakdown -------------------
    with st.expander("🧾 View Full Bill Breakdown"):
        b1, b2, b3, b4, b5 = st.columns(5)
        b1.metric("Energy Cost", fmt_thb(cost["energy_cost"]))
        b2.metric("Ft Cost", fmt_thb(cost["ft_cost"]))
        b3.metric("Service Charge", fmt_thb(cost["service_charge"]))
        b4.metric("VAT (7%)", fmt_thb(cost["vat"]))
        b5.metric("Grand Total", fmt_thb(cost["grand_total"]))


# =====================================================================================
# PAGE 2 — DATA ENTRY
# =====================================================================================
def page_data_entry():
    st.markdown("## 📝 Data Entry")
    st.caption("Enter the actual utility bill readings and department machine operating hours.")
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ------------------- Section A: Actual Bill & Solar -------------------
    st.markdown('<div class="section-title">Section A — Actual Bill & Solar Generation</div>',
                unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    with a1:
        st.number_input("Actual Peak kWh (from utility bill)", min_value=0.0, step=100.0,
                         format="%.2f", key="actual_peak_kwh")
    with a2:
        st.number_input("Actual Off-Peak kWh (from utility bill)", min_value=0.0, step=100.0,
                         format="%.2f", key="actual_offpeak_kwh")
    with a3:
        st.number_input("Total Solar Generation (kWh)", min_value=0.0, step=100.0,
                         format="%.2f", key="solar_kwh")

    st.info("💡 Solar generation is deducted from Peak kWh first; any remaining solar credit "
            "offsets Off-Peak kWh.", icon="☀️")

    st.write("")
    st.write("")

    # ------------------- Section B: Machine Working Hours -------------------
    st.markdown('<div class="section-title">Section B — Machine Working Hours by Department</div>',
                unsafe_allow_html=True)
    st.caption("Edit rows directly in each table. Use the ➕ button (last row) to add a machine, "
               "or select a row and press Delete to remove it.")

    for dept in list(st.session_state.departments.keys()):
        df = st.session_state.departments[dept]
        theoretical_kwh = 0.0
        if not df.empty:
            d = df.fillna(0)
            theoretical_kwh = ((d["Quantity"] * d["kW"] * d["Peak Hours/day"]) +
                                (d["Quantity"] * d["kW"] * d["Off-Peak Hours/day"])).sum() * st.session_state.billing_days

        with st.expander(f"🏭 {dept}  —  {theoretical_kwh:,.0f} kWh / month (theoretical)", expanded=False):
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_{dept}",
                column_config={
                    "Machine Name": st.column_config.TextColumn("Machine Name", required=True),
                    "Quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1, format="%d"),
                    "kW": st.column_config.NumberColumn("kW (per unit)", min_value=0.0, step=0.1, format="%.2f"),
                    "Peak Hours/day": st.column_config.NumberColumn("Peak Hours/day", min_value=0.0,
                                                                      max_value=24.0, step=0.5, format="%.1f"),
                    "Off-Peak Hours/day": st.column_config.NumberColumn("Off-Peak Hours/day", min_value=0.0,
                                                                         max_value=24.0, step=0.5, format="%.1f"),
                },
            )
            st.session_state.departments[dept] = edited_df


# =====================================================================================
# PAGE 3 — SETTINGS
# =====================================================================================
def page_settings():
    st.markdown("## ⚙️ Settings")
    st.caption("Configure electricity rates, historical benchmarks, and factory departments.")
    st.markdown("<hr/>", unsafe_allow_html=True)

    # ------------------- Rate Configurations -------------------
    st.markdown('<div class="section-title">Rate Configurations</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.number_input("Peak Rate (THB/kWh)", min_value=0.0, step=0.01, format="%.4f", key="peak_rate")
    with r2:
        st.number_input("Off-Peak Rate (THB/kWh)", min_value=0.0, step=0.01, format="%.4f", key="offpeak_rate")
    with r3:
        st.number_input("Ft Rate (THB/kWh)", min_value=-5.0, step=0.001, format="%.4f", key="ft_rate")
    with r4:
        st.number_input("Monthly Service Charge (THB)", min_value=0.0, step=1.0, format="%.2f",
                         key="service_charge")

    st.number_input("Billing Days in Month", min_value=1, max_value=31, step=1, key="billing_days",
                     help="Used to convert daily machine hours into monthly theoretical kWh.")

    st.write("")

    # ------------------- Historical Data -------------------
    st.markdown('<div class="section-title">Historical Data</div>', unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1:
        st.number_input("Last Month's Bill (THB)", min_value=0.0, step=1000.0, format="%.2f",
                         key="last_month_cost")
    with h2:
        st.number_input("6-Month Average Bill (THB)", min_value=0.0, step=1000.0, format="%.2f",
                         key="six_month_avg")

    st.write("")

    # ------------------- Department Management -------------------
    st.markdown('<div class="section-title">Department Management</div>', unsafe_allow_html=True)

    dcol1, dcol2 = st.columns(2)

    with dcol1:
        st.markdown("**➕ Add New Department**")
        new_dept_name = st.text_input("New Department Name", key="new_dept_input",
                                       placeholder="e.g. Cold Storage Warehouse")
        if st.button("Add Department", type="primary", use_container_width=True):
            name = new_dept_name.strip()
            if not name:
                st.warning("Please enter a department name.")
            elif name in st.session_state.departments:
                st.warning(f"Department '{name}' already exists.")
            else:
                st.session_state.departments[name] = pd.DataFrame(columns=MACHINE_COLUMNS)
                st.success(f"Department '{name}' added.")
                st.rerun()

    with dcol2:
        st.markdown("**🗑️ Delete Department**")
        if st.session_state.departments:
            dept_to_delete = st.selectbox("Select Department to Delete",
                                           options=list(st.session_state.departments.keys()),
                                           key="delete_dept_select")
            if st.button("Delete Department", type="secondary", use_container_width=True):
                del st.session_state.departments[dept_to_delete]
                st.success(f"Department '{dept_to_delete}' deleted.")
                st.rerun()
        else:
            st.info("No departments available.")

    st.write("")
    with st.expander("Current Departments Overview"):
        for dept, df in st.session_state.departments.items():
            st.write(f"**{dept}** — {len(df)} machine type(s)")


# =====================================================================================
# SIDEBAR NAVIGATION
# =====================================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🍄 MycoFactory")
        st.caption("Energy & Cost Management System")
        st.markdown("---")

        page = st.radio(
            "Navigate",
            options=["📊 Dashboard", "📝 Data Entry", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption(f"Billing cycle: **{st.session_state.billing_days} days**")
        st.caption(f"Departments tracked: **{len(st.session_state.departments)}**")
        st.markdown("---")
        st.caption("v1.0 · Built with Streamlit + Plotly")

    return page


# =====================================================================================
# MAIN APP ENTRY POINT
# =====================================================================================
def main():
    inject_css()
    init_session_state()

    page = render_sidebar()

    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "📝 Data Entry":
        page_data_entry()
    elif page == "⚙️ Settings":
        page_settings()


if __name__ == "__main__":
    main()
