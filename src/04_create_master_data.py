import pandas as pd
import os

def create_master_table():
    # 1. โหลดข้อมูล
    df_tourism = pd.read_csv('data/processed/tourism_combined_final.csv')
    df_prov = pd.read_csv('data/processed/ProvinceThailandList.csv')
    df_cpi = pd.read_csv('data/processed/Cleaned_CPI_Data.csv')

    # 2. ปรับชื่อคอลัมน์ให้ตรงกัน
    df_tourism = df_tourism.rename(columns={'province': 'ProvinceThai', 'year': 'Year', 'month': 'Month'})
    df_cpi = df_cpi.rename(columns={'จังหวัด': 'ProvinceThai', 'ปี': 'Year', 'เดือน': 'Month'})

    # 3. รวมข้อมูลเบื้องต้น
    df_master = pd.merge(df_tourism, df_prov, on='ProvinceThai', how='left')
    df_master = pd.merge(df_master, df_cpi, on=['ProvinceThai', 'Year', 'Month'], how='left')

    # --- 🌟 ส่วนที่เพิ่มเข้าไป: แก้ปัญหาไม่มีข้อมูลกรุงเทพฯ 🌟 ---
    
    print("🔍 กำลังจัดการข้อมูล Price Index ที่ว่างอยู่ (รวมถึงกรุงเทพฯ)...")

    # คำนวณค่าเฉลี่ย CPI รายเดือนของกลุ่ม "กรุงเทพและปริมณฑล" (นนทบุรี, ปทุมฯ, สมุทรปราการ ฯลฯ)
    vicinity_avg = df_master[df_master['Region_TH'] == 'กรุงเทพมหานครและปริมณฑล'].groupby(['Year', 'Month'])['Price_Index'].transform('mean')
    
    # ถ้าจังหวัดไหน Price_Index เป็นว่าง (NaN) ให้ใช้ค่าเฉลี่ยของภูมิภาคตัวเองแทน
    df_master['Price_Index'] = df_master['Price_Index'].fillna(vicinity_avg)
    
    # กรณีที่ยังว่างอยู่อีก (เช่น ภาคอื่นที่ข้อมูลขาด) ให้ใช้ค่าเฉลี่ยของประเภทเมือง (เมืองหลัก/เมืองรอง) ในเดือนนั้นๆ
    type_avg = df_master.groupby(['Year', 'Month', 'City_type_TH'])['Price_Index'].transform('mean')
    df_master['Price_Index'] = df_master['Price_Index'].fillna(type_avg)

    # --------------------------------------------------------

    # 4. คำนวณ Real Revenue
    df_master['real_revenue'] = (df_master['total_revenue'] / df_master['Price_Index']) * 100

    # 5. บันทึกไฟล์
    output_path = 'data/processed/master_tourism_analysis.csv'
    df_master.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"✅ รวมข้อมูลและเติมค่าว่างสำเร็จ! ไฟล์อยู่ที่: {output_path}")
    return df_master

if __name__ == "__main__":
    create_master_table()