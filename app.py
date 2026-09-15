"""
=====================================================================================
  🍄  FACTORY ENERGY & COST MANAGEMENT DASHBOARD (TURNKEY EDITION)
  A production-ready Streamlit + Plotly dashboard with automated history tracking.
=====================================================================================
  Run with:  streamlit run app.py
=====================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime

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
# GLOBAL CONSTANTS & STORAGE FILE
# =====================================================================================
COLOR_PALETTE = ["#2E86AB", "#06A77D", "#F1A208", "#D64550", "#5C4B99", "#1B998B",
                 "#E07A5F", "#3D5A80", "#8AB17D", "#B56576"]
HISTORY_FILE = "factory_history.json"
VAT_RATE = 0.07

# =====================================================================================
# CUSTOM CSS — Corporate Styling
# =====================================================================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container { padding-top: 2rem; padding-bottom: 3rem; }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        }
        section[data-testid="stSidebar"] * { color: #F4F6F7 !important; }
        .section-title {
            font-size: 1.15rem; font-weight: 700; color: #1B2A4A;
            margin-top: 0.4rem; margin-bottom: 0.6rem;
            border-left: 5px solid #2E86AB; padding-left: 10px;
        }
        .kpi-card {
            border-radius: 16px; padding: 22px 24px;
            box-shadow: 0 6px 18px rgba(16, 38, 73, 0.10);
            border: 1px solid rgba(46, 134, 171, 0.10); height: 100%; background: #FFFFFF;
        }
        .kpi-title {
            font-size: 0.82rem; font-weight: 600; color: #6B7A99;
            text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;
        }
        .kpi-value { font-size: 1.9rem; font-weight: 800; color: #14213D; margin-bottom: 6px; }
        .kpi-sub { font-size: 0.85rem; font-weight: 600; }
        .kpi-up { color: #D64550; }
        .kpi-down { color: #06A77D; }
        .kpi-flat { color: #6B7A99; }
        .kpi-primary { background: linear-gradient(135deg, #14213D 0%, #2E5090 100%); }
        .kpi-primary .kpi-title, .kpi-primary .kpi-value { color: #FFFFFF !important; }
        .chip-card {
            background: #F8FAFC; border-radius: 12px; padding: 14px 16px; border: 1px solid #E9EEF5;
        }
        .chip-label { font-size: 0.75rem; color: #6B7A99; font-weight: 600; text-transform: uppercase; }
        .chip-value { font-size: 1.25rem; color: #14213D; font-weight: 700; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================================
# HISTORY STORAGE FUNCTIONS
# =====================================================================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history_record(record):
    history = load_history()
    # Check if record for this month already exists, update or append
    month_str = record["Billing Month"]
    history = [h for h in history if h["Billing Month"] != month_str]
    history.append(record)
    # Sort by month string
    history = sorted(history, key=lambda x: x["Billing Month"])
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# =====================================================================================
# SESSION STATE INITIALIZATION
# =====================================================================================
def init_session_state():
    defaults = {
        "billing_month": datetime.now().strftime("%Y-%m"),
        "peak_rate": 4.50,
        "offpeak_rate": 2.80,
        "ft_rate": 0.2000,
        "service_charge": 312.24,
        "billing_days": 30,
        "actual_peak_kwh": 52000.0,
        "actual_offpeak_kwh": 81000.0,
        "solar_kwh": 15000.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "departments" not in st.session_state:
        st.session_state.departments = {
            "Cooling System": pd.DataFrame([
                {"Machine Name": "Industrial Chiller Unit", "Quantity": 2, "kW": 75.0, "Peak Hours/day": 9.0, "Off-Peak Hours/day": 15.0},
                {"Machine Name": "Cold Room Evaporator Fan", "Quantity": 6, "kW": 3.5, "Peak Hours/day": 10.0, "Off-Peak Hours/day": 14.0},
            ]),
            "Autoclave & Sterilization": pd.DataFrame([
                {"Machine Name": "Autoclave Sterilizer", "Quantity": 3, "kW": 45.0, "Peak Hours/day": 6.0, "Off-Peak Hours/day": 2.0},
                {"Machine Name": "Steam Boiler Feed Pump", "Quantity": 2, "kW": 7.5, "Peak Hours/day": 6.0, "Off-Peak Hours/day": 2.0},
            ]),
            "Packing Line": pd.DataFrame([
                {"Machine Name": "Conveyor Motor", "Quantity": 4, "kW": 2.2, "Peak Hours/day": 8.0, "Off-Peak Hours/day": 0.0},
                {"Machine Name": "Vacuum Sealing Machine", "Quantity": 5, "kW": 1.8, "Peak Hours/day": 8.0, "Off-Peak Hours/day": 0.0},
            ]),
            "Utilities & Lighting": pd.DataFrame([
                {"Machine Name": "Factory LED Lighting", "Quantity": 120, "kW": 0.04, "Peak Hours/day": 10.0, "Off-Peak Hours/day": 12.0},
                {"Machine Name": "Air Compressor", "Quantity": 2, "kW": 15.0, "Peak Hours/day": 8.0, "Off-Peak Hours/day": 4.0},
            ]),
        }

# =====================================================================================
# CALCULATION ENGINE
# =====================================================================================
def run_full_calculation():
    billing_days = int(st.session_state.billing_days)
    rows = []
    for dept, df in st.session_state.departments.items():
        if df is None or df.empty:
            peak_kwh, offpeak_kwh = 0.0, 0.0
        else:
            d = df.fillna(0)
            peak_kwh = (d["Quantity"] * d["kW"] * d["Peak Hours/day"]).sum() * billing_days
            offpeak_kwh = (d["Quantity"] * d["kW"] * d["Off-Peak Hours/day"]).sum() * billing_days
        rows.append({"Department": dept, "Peak kWh": peak_kwh, "Off-Peak kWh": offpeak_kwh, "Total kWh": peak_kwh + offpeak_kwh})
    dept_theo = pd.DataFrame(rows)

    actual_peak = st.session_state.actual_peak_kwh
    actual_offpeak = st.session_state.actual_offpeak_kwh
    solar = st.session_state.solar_kwh

    net_peak = max(actual_peak - solar, 0.0)
    remaining_solar = max(solar - actual_peak, 0.0)
    net_offpeak = max(actual_offpeak - remaining_solar, 0.0)
    solar_peak = min(solar, actual_peak)
    solar_offpeak = min(remaining_solar, actual_offpeak)

    energy_cost = (net_peak * st.session_state.peak_rate) + (net_offpeak * st.session_state.offpeak_rate)
    net_total_kwh = net_peak + net_offpeak
    ft_cost = net_total_kwh * st.session_state.ft_rate
    subtotal = energy_cost + ft_cost + st.session_state.service_charge
    vat = subtotal * VAT_RATE
    grand_total = subtotal + vat

    total_theo = dept_theo["Total kWh"].sum()
    if total_theo > 0:
        dept_theo["Share %"] = dept_theo["Total kWh"] / total_theo * 100
    else:
        dept_theo["Share %"] = 100 / len(dept_theo) if len(dept_theo) > 0 else 0
    dept_theo["Allocated Cost (THB)"] = dept_theo["Share %"] / 100 * grand_total

    return {
        "dept_theo": dept_theo,
        "net_peak": net_peak,
        "net_offpeak": net_offpeak,
        "solar_peak": solar_peak,
        "solar_offpeak": solar_offpeak,
        "cost": {
            "energy_cost": energy_cost, "ft_cost": ft_cost,
            "service_charge": st.session_state.service_charge,
            "subtotal": subtotal, "vat": vat, "grand_total": grand_total,
            "net_total_kwh": net_total_kwh
        },
        "allocation": dept_theo
    }

def fmt_thb(val): return f"฿{val:,.2f}"
def fmt_kwh(val): return f"{val:,.0f} kWh"

# =====================================================================================
# PAGES
# =====================================================================================
def page_dashboard():
    st.markdown("## 📊 Factory Energy & Cost Dashboard")
    st.caption("Real-time overview with automated monthly historical archiving.")
    st.markdown("<hr/>", unsafe_allow_html=True)

    results = run_full_calculation()
    cost = results["cost"]
    dept_theo = results["dept_theo"]
    grand_total = cost["grand_total"]

    # Load history for comparisons
    history = load_history()
    last_month_cost = None
    if len(history) >= 1:
        # Get previous record if available
        last_month_cost = history[-1]["Grand Total (THB)"]

    delta_vs_last = grand_total - last_month_cost if last_month_cost else None
    pct_vs_last = (delta_vs_last / last_month_cost * 100) if last_month_cost else 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="kpi-card kpi-primary">
                <div class="kpi-title">Current Month Cost ({st.session_state.billing_month})</div>
                <div class="kpi-value">{fmt_thb(grand_total)}</div>
                <div class="kpi-sub">Total Net kWh: {fmt_kwh(cost['net_total_kwh'])}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        sub_text = f"▲ {fmt_thb(abs(delta_vs_last))} ({pct_vs_last:+.1f}%) vs last recorded" if delta_vs_last else "— No prior record yet —"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">vs. Previous Recorded Month</div>
                <div class="kpi-value">{fmt_thb(last_month_cost if last_month_cost else grand_total)}</div>
                <div class="kpi-sub">{sub_text}</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Archived Months in System</div>
                <div class="kpi-value">{len(history)} Months</div>
                <div class="kpi-sub">Ready for trend analysis</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # Auto-Save Button
    col_save, col_info = st.columns([1, 3])
    with col_save:
        if st.button("💾 Save Current Month to History", type="primary", use_container_width=True):
            record = {
                "Billing Month": st.session_state.billing_month,
                "Grand Total (THB)": round(grand_total, 2),
                "Total kWh": round(cost["net_total_kwh"], 2),
                "Peak kWh": round(results["net_peak"], 2),
                "Off-Peak kWh": round(results["net_offpeak"], 2)
            }
            save_history_record(record)
            st.success(f"Successfully saved record for {st.session_state.billing_month}!")
            st.rerun()
    with col_info:
        st.info("Clicking save stores this month's data into the system database so historical trends update instantly.")

    st.write("")

    # Historical Trend Section
    if history:
        st.markdown('<div class="section-title">📈 Historical Cost & Energy Trend</div>', unsafe_allow_html=True)
        hist_df = pd.DataFrame(history)
        fig_hist = px.bar(hist_df, x="Billing Month", y="Grand Total (THB)", text_auto=".2s",
                          title="Monthly Total Electricity Cost Trend", color="Grand Total (THB)", color_continuousScale="Tealgrn")
        fig_hist.update_layout(height=350, margin=dict(t=30, b=10, l=10, r=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.write("")
    col_left, col_right = st.columns([1, 1.2])
    with col_left:
        st.markdown('<div class="section-title">Energy Share by Department</div>', unsafe_allow_html=True)
        fig_donut = go.Figure(data=[go.Pie(labels=dept_theo["Department"], values=dept_theo["Total kWh"], hole=0.58,
            marker=dict(colors=COLOR_PALETTE, line=dict(color="#FFFFFF", width=2)))])
        fig_donut.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)
    with col_right:
        st.markdown('<div class="section-title">Cost Allocation by Department</div>', unsafe_allow_html=True)
        fig_alloc = go.Figure(go.Bar(x=dept_theo["Allocated Cost (THB)"], y=dept_theo["Department"], orientation="h",
            marker=dict(color=dept_theo["Allocated Cost (THB)"], colorscale="Tealgrn"), text=[fmt_thb(v) for v in dept_theo["Allocated Cost (THB)"]], textposition="outside"))
        fig_alloc.update_layout(height=340, margin=dict(t=10, b=10, l=10, r=40), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_alloc, use_container_width=True)

def page_data_entry():
    st.markdown("## 📝 Data Entry & Monthly Setup")
    st.caption("Configure the current billing cycle month, utility readings, and machine operating hours.")
    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Billing Period & Actual Bill Readings</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.text_input("Billing Month (YYYY-MM)", key="billing_month")
    with m2:
        st.number_input("Actual Peak kWh", min_value=0.0, step=100.0, key="actual_peak_kwh")
    with m3:
        st.number_input("Actual Off-Peak kWh", min_value=0.0, step=100.0, key="actual_offpeak_kwh")
    with m4:
        st.number_input("Total Solar Generation (kWh)", min_value=0.0, step=100.0, key="solar_kwh")

    st.write("")
    st.markdown('<div class="section-title">Machine Operating Hours by Department</div>', unsafe_allow_html=True)
    for dept in list(st.session_state.departments.keys()):
        df = st.session_state.departments[dept]
        with st.expander(f"🏭 {dept}", expanded=False):
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"editor_{dept}",
                column_config={
                    "Machine Name": st.column_config.TextColumn("Machine Name", required=True),
                    "Quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1),
                    "kW": st.column_config.NumberColumn("kW (per unit)", min_value=0.0, step=0.1),
                    "Peak Hours/day": st.column_config.NumberColumn("Peak Hours/day", min_value=0.0, max_value=24.0, step=0.5),
                    "Off-Peak Hours/day": st.column_config.NumberColumn("Off-Peak Hours/day", min_value=0.0, max_value=24.0, step=0.5),
                })
            st.session_state.departments[dept] = edited_df

def page_settings():
    st.markdown("## ⚙️ Settings & Rate Configurations")
    st.markdown("<hr/>", unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1: st.number_input("Peak Rate (THB/kWh)", min_value=0.0, step=0.01, format="%.4f", key="peak_rate")
    with r2: st.number_input("Off-Peak Rate (THB/kWh)", min_value=0.0, step=0.01, format="%.4f", key="offpeak_rate")
    with r3: st.number_input("Ft Rate (THB/kWh)", min_value=-5.0, step=0.001, format="%.4f", key="ft_rate")
    with r4: st.number_input("Monthly Service Charge (THB)", min_value=0.0, step=1.0, key="service_charge")
    st.number_input("Billing Days in Month", min_value=1, max_value=31, step=1, key="billing_days")

    st.write("")
    st.markdown("### 🗄️ Manage Archived History Records")
    history = load_history()
    if history:
        hist_df = pd.DataFrame(history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear All History Data", type="secondary"):
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            st.success("History records cleared.")
            st.rerun()
    else:
        st.info("No archived history records found yet. Click 'Save Current Month to History' on the Dashboard.")

# =====================================================================================
# MAIN APP
# =====================================================================================
def main():
    inject_css()
    init_session_state()

    with st.sidebar:
        st.markdown("## 🍄 MycoFactory")
        st.caption("Energy & Cost Management System")
        st.markdown("---")
        page = st.radio("Navigate", options=["📊 Dashboard", "📝 Data Entry", "⚙️ Settings"], label_visibility="collapsed")
        st.markdown("---")
        st.caption(f"Active Month: **{st.session_state.billing_month}**")
        st.caption(f"Archived Records: **{len(load_history())} months**")

    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "📝 Data Entry":
        page_data_entry()
    elif page == "⚙️ Settings":
        page_settings()

if __name__ == "__main__":
    main()
