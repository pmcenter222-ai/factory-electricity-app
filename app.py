import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บให้เต็มจอและดูสบายตา
st.set_page_config(
    page_title="Factory Energy & Cost Management",
    page_icon="⚡",
    layout="wide"
)

# --- 1. ระบบจัดการข้อมูลกลาง (Session State) ---
if 'departments' not in st.session_state:
    st.session_state['departments'] = {
        "แผนกเพาะเชื้อและห้องเย็น": [
            {"name": "Chiller / Cooling", "qty": 2, "power_kw": 45.0, "peak_hrs": 6.0, "op_hrs": 12.0},
            {"name": "Autoclave (เครื่องนึ่ง)", "qty": 3, "power_kw": 30.0, "peak_hrs": 4.0, "op_hrs": 8.0}
        ],
        "แผนกบรรจุภัณฑ์": [
            {"name": "Packing Machine", "qty": 1, "power_kw": 15.0, "peak_hrs": 5.0, "op_hrs": 10.0},
            {"name": "Conveyor Belt", "qty": 4, "power_kw": 3.5, "peak_hrs": 6.0, "op_hrs": 12.0}
        ]
    }

if 'settings' not in st.session_state:
    st.session_state['settings'] = {
        "peak_rate": 4.1839,
        "op_rate": 2.6037,
        "ft_rate": 0.3972,
        "service_charge": 312.24,
        "last_month_cost": 85400.0,
        "avg_historic_cost": 82000.0,
        "days_per_month": 30
    }

if 'bill_data' not in st.session_state:
    st.session_state['bill_data'] = {
        "bill_peak_kwh": 12500.0,
        "bill_op_kwh": 18200.0,
        "solar_kwh": 4500.0
    }

# --- 2. เมนูด้านซ้าย (Sidebar Navigation) ---
st.sidebar.title("⚡ เมนูระบบจัดการพลังงาน")
menu = st.sidebar.radio(
    "เลือกหน้าการใช้งาน:",
    ["📊 หน้าสรุป (Dashboard)", "📝 หน้าลงข้อมูลจริง", "⚙️ หน้า Setting (ตั้งค่า)"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **คำแนะนำ:** กรอกข้อมูลบิลและเครื่องจักรที่หน้าลงข้อมูล จากนั้นดูผลวิเคราะห์ที่หน้าสรุป")


# ==========================================
# หน้าที่ 1: หน้าสรุป (Dashboard)
# ==========================================
if menu == "📊 หน้าสรุป (Dashboard)":
    st.title("📊 แดชบอร์ดสรุปการใช้พลังงานและค่าไฟฟ้าโรงงาน")
    st.markdown("วิเคราะห์สัดส่วนการใช้ไฟฟ้ารายแผนก ต้นทุน และการเปรียบเทียบสถิติย้อนหลัง")
    st.markdown("---")

    # คำนวณผลลัพธ์จากข้อมูลปัจจุบัน
    sets = st.session_state['settings']
    bill = st.session_state['bill_data']
    depts = st.session_state['departments']
    
    days = sets['days_per_month']
    
    # คำนวณสัดส่วนพลังงานแต่ละแผนกจากเครื่องจักร
    dept_totals = {}
    factory_theoretical_total = 0
    
    for dept_name, machines in depts.items():
        dept_sum = 0
        for m in machines:
            m_kwh = m['qty'] * m['power_kw'] * (m['peak_hrs'] + m['op_hrs']) * days
            dept_sum += m_kwh
        dept_totals[dept_name] = dept_sum
        factory_theoretical_total += dept_sum

    # คำนวณค่าไฟฟ้าจากบิลจริง + โซล่าเซลล์
    solar = bill['solar_kwh']
    net_peak = max(0, bill['bill_peak_kwh'] - solar)
    solar_remainder = max(0, solar - bill['bill_peak_kwh'])
    net_op = max(0, bill['bill_op_kwh'] - solar_remainder)
    net_total_kwh = net_peak + net_op

    energy_cost = (net_peak * sets['peak_rate']) + (net_op * sets['op_rate'])
    ft_cost = net_total_kwh * sets['ft_rate']
    subtotal = energy_cost + ft_cost + sets['service_charge']
    vat = subtotal * 0.07
    grand_total = subtotal + vat

    # 1. ส่วนแสดง KPI Cards เปรียบเทียบ
    st.subheader("📈 สถิติและเปรียบเทียบค่าใช้จ่ายภาพรวม")
    col1, col2, col3 = st.columns(3)
    
    diff_last = grand_total - sets['last_month_cost']
    diff_avg = grand_total - sets['avg_historic_cost']
    
    col1.metric("💰 ค่าไฟฟ้าสุทธิเดือนนี้", f"{grand_total:,.2f} บาท", delta=f"{diff_last:+,.2f} บาท จากเดือนก่อน", delta_color="inverse")
    col2.metric("📉 ค่าไฟเดือนที่แล้ว", f"{sets['last_month_cost']:,.2f} บาท")
    col3.metric("📊 ค่าเฉลี่ยย้อนหลัง 6 เดือน", f"{sets['avg_historic_cost']:,.2f} บาท", delta=f"{diff_avg:+,.2f} บาท จากค่าเฉลี่ย", delta_color="inverse")

    st.markdown("---")

    # 2. ส่วนแสดงข้อมูลพลังงานจากบิล & โซล่าเซลล์
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("⚡ รายละเอียดหน่วยไฟฟ้า (จากบิล & โซล่าเซลล์)")
        st.write(f"- **หน่วยไฟฟ้าบิล (Peak):** {bill['bill_peak_kwh']:,.2f} kWh")
        st.write(f"- **หน่วยไฟฟ้าบิล (Off-Peak):** {bill['bill_op_kwh']:,.2f} kWh")
        st.write(f"- **พลังงานจากโซล่าเซลล์:** {bill['solar_kwh']:,.2f} kWh")
        st.success(f"**รวมหน่วยไฟฟ้าสุทธิที่ต้องชำระ:** {net_total_kwh:,.2f} kWh")

    with c_right:
        st.subheader("💵 โครงสร้างค่าใช้จ่ายสุทธิ")
        st.write(f"- ค่าพลังงานไฟฟ้า (Peak/Off-Peak): {energy_cost:,.2f} บาท")
        st.write(f"- ค่า Ft รวม: {ft_cost:,.2f} บาท")
        st.write(f"- ค่าบริการรายเดือน: {sets['service_charge']:,.2f} บาท")
        st.write(f"- ภาษีมูลค่าเพิ่ม (VAT 7%): {vat:,.2f} บาท")

    st.markdown("---")

    # 3. ส่วนแสดงสัดส่วนและการจัดสรรต้นทุนรายแผนก
    st.subheader("🏭 สัดส่วนการใช้ไฟฟ้าและการจัดสรรต้นทุนแยกตามแผนก")
    
    if factory_theoretical_total > 0:
        for dept_name, dept_kwh in dept_totals.items():
            share = (dept_kwh / factory_theoretical_total) * 100
            allocated_cost = grand_total * (share / 100)
            
            with st.container():
                st.markdown(f"#### 📁 {dept_name}")
                col_a, col_b, col_c = st.columns([2, 2, 2])
                col_a.write(f"พลังงานรวม: **{dept_kwh:,.2f} kWh**")
                col_b.write(f"สัดส่วนการใช้ไฟ: **{share:.2f}%** ของโรงงาน")
                col_c.write(f"ต้นทุนค่าไฟประเมิน: **{allocated_cost:,.2f} บาท**")
                st.progress(share / 100)
                st.markdown("")
    else:
        st.warning("⚠️ กรุณากรอกข้อมูลกำลังไฟฟ้าและชั่วโมงทำงานของเครื่องจักรใน 'หน้าลงข้อมูลจริง'")


# ==========================================
# หน้าที่ 2: หน้าลงข้อมูลจริง
# ==========================================
elif menu == "📝 หน้าลงข้อมูลจริง":
    st.title("📝 บันทึกข้อมูลบิลค่าไฟและเครื่องจักรรายแผนก")
    st.markdown("กรอกหน่วยไฟฟ้าจากบิลการไฟฟ้า ผลผลิตโซล่าเซลล์ และรายละเอียดการทำงานของเครื่องจักร")
    st.markdown("---")

    # 1. ข้อมูลบิลค่าไฟและโซล่าเซลล์
    st.subheader("📄 1. ข้อมูลจากบิลค่าไฟฟ้าและโซล่าเซลล์ประจำเดือน")
    b_col1, b_col2, b_col3 = st.columns(3)
    
    with b_col1:
        st.session_state['bill_data']['bill_peak_kwh'] = st.number_input(
            "หน่วยไฟฟ้าบิล ช่วง Peak (kWh)", value=st.session_state['bill_data']['bill_peak_kwh'], step=100.0
        )
    with b_col2:
        st.session_state['bill_data']['bill_op_kwh'] = st.number_input(
            "หน่วยไฟฟ้าบิล ช่วง Off-Peak (kWh)", value=st.session_state['bill_data']['bill_op_kwh'], step=100.0
        )
    with b_col3:
        st.session_state['bill_data']['solar_kwh'] = st.number_input(
            "พลังงานโซล่าเซลล์ที่ผลิตได้ทั้งหมด (kWh)", value=st.session_state['bill_data']['solar_kwh'], step=100.0
        )

    st.markdown("---")

    # 2. ข้อมูลเครื่องจักรแยกตามแผนก
    st.subheader("⚙️ 2. ข้อมูลชั่วโมงการทำงานและกำลังไฟฟ้าของเครื่องจักรแยกตามแผนก")
    st.session_state['settings']['days_per_month'] = st.slider(
        "จำนวนวันทำงานเฉลี่ยต่อเดือน", min_value=1, max_value=31, value=st.session_state['settings']['days_per_month']
    )

    depts = st.session_state['departments']
    
    for dept_name, machines in depts.items():
        with st.expander(f"📁 แผนก: {dept_name}", expanded=True):
            for i, m in enumerate(machines):
                st.markdown(f"**เครื่องที่ {i+1}: {m['name']}**")
                mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                
                with mc1:
                    m['qty'] = st.number_input(f"จำนวนเครื่อง ({m['name']})", value=int(m['qty']), min_value=1, key=f"{dept_name}_{i}_qty")
                with mc2:
                    m['power_kw'] = st.number_input(f"กำลังไฟ/เครื่อง (kW)", value=float(m['power_kw']), key=f"{dept_name}_{i}_kw")
                with mc3:
                    m['peak_hrs'] = st.number_input(f"ชม. Peak/วัน", value=float(m['peak_hrs']), key=f"{dept_name}_{i}_peak")
                with mc4:
                    m['op_hrs'] = st.number_input(f"ชม. Off-Peak/วัน", value=float(m['op_hrs']), key=f"{dept_name}_{i}_op")
                with mc5:
                    calc_total = m['qty'] * m['power_kw'] * (m['peak_hrs'] + m['op_hrs']) * st.session_state['settings']['days_per_month']
                    st.metric("รวมพลังงาน (kWh/เดือน)", f"{calc_total:,.1f}")
                st.markdown("---")

    st.success("✅ ข้อมูลทั้งหมดถูกบันทึกอัตโนมัติ สามารถกดไปที่เมนู 'หน้าสรุป (Dashboard)' เพื่อดูรายงานได้ทันทีครับ")


# ==========================================
# หน้าที่ 3: หน้า Setting (ตั้งค่า)
# ==========================================
elif menu == "⚙️ หน้า Setting (ตั้งค่า)":
    st.title("⚙️ ตั้งค่าระบบ เรทราคาค่าไฟฟ้า และจัดการแผนก")
    st.markdown("กำหนดอัตราค่าไฟฟ้าตามประเภทผู้ใช้ไฟ ค่า Ft ค่าบริการ และจัดการโครงสร้างแผนกในโรงงาน")
    st.markdown("---")

    sets = st.session_state['settings']

    st.subheader("💰 กำหนดเรทราคาค่าไฟฟ้าและค่าบริการ")
    s_col1, s_col2 = st.columns(2)
    
    with s_col1:
        sets['peak_rate'] = st.number_input("เรทค่าไฟ Peak (บาท/หน่วย)", value=float(sets['peak_rate']), format="%.4f")
        sets['op_rate'] = st.number_input("เรทค่าไฟ Off-Peak (บาท/หน่วย)", value=float(sets['op_rate']), format="%.4f")
        sets['ft_rate'] = st.number_input("ค่า Ft (บาท/หน่วย)", value=float(sets['ft_rate']), format="%.4f")
    
    with s_col2:
        sets['service_charge'] = st.number_input("ค่าบริการรายเดือน (บาท)", value=float(sets['service_charge']))
        sets['last_month_cost'] = st.number_input("ยอดค่าไฟเดือนที่แล้วสำหรับเปรียบเทียบ (บาท)", value=float(sets['last_month_cost']))
        sets['avg_historic_cost'] = st.number_input("ค่าเฉลี่ยค่าไฟย้อนหลัง 6 เดือน (บาท)", value=float(sets['avg_historic_cost']))

    st.markdown("---")
    st.subheader("🏢 จัดการแผนกในโรงงาน")
    
    # เพิ่มแผนกใหม่
    new_dept_name = st.text_input("ชื่อแผนกใหม่ที่ต้องการเพิ่ม:")
    if st.button("➕ เพิ่มแผนกใหม่"):
        if new_dept_name and new_dept_name not in st.session_state['departments']:
            st.session_state['departments'][new_dept_name] = [
                {"name": "เครื่องจักรหลัก", "qty": 1, "power_kw": 10.0, "peak_hrs": 5.0, "op_hrs": 10.0}
            ]
            st.success(f"เพิ่มแผนก '{new_dept_name}' สำเร็จ!")
            st.rerun()
        elif new_dept_name in st.session_state['departments']:
            st.warning("ชื่อแผนกนี้มีอยู่แล้วในระบบ")

    st.write("---")
    st.markdown("### แผนกที่มีอยู่ปัจจุบัน:")
    depts = st.session_state['departments']
    
    for d_name in list(depts.keys()):
        col_d1, col_d2 = st.columns([3, 1])
        col_d1.markdown(f"- **{d_name}** (มี {len(depts[d_name])} รายการเครื่องจักร)")
        if col_d2.button(f"🗑️ ลบแผนก", key=f"del_{d_name}"):
            if len(depts) > 1:
                del st.session_state['departments'][d_name]
                st.success(f"ลบแผนก {d_name} เรียบร้อยแล้ว")
                st.rerun()
            else:
                st.error("ต้องมีแผนกอย่างน้อย 1 แผนกในระบบ")

    st.success("✅ บันทึกการตั้งค่าทั้งหมดเรียบร้อยแล้ว")
