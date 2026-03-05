import pandas as pd
import numpy as np

# 1. โหลดข้อมูล (เปลี่ยนชื่อไฟล์ตามที่คุณใช้อยู่)
try:
    df = pd.read_csv('data/processed/final_master_with_trends.csv')
except FileNotFoundError:
    # หากไม่พบไฟล์ ให้ลองหาชื่อไฟล์สำรองที่เคยคุยกัน
    df = pd.read_csv('data/processed/master_tourism_analysis.csv')

# 2. เตรียมข้อมูล (รวม Search Intent ทั้งไทยและอังกฤษ)
# อ้างอิงจากโค้ดที่คุณส่งมา: search_thai + search_foreign
df['total_search'] = df['search_thai'] + df['search_foreign']

# 3. แยกกลุ่มเมืองหลัก และ เมืองรอง
# ปรับให้ค้นหาคำว่า 'Major' และ 'Secondary' ในคอลัมน์ City_type_EN
city_types = {
    'Major Cities': df[df['City_type_EN'].str.contains('Major', case=False, na=False)],
    'Secondary Cities': df[df['City_type_EN'].str.contains('Secondary', case=False, na=False)]
}

print("📊 --- LAG CORRELATION ANALYSIS RESULTS ---")

for label, group in city_types.items():
    # ยุบข้อมูลรายเดือน (รวมทุกจังหวัดในกลุ่มเดียวกันเข้าด้วยกัน)
    monthly = group.groupby(['Year', 'Month']).agg({
        'total_visitors': 'sum',
        'total_search': 'sum'
    }).sort_values(['Year', 'Month']).reset_index()
    
    # คำนวณหา Correlation ในช่วง Lag 0-4 เดือน
    results = []
    for i in range(5):
        # ทดสอบการเลื่อน (Shift) ข้อมูลนักท่องเที่ยวไปข้างหลัง i เดือน 
        # เพื่อดูว่าการค้นหาในอดีต สัมพันธ์กับการมาจริงในอีก i เดือนข้างหน้าแค่ไหน
        corr = monthly['total_search'].corr(monthly['total_visitors'].shift(-i))
        results.append({'Lag (Months)': i, 'Correlation (r)': corr})
    
    res_df = pd.DataFrame(results)
    
    # หาค่าที่แม่นยำที่สุด (Correlation สูงสุด)
    best_lag = res_df.loc[res_df['Correlation (r)'].idxmax()]
    
    print(f"\n📍 Group: {label}")
    print(res_df.to_string(index=False))
    print(f"👉 Recommended Lag: {int(best_lag['Lag (Months)'])} Month(s) (Max r = {best_lag['Correlation (r)']:.3f})")

print("\n-------------------------------------------")