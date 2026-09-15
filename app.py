"""
=====================================================================================
  🍄  FACTORY ENERGY & COST MANAGEMENT DASHBOARD (Multi-Month & PM1/PM2/All Split)
  A world-class Streamlit + Plotly dashboard for an industrial mushroom cultivation
  factory with high-contrast UI, sharp tables, and selectable PM1/PM2 views.
=====================================================================================
  Run with:  streamlit run app.py
=====================================================================================
"""

import io
import json
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =====================================================================================
# PAGE CONFIGURATION
# =====================================================================================
st.set_page_config(
    page_title="Factory Energy & Cost Dashboard",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================================================
# GLOBAL CONSTANTS & JSON PERSISTENCE CONFIG
# =====================================================================================
CONFIG_FILE = "departments_config.json"

DEFAULT_DEPARTMENTS = [
    "หน้านอก PM1",
    "หน้านอก PM2",
    "หน้าใน PM1",
    "หน้าใน PM2",
    "G Control PM1",
    "G Control PM2",
    "หลัง PM1",
    "หลัง PM2",
    "Warehouse PM1",
    "Warehouse PM2",
]

# High Contrast Grafana-inspired Dark Palette (Sharp & Clear Text)
BG_APP = "#0B0D10"
BG_PANEL = "#16191D"
BG_PANEL_ALT = "#1E2228"
BORDER = "#30363D"
TEXT_PRIMARY = "#F0F3F6"  # Bright white for maximum crispness
TEXT_MUTED = "#919EAB"  # Clear secondary text

GREEN = "#56D364"
BLUE = "#58A6FF"
ORANGE = "#FFA657"
RED = "#FF7B72"
PURPLE = "#D2A8FF"
YELLOW = "#E3B341"
TEAL = "#39C5CF"

COLOR_PALETTE = [BLUE, GREEN, ORANGE, RED, PURPLE, YELLOW, TEAL, "#79C0FF"]
MACHINE_COLUMNS = [
    "Machine Name",
    "Quantity",
    "kW",
    "Peak Hours/day",
    "Off-Peak Hours/day",
]
VAT_RATE = 0.07


# =====================================================================================
# PERSISTENT CONFIG FUNCTIONS
# =====================================================================================
def load_persistent_config():
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        depts = data.get("departments", DEFAULT_DEPARTMENTS)
        raw_mach = data.get("machines", {})
        departments_dict = {}
        for dept in depts:
          if dept in raw_mach and isinstance(raw_mach[dept], list):
            departments_dict[dept] = pd.DataFrame(raw_mach[dept])
          else:
            default_list = [
                {
                    "Machine Name": f"เครื่องที่ {i}",
                    "Quantity": 1,
                    "kW": 5.0,
                    "Peak Hours/day": 8.0,
                    "Off-Peak Hours/day": 16.0,
                }
                for i in range(1, 9)
            ]
            departments_dict[dept] = pd.DataFrame(default_list)
        return depts, departments_dict
    except Exception:
      pass

  depts = DEFAULT_DEPARTMENTS
  departments_dict = {}
  for dept in depts:
    default_list = [
        {
            "Machine Name": f"เครื่องที่ {i}",
            "Quantity": 1,
            "kW": 5.0,
            "Peak Hours/day": 8.0,
            "Off-Peak Hours/day": 16.0,
        }
        for i in range(1, 9)
    ]
    departments_dict[dept] = pd.DataFrame(default_list)

  save_persistent_config(depts, departments_dict)
  return depts, departments_dict


def save_persistent_config(depts, departments_dict):
  raw_mach = {}
  for dept, df in departments_dict.items():
    if df is not None and not df.empty:
      raw_mach[dept] = df.to_dict(orient="records")
    else:
      raw_mach[dept] = []
  data = {"departments": depts, "machines": raw_mach}
  with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# =====================================================================================
# TRANSLATIONS
# =====================================================================================
LANG = {
    "en": {
        "brand_title": "🍄 MycoFactory",
        "brand_caption": "Energy & Cost Management",
        "nav_dashboard": "📊 Dashboard",
        "nav_data_entry": "📝 Data Entry & Excel",
        "nav_settings": "⚙️ Settings",
        "billing_cycle": "Billing cycle",
        "days": "days",
        "departments_tracked": "Departments tracked",
        "footer": "v2.2 · High Contrast UI",
        "dash_title": "📊 Factory Energy & Cost Dashboard",
        "dash_caption": (
            "Monitor utility consumption, bills, and plant-specific cost"
            " allocations."
        ),
        "select_dash_month": "📅 Select Month",
        "select_factory_view": "🏭 Select Factory View",
        "view_all": "🌐 Combined (All Factory)",
        "view_pm1": "🏢 PM1 Only",
        "view_pm2": "🏢 PM2 Only",
        "kpi_total_cost": "TOTAL NET COST (SELECTED VIEW)",
        "kpi_vs_last_month": "VS. PREVIOUS MONTH",
        "kpi_vs_avg": "VS. 6-MONTH AVERAGE",
        "ref_none": "— no comparison data —",
        "vs_ref": "vs. reference",
        "chip_net_peak": "Net Peak kWh (billed)",
        "chip_net_offpeak": "Net Off-Peak kWh (billed)",
        "chip_solar": "Solar Offset Used",
        "chip_theoretical": "Theoretical Machine Usage",
        "section_energy_share": "Energy Consumption Share by Department",
        "section_peak_offpeak": "Peak vs. Off-Peak Usage by Department",
        "no_machine_data": "No machine data available for this view.",
        "kwh_total": "kWh Total",
        "peak_kwh_legend": "Peak kWh",
        "offpeak_kwh_legend": "Off-Peak kWh",
        "yaxis_kwh_month": "kWh / month",
        "section_cost_allocation": "💰 Cost Allocation by Department",
        "section_cost_allocation_caption": (
            "Utility expenses distributed proportionally based on theoretical"
            " machine energy consumption."
        ),
        "col_department": "Department",
        "col_theoretical_kwh": "Theoretical kWh",
        "col_share_pct": "Share %",
        "col_allocated_cost": "Allocated Cost",
        "xaxis_allocated_cost": "Allocated Cost (THB)",
        "expander_bill_breakdown": "🧾 View Full Factory Bill Breakdown",
        "bill_energy_cost": "Energy Cost",
        "bill_ft_cost": "Ft Cost",
        "bill_service_charge": "Service Charge",
        "bill_vat": "VAT (7%)",
        "bill_grand_total": "Grand Total",
        "data_entry_title": "📝 Data Entry & Excel Sync",
        "data_entry_caption": (
            "Download template, fill multi-month history, and upload back, or"
            " edit tables directly."
        ),
        "section_excel_title": "📥 Excel Template & File Synchronization",
        "btn_download_template": "Download Excel Template",
        "upload_excel_label": "Upload Filled Excel File (.xlsx)",
        "success_upload": "Successfully imported data from Excel!",
        "section_history_title": "📅 Monthly Energy & Cost History",
        "section_history_caption": (
            "Manage utility bills and solar generation across multiple"
            " months."
        ),
        "section_machines_title": (
            "🏭 Machine Working Hours by Department (Direct Editor)"
        ),
        "monthly_theoretical": "kWh / month (theoretical)",
        "col_machine_name": "Machine Name",
        "col_qty": "Quantity",
        "col_kw": "kW (per unit)",
        "col_peak_hours": "Peak Hours/day",
        "col_offpeak_hours": "Off-Peak Hours/day",
        "settings_title": "⚙️ Settings & Departments",
        "settings_caption": (
            "Configure electricity rates, billing days, add/remove departments"
            " freely."
        ),
        "section_rates": "Rate Configurations",
        "label_peak_rate": "Peak Rate (THB/kWh)",
        "label_offpeak_rate": "Off-Peak Rate (THB/kWh)",
        "label_ft_rate": "Ft Rate (THB/kWh)",
        "label_service_charge": "Monthly Service Charge (THB)",
        "label_billing_days": "Billing Days in Month",
        "section_dept_mgmt": "Department Customization Management",
        "add_dept_label": "➕ Add New Department",
        "add_dept_input_label": "New Department Name",
        "add_dept_placeholder": "e.g. G Control PM3",
        "add_dept_button": "Add Department",
        "warn_empty_name": "Please enter a department name.",
        "warn_dept_exists": "Department '{name}' already exists.",
        "success_dept_added": "Department '{name}' added successfully.",
        "delete_dept_label": "🗑️ Delete Department",
        "delete_dept_select": "Select Department to Delete",
        "delete_dept_button": "Delete Department",
        "success_dept_deleted": "Department '{name}' deleted successfully.",
        "info_no_departments": "No departments available.",
    },
    "th": {
        "brand_title": "🍄 โรงงานเห็ด",
        "brand_caption": "ระบบบริหารจัดการพลังงาน",
        "nav_dashboard": "📊 แดชบอร์ด",
        "nav_data_entry": "📝 บันทึกข้อมูล & Excel",
        "nav_settings": "⚙️ ตั้งค่าแผนกและระบบ",
        "billing_cycle": "รอบบิล",
        "days": "วัน",
        "departments_tracked": "แผนกที่ติดตาม",
        "footer": "v2.2 · ตัวหนังสือคมชัดสูง",
        "dash_title": "📊 แดชบอร์ดพลังงานและต้นทุนโรงงาน",
        "dash_caption": (
            "ติดตามการใช้พลังงาน ค่าไฟ และการจัดสรรต้นทุนแยกตามโรงงาน (PM1 / PM2)"
        ),
        "select_dash_month": "📅 เลือกเดือนที่แสดงผล",
        "select_factory_view": "🏭 เลือกระบบโรงงานที่ต้องการดู",
        "view_all": "🌐 รวมทั้งโรงงาน (All Factory)",
        "view_pm1": "🏢 เฉพาะโรงงาน PM1",
        "view_pm2": "🏢 เฉพาะโรงงาน PM2",
        "kpi_total_cost": "ต้นทุนสุทธิรวม (มุมมองที่เลือก)",
        "kpi_vs_last_month": "เทียบกับเดือนก่อนหน้า",
        "kpi_vs_avg": "เทียบกับค่าเฉลี่ย 6 เดือน",
        "ref_none": "— ไม่มีข้อมูลเปรียบเทียบ —",
        "vs_ref": "เทียบกับอ้างอิง",
        "chip_net_peak": "หน่วย Peak สุทธิ (คิดเงิน)",
        "chip_net_offpeak": "หน่วย Off-Peak สุทธิ (คิดเงิน)",
        "chip_solar": "พลังงานโซลาร์ที่หักลบ",
        "chip_theoretical": "การใช้พลังงานตามทฤษฎีเครื่องจักร",
        "section_energy_share": "สัดส่วนการใช้พลังงานแยกตามแผนก",
        "section_peak_offpeak": "การใช้พลังงาน Peak เทียบ Off-Peak แยกตามแผนก",
        "no_machine_data": "ยังไม่มีข้อมูลเครื่องจักรในมุมมองนี้",
        "kwh_total": "หน่วยรวม (kWh)",
        "peak_kwh_legend": "Peak (kWh)",
        "offpeak_kwh_legend": "Off-Peak (kWh)",
        "yaxis_kwh_month": "kWh / เดือน",
        "section_cost_allocation": "💰 การจัดสรรต้นทุนค่าไฟแยกตามแผนก",
        "section_cost_allocation_caption": (
            "ค่าไฟโรงงานถูกกระจายสัดส่วนตามการใช้พลังงานตามทฤษฎีของเครื่องจักร"
        ),
        "col_department": "แผนก",
        "col_theoretical_kwh": "kWh ตามทฤษฎี",
        "col_share_pct": "สัดส่วน %",
        "col_allocated_cost": "ต้นทุนที่จัดสรร",
        "xaxis_allocated_cost": "ต้นทุนที่จัดสรร (บาท)",
        "expander_bill_breakdown": "🧾 ดูรายละเอียดบิลค่าไฟภาพรวมโรงงาน",
        "bill_energy_cost": "ค่าพลังงาน",
        "bill_ft_cost": "ค่า Ft",
        "bill_service_charge": "ค่าบริการรายเดือน",
        "bill_vat": "ภาษีมูลค่าเพิ่ม (7%)",
        "bill_grand_total": "ยอดรวมทั้งหมด",
        "data_entry_title": "📝 บันทึกข้อมูลและซิงค์ Excel",
        "data_entry_caption": (
            "ดาวน์โหลดเทมเพลต Excel ไปกรอกข้อมูลหลายเดือนและเครื่องจักร"
            " แล้วอัพโหลดกลับเข้ามา หรือแก้ไขในตารางด้านล่างได้ทันที"
        ),
        "section_excel_title": "📥 ดาวน์โหลดเทมเพลตและอัพโหลดไฟล์ Excel",
        "btn_download_template": "ดาวน์โหลดเทมเพลต Excel",
        "upload_excel_label": "อัพโหลดไฟล์ Excel ที่กรอกข้อมูลแล้ว (.xlsx)",
        "success_upload": "นำเข้าข้อมูลจากไฟล์ Excel สำเร็จแล้ว!",
        "section_history_title": "📅 ประวัติข้อมูลพลังงานและค่าใช้จ่ายรายเดือน",
        "section_history_caption": (
            "จัดการข้อมูลบิลค่าไฟและโซลาร์เซลล์ย้อนหลังหลายเดือน"
        ),
        "section_machines_title": (
            "🏭 ชั่วโมงการทำงานของเครื่องจักรแยกตามแผนก (แก้ไขในเว็บ)"
        ),
        "monthly_theoretical": "kWh / เดือน (ตามทฤษฎี)",
        "col_machine_name": "ชื่อเครื่องจักร",
        "col_qty": "จำนวน",
        "col_kw": "kW (ต่อเครื่อง)",
        "col_peak_hours": "ชม. Peak/วัน",
        "col_offpeak_hours": "ชม. Off-Peak/วัน",
        "settings_title": "⚙️ ตั้งค่าแผนกและระบบ",
        "settings_caption": (
            "ตั้งค่าอัตราค่าไฟฟ้า จำนวนวันในรอบบิล และเพิ่ม/ลบแผนกได้อย่างอิสระ"
        ),
        "section_rates": "การตั้งค่าอัตราค่าไฟ",
        "label_peak_rate": "อัตรา Peak (บาท/kWh)",
        "label_offpeak_rate": "อัตรา Off-Peak (บาท/kWh)",
        "label_ft_rate": "อัตราค่า Ft (บาท/kWh)",
        "label_service_charge": "ค่าบริการรายเดือน (บาท)",
        "label_billing_days": "จำนวนวันในรอบบิล",
        "section_dept_mgmt": "จัดการแผนกอิสระ (เพิ่ม/ลบ แผนก)",
        "add_dept_label": "➕ เพิ่มแผนกใหม่",
        "add_dept_input_label": "ชื่อแผนกใหม่",
        "add_dept_placeholder": "เช่น G Control PM3",
        "add_dept_button": "เพิ่มแผนก",
        "warn_empty_name": "กรุณากรอกชื่อแผนก",
        "warn_dept_exists": "แผนก '{name}' มีอยู่แล้วในระบบ",
        "success_dept_added": "เพิ่มแผนก '{name}' เรียบร้อยแล้ว",
        "delete_dept_label": "🗑️ ลบแผนกที่ไม่ต้องการ",
        "delete_dept_select": "เลือกแผนกที่ต้องการลบ",
        "delete_dept_button": "ลบแผนกนี้",
        "success_dept_deleted": "ลบแผนก '{name}' เรียบร้อยแล้ว",
        "info_no_departments": "ไม่มีแผนกในระบบ",
    },
}


def t(key: str, **kwargs) -> str:
  text = LANG[st.session_state.lang].get(key, key)
  return text.format(**kwargs) if kwargs else text


# =====================================================================================
# CUSTOM CSS — HIGH CONTRAST & SHARP UI (Fixed Dropdowns & Tables)
# =====================================================================================
def inject_css():
  st.markdown(
      f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {TEXT_PRIMARY};
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        .stApp {{
            background-color: {BG_APP};
        }}
        .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 3rem;
        }}

        /* Typography Sharpness */
        h1, h2, h3, h4, h5, h6 {{
            color: {TEXT_PRIMARY} !important;
            font-weight: 700 !important;
        }}
        p, span, label, div {{
            color: {TEXT_PRIMARY};
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {TEXT_MUTED} !important;
            font-size: 0.85rem;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B0D10 0%, #14171B 100%);
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT_PRIMARY} !important;
        }}

        /* SECTION TITLES */
        .section-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-top: 0.4rem;
            margin-bottom: 0.8rem;
            border-left: 4px solid {BLUE};
            padding-left: 10px;
            letter-spacing: 0.01em;
        }}

        /* KPI CARDS */
        .kpi-card {{
            background: {BG_PANEL};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 18px 20px;
            height: 100%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .kpi-title {{
            font-size: 0.75rem;
            font-weight: 700;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }}
        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.1rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-bottom: 6px;
        }}
        .kpi-sub {{ font-size: 0.85rem; font-weight: 600; }}
        .kpi-up {{ color: {RED}; }}
        .kpi-down {{ color: {GREEN}; }}
        .kpi-flat {{ color: {TEXT_MUTED}; }}
        .kpi-primary-value {{ color: {GREEN}; }}

        /* CHIPS */
        .chip-card {{
            background: {BG_PANEL_ALT};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 12px 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .chip-label {{
            font-size: 0.7rem; color: {TEXT_MUTED}; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.06em;
        }}
        .chip-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.2rem; color: {TEXT_PRIMARY}; font-weight: 700; margin-top: 4px;
        }}

        .chart-panel {{
            background: {BG_PANEL};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}

        /* DROPDOWNS & INPUTS HIGH CONTRAST FIX */
        .stTextInput input, .stNumberInput input {{
            background-color: {BG_PANEL_ALT} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 6px !important;
            font-weight: 600;
        }}

        /* Streamlit Selectbox Fix (High Contrast Text & Background) */
        div[data-baseweb="select"] > div {{
            background-color: {BG_PANEL_ALT} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 6px !important;
        }}
        div[data-baseweb="select"] span {{
            color: {TEXT_PRIMARY} !important;
            font-weight: 600 !important;
        }}
        div[data-baseweb="popover"] div, div[role="listbox"] div {{
            background-color: {BG_PANEL_ALT} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        div[role="option"] {{
            background-color: {BG_PANEL_ALT} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        div[role="option"]:hover {{
            background-color: {BORDER} !important;
            color: {TEXT_PRIMARY} !important;
        }}

        /* BUTTONS */
        .stButton > button {{
            border-radius: 6px;
            font-weight: 600;
            border: 1px solid {BORDER};
            background-color: {BG_PANEL_ALT};
            color: {TEXT_PRIMARY};
        }}
        .stButton > button:hover {{
            border-color: {BLUE};
            color: {BLUE};
        }}

        /* DATAFRAMES / TABLES SHARPNESS */
        [data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid {BORDER};
            background-color: {BG_PANEL};
        }}
        table {{
            color: {TEXT_PRIMARY} !important;
        }}

        details {{
            background: {BG_PANEL};
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
        }}

        hr {{ border-color: {BORDER}; margin: 0.8rem 0 1.4rem 0; }}
    </style>
    """,
      unsafe_allow_html=True,
  )


PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG_PANEL,
    plot_bgcolor=BG_PANEL,
    font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY, size=12),
)


# =====================================================================================
# INITIALIZE SESSION STATE
# =====================================================================================
def init_session_state():
  defaults = {
      "peak_rate": 4.50,
      "offpeak_rate": 2.80,
      "ft_rate": 0.2000,
      "service_charge": 312.24,
      "billing_days": 30,
      "lang": "th",  # Default Thai language for convenience
  }
  for k, v in defaults.items():
    if k not in st.session_state:
      st.session_state[k] = v

  if "departments_list" not in st.session_state or "departments" not in st.session_state:
    depts, depts_dict = load_persistent_config()
    st.session_state.departments_list = depts
    st.session_state.departments = depts_dict

  if "monthly_history" not in st.session_state:
    st.session_state.monthly_history = pd.DataFrame([
        {
            "Month": "2025-11",
            "Actual Peak kWh": 49000.0,
            "Actual Off-Peak kWh": 78000.0,
            "Solar kWh": 14000.0,
        },
        {
            "Month": "2025-12",
            "Actual Peak kWh": 51000.0,
            "Actual Off-Peak kWh": 80000.0,
            "Solar kWh": 14500.0,
        },
        {
            "Month": "2026-01",
            "Actual Peak kWh": 50000.0,
            "Actual Off-Peak kWh": 79000.0,
            "Solar kWh": 15000.0,
        },
        {
            "Month": "2026-02",
            "Actual Peak kWh": 48000.0,
            "Actual Off-Peak kWh": 77000.0,
            "Solar kWh": 15500.0,
        },
        {
            "Month": "2026-03",
            "Actual Peak kWh": 53000.0,
            "Actual Off-Peak kWh": 82000.0,
            "Solar kWh": 14800.0,
        },
        {
            "Month": "2026-04",
            "Actual Peak kWh": 54000.0,
            "Actual Off-Peak kWh": 83000.0,
            "Solar kWh": 16000.0,
        },
        {
            "Month": "2026-05",
            "Actual Peak kWh": 52500.0,
            "Actual Off-Peak kWh": 81500.0,
            "Solar kWh": 15200.0,
        },
        {
            "Month": "2026-06",
            "Actual Peak kWh": 51500.0,
            "Actual Off-Peak kWh": 80500.0,
            "Solar kWh": 15000.0,
        },
        {
            "Month": "2026-07",
            "Actual Peak kWh": 52000.0,
            "Actual Off-Peak kWh": 81000.0,
            "Solar kWh": 15000.0,
        },
        {
            "Month": "2026-08",
            "Actual Peak kWh": 52000.0,
            "Actual Off-Peak kWh": 81000.0,
            "Solar kWh": 15000.0,
        },
    ])


# =====================================================================================
# EXCEL ENGINE
# =====================================================================================
def create_excel_template() -> bytes:
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    history_df = st.session_state.monthly_history.copy()
    history_df.to_excel(writer, sheet_name="Monthly_History", index=False)

    all_machines = []
    for dept in st.session_state.departments_list:
      if dept in st.session_state.departments:
        df = st.session_state.departments[dept]
        if not df.empty:
          temp_df = df.copy()
          temp_df.insert(0, "Department", dept)
          all_machines.append(temp_df)
    if all_machines:
      combined_machines = pd.concat(all_machines, ignore_index=True)
    else:
      combined_machines = pd.DataFrame(columns=["Department"] + MACHINE_COLUMNS)
    combined_machines.to_excel(writer, sheet_name="Machines", index=False)

  output.seek(0)
  return output.getvalue()


def process_uploaded_excel(uploaded_file):
  try:
    xls = pd.ExcelFile(uploaded_file)
    if "Monthly_History" in xls.sheet_names:
      hist_df = pd.read_excel(xls, sheet_name="Monthly_History")
      required_cols = [
          "Month",
          "Actual Peak kWh",
          "Actual Off-Peak kWh",
          "Solar kWh",
      ]
      if all(col in hist_df.columns for col in required_cols):
        st.session_state.monthly_history = hist_df[required_cols]

    if "Machines" in xls.sheet_names:
      mach_df = pd.read_excel(xls, sheet_name="Machines")
      required_mach_cols = ["Department"] + MACHINE_COLUMNS
      if all(col in mach_df.columns for col in required_mach_cols):
        new_depts_list = mach_df["Department"].unique().tolist()
        new_depts_dict = {}
        for dept, group in mach_df.groupby("Department"):
          clean_group = group.drop(columns=["Department"]).reset_index(
              drop=True
          )
          new_depts_dict[str(dept)] = clean_group
        st.session_state.departments_list = new_depts_list
        st.session_state.departments = new_depts_dict
        save_persistent_config(new_depts_list, new_depts_dict)
    return True
  except Exception as e:
    st.error(f"Error processing file: {e}")
    return False


# =====================================================================================
# CALCULATIONS
# =====================================================================================
def compute_department_theoretical_kwh(departments, depts_list, billing_days):
  rows = []
  for dept in depts_list:
    df = departments.get(dept, pd.DataFrame())
    if df is None or df.empty:
      peak_kwh, offpeak_kwh = 0.0, 0.0
    else:
      d = df.fillna(0)
      peak_kwh = (
          (d["Quantity"] * d["kW"] * d["Peak Hours/day"]).sum() * billing_days
      )
      offpeak_kwh = (
          (d["Quantity"] * d["kW"] * d["Off-Peak Hours/day"]).sum()
          * billing_days
      )
    rows.append({
        "Department": dept,
        "Peak kWh": peak_kwh,
        "Off-Peak kWh": offpeak_kwh,
        "Total kWh": peak_kwh + offpeak_kwh,
    })
  return pd.DataFrame(rows)


def compute_net_bill(actual_peak, actual_offpeak, solar):
  net_peak = max(actual_peak - solar, 0.0)
  remaining_solar = max(solar - actual_peak, 0.0)
  net_offpeak = max(actual_offpeak - remaining_solar, 0.0)
  solar_used_on_peak = min(solar, actual_peak)
  solar_used_on_offpeak = min(remaining_solar, actual_offpeak)
  return net_peak, net_offpeak, solar_used_on_peak, solar_used_on_offpeak


def compute_total_cost(
    net_peak,
    net_offpeak,
    peak_rate,
    offpeak_rate,
    ft_rate,
    service_charge,
):
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
  df = dept_theoretical.copy()
  total_theoretical = df["Total kWh"].sum()
  if total_theoretical > 0:
    df["Share %"] = df["Total kWh"] / total_theoretical * 100
  else:
    df["Share %"] = 100 / len(df) if len(df) > 0 else 0
  df["Allocated Cost (THB)"] = df["Share %"] / 100 * grand_total
  return df


# =====================================================================================
# UI HELPERS
# =====================================================================================
def fmt_thb(value):
  return f"฿{value:,.2f}"


def fmt_kwh(value):
  return f"{value:,.0f} kWh"


def kpi_card(title, value_str, delta_val, delta_pct, primary=False):
  if delta_val is None:
    sub_html = f'<div class="kpi-sub kpi-flat">{t("ref_none")}</div>'
  else:
    is_increase = delta_val > 0
    css_class = (
        "kpi-up" if is_increase else ("kpi-down" if delta_val < 0 else "kpi-flat")
    )
    arrow = "▲" if is_increase else ("▼" if delta_val < 0 else "■")
    sub_html = (
        f'<div class="kpi-sub {css_class}">{arrow}'
        f" {fmt_thb(abs(delta_val))} ({delta_pct:+.1f}%)"
        f' {t("vs_ref")}</div>'
    )

  val_class = "kpi-primary-value" if primary else "kpi-value"
  st.markdown(
      f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="{val_class}" style="font-family:'JetBrains Mono', monospace; font-size: 2.1rem; font-weight:700; margin-bottom: 6px;">{value_str}</div>
            {sub_html}
        </div>
    """,
      unsafe_allow_html=True,
  )


def chip_metric(label, value):
  st.markdown(
      f"""
        <div class="chip-card">
            <div class="chip-label">{label}</div>
            <div class="chip-value">{value}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )


# =====================================================================================
# PAGE 1 — DASHBOARD (With PM1 / PM2 / All Split View)
# =====================================================================================
def page_dashboard():
  st.markdown(f"## {t('dash_title')}")
  st.caption(t("dash_caption"))
  st.markdown("<hr/>", unsafe_allow_html=True)

  history_df = st.session_state.monthly_history
  if history_df.empty:
    st.warning("No monthly history data available.")
    return

  months_list = history_df["Month"].tolist()
  default_index = len(months_list) - 1 if months_list else 0

  # Controls for Month & Factory View Selection
  col_sel1, col_sel2 = st.columns([1, 1])
  with col_sel1:
    selected_month = st.selectbox(
        t("select_dash_month"), options=months_list, index=default_index
    )
  with col_sel2:
    factory_view = st.selectbox(
        t("select_factory_view"),
        options=[t("view_all"), t("view_pm1"), t("view_pm2")],
    )

  # Filter departments based on selection
  all_depts_list = st.session_state.departments_list
  if factory_view == t("view_pm1"):
    filtered_depts = [d for d in all_depts_list if "PM1" in d.upper()]
  elif factory_view == t("view_pm2"):
    filtered_depts = [d for d in all_depts_list if "PM2" in d.upper()]
  else:
    filtered_depts = all_depts_list

  billing_days = int(st.session_state.billing_days)
  dept_theo_all = compute_department_theoretical_kwh(
      st.session_state.departments, all_depts_list, billing_days
  )
  dept_theo_filtered = compute_department_theoretical_kwh(
      st.session_state.departments, filtered_depts, billing_days
  )

  # Total factory theoretical vs filtered theoretical for cost scaling
  total_factory_theo_kwh = dept_theo_all["Total kWh"].sum()
  filtered_theo_kwh = dept_theo_filtered["Total kWh"].sum()

  view_ratio = (
      (filtered_theo_kwh / total_factory_theo_kwh)
      if total_factory_theo_kwh > 0
      else 1.0
  )

  row_data = history_df[history_df["Month"] == selected_month].iloc[0]

  # Compute full factory bill
  net_peak, net_offpeak, solar_peak, solar_offpeak = compute_net_bill(
      row_data["Actual Peak kWh"],
      row_data["Actual Off-Peak kWh"],
      row_data["Solar kWh"],
  )
  full_cost = compute_total_cost(
      net_peak,
      net_offpeak,
      st.session_state.peak_rate,
      st.session_state.offpeak_rate,
      st.session_state.ft_rate,
      st.session_state.service_charge,
  )

  # Apply ratio if viewing PM1 or PM2 specifically
  grand_total = full_cost["grand_total"] * view_ratio
  view_net_peak = net_peak * view_ratio
  view_net_offpeak = net_offpeak * view_ratio
  view_solar = (solar_peak + solar_offpeak) * view_ratio

  allocation = allocate_cost(dept_theo_filtered, grand_total)

  # Last month comparison
  sel_idx = months_list.index(selected_month)
  last_month_cost = None
  if sel_idx > 0:
    prev_row = history_df[history_df["Month"] == months_list[sel_idx - 1]].iloc[0]
    p_peak, p_off, _, _ = compute_net_bill(
        prev_row["Actual Peak kWh"],
        prev_row["Actual Off-Peak kWh"],
        prev_row["Solar kWh"],
    )
    p_cost = compute_total_cost(
        p_peak,
        p_off,
        st.session_state.peak_rate,
        st.session_state.offpeak_rate,
        st.session_state.ft_rate,
        st.session_state.service_charge,
    )
    last_month_cost = p_cost["grand_total"] * view_ratio

  delta_vs_last = grand_total - last_month_cost if last_month_cost else None
  pct_vs_last = (delta_vs_last / last_month_cost * 100) if last_month_cost else 0

  # 6-Month Average
  all_costs = []
  for _, r in history_df.iterrows():
    r_peak, r_off, _, _ = compute_net_bill(
        r["Actual Peak kWh"], r["Actual Off-Peak kWh"], r["Solar kWh"]
    )
    r_c = compute_total_cost(
        r_peak,
        r_off,
        st.session_state.peak_rate,
        st.session_state.offpeak_rate,
        st.session_state.ft_rate,
        st.session_state.service_charge,
    )
    all_costs.append(r_c["grand_total"] * view_ratio)
  six_avg = (
      sum(all_costs[-6:]) / min(len(all_costs), 6) if all_costs else grand_total
  )

  delta_vs_avg = grand_total - six_avg
  pct_vs_avg = (delta_vs_avg / six_avg * 100) if six_avg > 0 else 0

  # KPIs
  c1, c2, c3 = st.columns(3)
  with c1:
    kpi_card(
        t("kpi_total_cost"), fmt_thb(grand_total), None, None, primary=True
    )
  with c2:
    kpi_card(
        t("kpi_vs_last_month"),
        fmt_thb(last_month_cost) if last_month_cost else t("ref_none"),
        delta_vs_last,
        pct_vs_last,
    )
  with c3:
    kpi_card(t("kpi_vs_avg"), fmt_thb(six_avg), delta_vs_avg, pct_vs_avg)

  st.write("")

  s1, s2, s3, s4 = st.columns(4)
  with s1:
    chip_metric(t("chip_net_peak"), fmt_kwh(view_net_peak))
  with s2:
    chip_metric(t("chip_net_offpeak"), fmt_kwh(view_net_offpeak))
  with s3:
    chip_metric(t("chip_solar"), fmt_kwh(view_solar))
  with s4:
    chip_metric(t("chip_theoretical"), fmt_kwh(filtered_theo_kwh))

  st.write("")
  st.write("")

  col_left, col_right = st.columns([1, 1.2])

  with col_left:
    st.markdown(
        f'<div class="section-title">{t("section_energy_share")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    if filtered_theo_kwh > 0:
      fig_donut = go.Figure(
          data=[
              go.Pie(
                  labels=dept_theo_filtered["Department"],
                  values=dept_theo_filtered["Total kWh"],
                  hole=0.58,
                  marker=dict(
                      colors=COLOR_PALETTE, line=dict(color=BG_PANEL, width=2)
                  ),
                  textinfo="percent",
                  textfont=dict(size=13, color=TEXT_PRIMARY, weight="bold"),
                  hovertemplate=(
                      "<b>%{label}</b><br>%{value:,.0f}"
                      " kWh<br>%{percent}<extra></extra>"
                  ),
              )
          ]
      )
      fig_donut.update_layout(
          **PLOTLY_LAYOUT,
          showlegend=True,
          legend=dict(
              orientation="v",
              yanchor="middle",
              y=0.5,
              xanchor="left",
              x=1.02,
              font=dict(size=11, color=TEXT_PRIMARY),
          ),
          annotations=[
              dict(
                  text=(
                      f"{filtered_theo_kwh:,.0f}<br>{t('kwh_total')}"
                  ),
                  x=0.5,
                  y=0.5,
                  font_size=14,
                  showarrow=False,
                  font=dict(color=TEXT_PRIMARY, weight="bold"),
              )
          ],
          margin=dict(t=10, b=10, l=10, r=10),
          height=380,
      )
      st.plotly_chart(fig_donut, use_container_width=True)
    else:
      st.info(t("no_machine_data"))
    st.markdown("</div>", unsafe_allow_html=True)

  with col_right:
    st.markdown(
        f'<div class="section-title">{t("section_peak_offpeak")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    if filtered_theo_kwh > 0:
      fig_bar = go.Figure()
      fig_bar.add_trace(
          go.Bar(
              name=t("peak_kwh_legend"),
              x=dept_theo_filtered["Department"],
              y=dept_theo_filtered["Peak kWh"],
              marker_color=RED,
              hovertemplate=(
                  "<b>%{x}</b><br>"
                  + t("peak_kwh_legend")
                  + ": %{y:,.0f}<extra></extra>"
              ),
          )
      )
      fig_bar.add_trace(
          go.Bar(
              name=t("offpeak_kwh_legend"),
              x=dept_theo_filtered["Department"],
              y=dept_theo_filtered["Off-Peak kWh"],
              marker_color=BLUE,
              hovertemplate=(
                  "<b>%{x}</b><br>"
                  + t("offpeak_kwh_legend")
                  + ": %{y:,.0f}<extra></extra>"
              ),
          )
      )
      fig_bar.update_layout(
          **PLOTLY_LAYOUT,
          barmode="group",
          height=380,
          margin=dict(t=10, b=10, l=10, r=10),
          legend=dict(
              orientation="h",
              yanchor="bottom",
              y=1.02,
              xanchor="right",
              x=1,
              font=dict(color=TEXT_PRIMARY),
          ),
          yaxis=dict(
              title=t("yaxis_kwh_month"), gridcolor=BORDER, color=TEXT_PRIMARY
          ),
          xaxis=dict(title=None, color=TEXT_PRIMARY),
      )
      st.plotly_chart(fig_bar, use_container_width=True)
    else:
      st.info(t("no_machine_data"))
    st.markdown("</div>", unsafe_allow_html=True)

  st.write("")

  st.markdown(
      f'<div class="section-title">{t("section_cost_allocation")}</div>',
      unsafe_allow_html=True,
  )
  st.caption(t("section_cost_allocation_caption"))

  if filtered_theo_kwh > 0:
    alloc_sorted = allocation.sort_values(
        "Allocated Cost (THB)", ascending=True
    )

    col_chart, col_table = st.columns([1.1, 1])
    with col_chart:
      st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
      fig_alloc = go.Figure(
          go.Bar(
              x=alloc_sorted["Allocated Cost (THB)"],
              y=alloc_sorted["Department"],
              orientation="h",
              marker=dict(
                  color=alloc_sorted["Allocated Cost (THB)"],
                  colorscale=[[0, "#1F5C4F"], [1, GREEN]],
              ),
              text=[fmt_thb(v) for v in alloc_sorted["Allocated Cost (THB)"]],
              textposition="outside",
              textfont=dict(color=TEXT_PRIMARY, weight="bold"),
              hovertemplate="<b>%{y}</b><br>%{x:,.2f} THB<extra></extra>",
          )
      )
      fig_alloc.update_layout(
          **PLOTLY_LAYOUT,
          height=340,
          margin=dict(t=10, b=10, l=10, r=40),
          xaxis=dict(
              title=t("xaxis_allocated_cost"),
              gridcolor=BORDER,
              color=TEXT_PRIMARY,
          ),
          yaxis=dict(color=TEXT_PRIMARY),
      )
      st.plotly_chart(fig_alloc, use_container_width=True)
      st.markdown("</div>", unsafe_allow_html=True)

    with col_table:
      display_df = allocation[
          ["Department", "Total kWh", "Share %", "Allocated Cost (THB)"]
      ].copy()
      display_df = display_df.sort_values(
          "Allocated Cost (THB)", ascending=False
      )
      display_df.columns = [
          t("col_department"),
          t("col_theoretical_kwh"),
          t("col_share_pct"),
          t("col_allocated_cost"),
      ]
      st.dataframe(
          display_df,
          column_config={
              t("col_theoretical_kwh"): st.column_config.NumberColumn(
                  t("col_theoretical_kwh"), format="%.0f"
              ),
              t("col_share_pct"): st.column_config.NumberColumn(
                  t("col_share_pct"), format="%.1f%%"
              ),
              t("col_allocated_cost"): st.column_config.NumberColumn(
                  t("col_allocated_cost"), format="฿%.2f"
              ),
          },
          hide_index=True,
          use_container_width=True,
          height=340,
      )
  else:
    st.info(t("no_machine_data"))

  with st.expander(t("expander_bill_breakdown")):
    b1, b2, b3, b4, b5 = st.columns(5)
    b1.metric(t("bill_energy_cost"), fmt_thb(full_cost["energy_cost"]))
    b2.metric(t("bill_ft_cost"), fmt_thb(full_cost["ft_cost"]))
    b3.metric(t("bill_service_charge"), fmt_thb(full_cost["service_charge"]))
    b4.metric(t("bill_vat"), fmt_thb(full_cost["vat"]))
    b5.metric(t("bill_grand_total"), fmt_thb(full_cost["grand_total"]))


# =====================================================================================
# PAGE 2 — DATA ENTRY & EXCEL SYNC
# =====================================================================================
def page_data_entry():
  st.markdown(f"## {t('data_entry_title')}")
  st.caption(t('data_entry_caption'))
  st.markdown("<hr/>", unsafe_allow_html=True)

  st.markdown(
      f'<div class="section-title">{t("section_excel_title")}</div>',
      unsafe_allow_html=True,
  )
  col_dl, col_ul = st.columns(2)

  with col_dl:
    excel_bytes = create_excel_template()
    st.download_button(
        label=f"📥 {t('btn_download_template')}",
        data=excel_bytes,
        file_name="Factory_Energy_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

  with col_ul:
    uploaded_file = st.file_uploader(t("upload_excel_label"), type=["xlsx"])
    if uploaded_file is not None:
      if process_uploaded_excel(uploaded_file):
        st.success(t("success_upload"))
        st.rerun()

  st.write("")
  st.write("")

  st.markdown(
      f'<div class="section-title">{t("section_history_title")}</div>',
      unsafe_allow_html=True,
  )
  st.caption(t("section_history_caption"))

  edited_history = st.data_editor(
      st.session_state.monthly_history,
      num_rows="dynamic",
      use_container_width=True,
      key="history_editor",
      column_config={
          "Month": st.column_config.TextColumn("Month (YYYY-MM)", required=True),
          "Actual Peak kWh": st.column_config.NumberColumn(
              "Actual Peak kWh", min_value=0.0, step=100.0, format="%.2f"
          ),
          "Actual Off-Peak kWh": st.column_config.NumberColumn(
              "Actual Off-Peak kWh", min_value=0.0, step=100.0, format="%.2f"
          ),
          "Solar kWh": st.column_config.NumberColumn(
              "Solar kWh", min_value=0.0, step=100.0, format="%.2f"
          ),
      },
  )
  st.session_state.monthly_history = edited_history

  st.write("")
  st.write("")

  st.markdown(
      f'<div class="section-title">{t("section_machines_title")}</div>',
      unsafe_allow_html=True,
  )

  for dept in list(st.session_state.departments_list):
    if dept not in st.session_state.departments:
      st.session_state.departments[dept] = pd.DataFrame(columns=MACHINE_COLUMNS)

    df = st.session_state.departments[dept]
    theoretical_kwh = 0.0
    if not df.empty:
      d = df.fillna(0)
      theoretical_kwh = (
          (d["Quantity"] * d["kW"] * d["Peak Hours/day"])
          + (d["Quantity"] * d["kW"] * d["Off-Peak Hours/day"])
      ).sum() * st.session_state.billing_days

    with st.expander(
        f"🏭 {dept}  —  {theoretical_kwh:,.0f} {t('monthly_theoretical')}",
        expanded=False,
    ):
      edited_df = st.data_editor(
          df,
          num_rows="dynamic",
          use_container_width=True,
          key=f"editor_{dept}",
          column_config={
              "Machine Name": st.column_config.TextColumn(
                  t("col_machine_name"), required=True
              ),
              "Quantity": st.column_config.NumberColumn(
                  t("col_qty"), min_value=0, step=1, format="%d"
              ),
              "kW": st.column_config.NumberColumn(
                  t("col_kw"), min_value=0.0, step=0.1, format="%.2f"
              ),
              "Peak Hours/day": st.column_config.NumberColumn(
                  t("col_peak_hours"),
                  min_value=0.0,
                  max_value=24.0,
                  step=0.5,
                  format="%.1f",
              ),
              "Off-Peak Hours/day": st.column_config.NumberColumn(
                  t("col_offpeak_hours"),
                  min_value=0.0,
                  max_value=24.0,
                  step=0.5,
                  format="%.1f",
              ),
          },
      )
      st.session_state.departments[dept] = edited_df
      save_persistent_config(
          st.session_state.departments_list, st.session_state.departments
      )


# =====================================================================================
# PAGE 3 — SETTINGS
# =====================================================================================
def page_settings():
  st.markdown(f"## {t('settings_title')}")
  st.caption(t("settings_caption"))
  st.markdown("<hr/>", unsafe_allow_html=True)

  st.markdown(
      f'<div class="section-title">{t("section_rates")}</div>',
      unsafe_allow_html=True,
  )
  r1, r2, r3, r4 = st.columns(4)
  with r1:
    st.number_input(
        t("label_peak_rate"),
        min_value=0.0,
        step=0.01,
        format="%.4f",
        key="peak_rate",
    )
  with r2:
    st.number_input(
        t("label_offpeak_rate"),
        min_value=0.0,
        step=0.01,
        format="%.4f",
        key="offpeak_rate",
    )
  with r3:
    st.number_input(
        t("label_ft_rate"),
        min_value=-5.0,
        step=0.001,
        format="%.4f",
        key="ft_rate",
    )
  with r4:
    st.number_input(
        t("label_service_charge"),
        min_value=0.0,
        step=1.0,
        format="%.2f",
        key="service_charge",
    )

  st.number_input(
      t("label_billing_days"),
      min_value=1,
      max_value=31,
      step=1,
      key="billing_days",
  )

  st.write("")
  st.markdown(
      f'<div class="section-title">{t("section_dept_mgmt")}</div>',
      unsafe_allow_html=True,
  )

  dcol1, dcol2 = st.columns(2)

  with dcol1:
    st.markdown(f"**{t('add_dept_label')}**")
    new_dept_name = st.text_input(
        t("add_dept_input_label"),
        key="new_dept_input",
        placeholder=t("add_dept_placeholder"),
    )
    if st.button(t("add_dept_button"), type="primary", use_container_width=True):
      name = new_dept_name.strip()
      if not name:
        st.warning(t("warn_empty_name"))
      elif name in st.session_state.departments_list:
        st.warning(t("warn_dept_exists", name=name))
      else:
        st.session_state.departments_list.append(name)
        st.session_state.departments[name] = pd.DataFrame([
            {
                "Machine Name": "เครื่องที่ 1",
                "Quantity": 1,
                "kW": 5.0,
                "Peak Hours/day": 8.0,
                "Off-Peak Hours/day": 16.0,
            }
        ])
        save_persistent_config(
            st.session_state.departments_list, st.session_state.departments
        )
        st.success(t("success_dept_added", name=name))
        st.rerun()

  with dcol2:
    st.markdown(f"**{t('delete_dept_label')}**")
    if st.session_state.departments_list:
      dept_to_delete = st.selectbox(
          t("delete_dept_select"),
          options=st.session_state.departments_list,
          key="delete_dept_select",
      )
      if st.button(
          t("delete_dept_button"), type="secondary", use_container_width=True
      ):
        if dept_to_delete in st.session_state.departments_list:
          st.session_state.departments_list.remove(dept_to_delete)
        if dept_to_delete in st.session_state.departments:
          del st.session_state.departments[dept_to_delete]
        save_persistent_config(
            st.session_state.departments_list, st.session_state.departments
        )
        st.success(t("success_dept_deleted", name=dept_to_delete))
        st.rerun()
    else:
      st.info(t("info_no_departments"))

  st.write("")
  st.markdown("### 📋 แผนกทั้งหมดในระบบปัจจุบัน:")
  for idx, d in enumerate(st.session_state.departments_list):
    count = (
        len(st.session_state.departments[d])
        if d in st.session_state.departments
        else 0
    )
    st.markdown(f"- **{idx+1}. {d}** ({count} รายการเครื่องจักร)")


# =====================================================================================
# SIDEBAR NAVIGATION
# =====================================================================================
def render_sidebar():
  with st.sidebar:
    lang_options = {"ไทย": "th", "English": "en"}
    current_label = "ไทย" if st.session_state.lang == "th" else "English"
    chosen = st.selectbox(
        "🌐 ภาษา / Language",
        options=list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_label),
        key="lang_select",
    )
    st.session_state.lang = lang_options[chosen]

    st.markdown(f"## {t('brand_title')}")
    st.caption(t("brand_caption"))
    st.markdown("---")

    page = st.radio(
        "Navigate",
        options=[t("nav_dashboard"), t("nav_data_entry"), t("nav_settings")],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption(
        f"{t('billing_cycle')}: **{st.session_state.billing_days} {t('days')}**"
    )
    st.caption(
        f"{t('departments_tracked')}: **{len(st.session_state.departments_list)}**"
    )
    st.markdown("---")
    st.caption(t("footer"))

  return page


# =====================================================================================
# MAIN APP ENTRY POINT
# =====================================================================================
def main():
  init_session_state()
  inject_css()

  page = render_sidebar()

  if page == t("nav_dashboard"):
    page_dashboard()
  elif page == t("nav_data_entry"):
    page_data_entry()
  elif page == t("nav_settings"):
    page_settings()


if __name__ == "__main__":
  main()
