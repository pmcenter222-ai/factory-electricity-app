import streamlit as st
import pandas as pd

st.set_page_config(page_title="Factory Energy Dashboard", layout="wide")

st.title("⚡ แดชบอร์ดคำนวณและวิเคราะห์การใช้ไฟฟ้าโรงงาน")
st.markdown("วิเคราะห์พลังงานรายแผนก หักลบโซล่าเซลล์ เทียบกับเดือนก่อนหน้า และค่าเฉลี่ยย้อนหลัง")

# Sidebar: ค่าคงที่และเรทค่าไฟ
st.sidebar.header("⚙️ ตั้งค่าเรทราคาและโซล่าเซลล์")
solar_kwh = st.sidebar.number_input("พลังงานโซล่าเซลล์ทั้งหมด (kWh/เดือน)", value=4500.0, step=100.0)
peak_rate = st.sidebar.number_input("เรทค่าไฟ Peak (บาท/หน่วย)", value=4.1839, format="%.4f")
op_rate = st.sidebar.number_input("เรทค่าไฟ Off-Peak (บาท/หน่วย)", value=2.6037, format="%.4f")
ft_rate = st.sidebar.number_input("ค่า Ft (บาท/หน่วย)", value=0.3972, format="%.4f")
service_charge = st.sidebar.number_input("ค่าบริการรายเดือน (บาท)", value=312.24)

# ข้อมูลเปรียบเทียบเดือนที่แล้วและค่าเฉลี่ย
st.sidebar.markdown("---")
st.sidebar.header("📊 ข้อมูลเปรียบเทียบอ้างอิง")
last_month_cost = st.sidebar.number_input("ค่าไฟเดือนที่แล้ว (บาท)", value=85400.0)
avg_historic_cost = st.sidebar.number_input("ค่าเฉลี่ยย้อนหลัง 6 เดือน (บาท)", value=82000.0)

# Main input: แยกตามแผนกและเครื่องจักร
st.subheader("🏭 ข้อมูลการใช้พลังงานแยกตามแผนกและเครื่องจักร")

# จำนวนวันทำงานต่อเดือน
days_per_month = st.slider("จำนวนวันทำงานต่อเดือน", min_value=1, max_value=31, value=30)

# แผนกที่ 1: ระบบทำความเย็น / ห้องเย็น
with st.expander("📁 แผนกเพาะเชื้อและห้องเย็น (Cooling & Culture)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        c1_qty = st.number_input("จำนวนเครื่อง Chiller", value=2, key="c1_qty")
        c1_kw = st.number_input("กำลังไฟฟ้า Chiller (kW)", value=45.0, key="c1_kw")
        c1_peak = st.number_input("ชม. Peak / วัน (Chiller)", value=6.0, key="c1_peak")
        c1_op = st.number_input("ชม. Off-Peak / วัน (Chiller)", value=12.0, key="c1_op")
    with col2:
        c2_qty = st.number_input("จำนวนเครื่อง Autoclave", value=3, key="c2_qty")
        c2_kw = st.number_input("กำลังไฟฟ้า Autoclave (kW)", value=30.0, key="c2_kw")
        c2_peak = st.number_input("ชม. Peak / วัน (Autoclave)", value=4.0, key="c2_peak")
        c2_op = st.number_input("ชม. Off-Peak / วัน (Autoclave)", value=8.0, key="c2_op")
    
    dept1_peak = ((c1_qty * c1_kw * c1_peak) + (c2_qty * c2_kw * c2_peak)) * days_per_month
    dept1_op = ((c1_qty * c1_kw * c1_op) + (c2_qty * c2_kw * c2_op)) * days_per_month
    dept1_total = dept1_peak + dept1_op

# แผนกที่ 2: บรรจุภัณฑ์
with st.expander("📁 แผนกบรรจุภัณฑ์ (Packing Department)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        p1_qty = st.number_input("จำนวนเครื่อง Packing Line", value=1, key="p1_qty")
        p1_kw = st.number_input("กำลังไฟฟ้า Packing (kW)", value=15.0, key="p1_kw")
        p1_peak = st.number_input("ชม. Peak / วัน (Packing)", value=5.0, key="p1_peak")
        p1_op = st.number_input("ชม. Off-Peak / วัน (Packing)", value=10.0, key="p1_op")
    with col2:
        p2_qty = st.number_input("จำนวนเครื่อง Conveyor", value=4, key="p2_qty")
        p2_kw = st.number_input("กำลังไฟฟ้า Conveyor (kW)", value=3.5, key="p2_kw")
        p2_peak = st.number_input("ชม. Peak / วัน (Conveyor)", value=6.0, key="p2_peak")
        p2_op = st.number_input("ชม. Off-Peak / วัน (Conveyor)", value=12.0, key="p2_op")

    dept2_peak = ((p1_qty * p1_kw * p1_peak) + (p2_qty * p2_kw * p2_peak)) * days_per_month
    dept2_op = ((p1_qty * p1_kw * p1_op) + (p2_qty * p2_kw * p2_op)) * days_per_month
    dept2_total = dept2_peak + dept2_op

# รวมทั้งโรงงาน
factory_peak = dept1_peak + dept2_peak
factory_op = dept1_op + dept2_op
gross_total_kwh = factory_peak + factory_op

# สัดส่วนแผนก (%)
d1_share = (dept1_total / gross_total_kwh * 100) if gross_total_kwh > 0 else 0
d2_share = (dept2_total / gross_total_kwh * 100) if gross_total_kwh > 0 else 0

# หักโซล่าเซลล์ (หัก Peak ก่อน เหลือไปหัก Off-Peak)
net_peak = max(0, factory_peak - solar_kwh)
solar_remainder = max(0, solar_kwh - factory_peak)
net_op = max(0, factory_op - solar_remainder)
net_total_kwh = net_peak + net_op

# คำนวณค่าใช้จ่าย
cost_energy = (net_peak * peak_rate) + (net_op * op_rate)
cost_ft = net_total_kwh * ft_rate
subtotal = cost_energy + cost_ft + service_charge
vat = subtotal * 0.07
grand_total = subtotal + vat

# --- ส่วนแสดงผล Dashboard ---
st.markdown("---")
st.subheader("📊 ผลการสรุปและเปรียบเทียบสถิติสำคัญ")

m1, m2, m3 = st.columns(3)
diff_last = grand_total - last_month_cost
diff_avg = grand_total - avg_historic_cost

m1.metric("💰 ค่าไฟฟ้าสุทธิเดือนนี้", f"{grand_total:,.2f} บาท", delta=f"{diff_last:+,.2f} บาท จากเดือนก่อน", delta_color="inverse")
m2.metric("📉 เทียบกับเดือนที่แล้ว", f"{last_month_cost:,.2f} บาท")
m3.metric("📊 เทียบค่าเฉลี่ยย้อนหลัง", f"{avg_historic_cost:,.2f} บาท", delta=f"{diff_avg:+,.2f} บาท จากค่าเฉลี่ย", delta_color="inverse")

st.markdown("---")
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.markdown("### ⚡ สรุปหน่วยไฟฟ้า (kWh)")
    st.write(f"- หน่วยไฟฟ้าเดิมก่อนหักโซล่าเซลล์: **{gross_total_kwh:,.2f} kWh**")
    st.write(f"- ผลผลิตจากโซล่าเซลล์: **{solar_kwh:,.2f} kWh**")
    st.write(f"- หน่วยไฟฟ้าสุทธิที่ต้องชำระ (Peak): **{net_peak:,.2f} kWh**")
    st.write(f"- หน่วยไฟฟ้าสุทธิที่ต้องชำระ (Off-Peak): **{net_op:,.2f} kWh**")
    st.write(f"- **รวมหน่วยไฟฟ้าสุทธิ:** **{net_total_kwh:,.2f} kWh**")

with col_res2:
    st.markdown("### 🥧 สัดส่วนการใช้พลังงานรายแผนก")
    st.write(f"- **แผนกเพาะเชื้อและห้องเย็น:** {dept1_total:,.2f} kWh (**{d1_share:.2f}%**)")
    st.write(f"- **แผนกบรรจุภัณฑ์:** {dept2_total:,.2f} kWh (**{d2_share:.2f}%**)")
    st.progress(d1_share / 100, text=f"สัดส่วนห้องเย็น {d1_share:.1f}% / บรรจุภัณฑ์ {d2_share:.1f}%")
