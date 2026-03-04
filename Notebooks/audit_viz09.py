import pandas as pd
import matplotlib.pyplot as plt
import textwrap
import os

# --- 1. LOAD & CLEAN ---
df_path = 'data/processed/master_tourism_analysis.csv'
list_path = 'data/processed/ProvinceThailandList.csv'

df_main = pd.read_csv(df_path)
province_list = pd.read_csv(list_path)

# กำจัดค่าว่างในชื่อจังหวัด (ป้องกัน Error)
df_main = df_main.dropna(subset=['ProvinceEN'])

# --- 2. MASTER MAPPING (แก้ไขชื่อให้ตรงกัน) ---
# เราต้องเปลี่ยนชื่อใน Master (ที่อาจจะเขียนติดกัน) 
# ให้กลายเป็นชื่อมาตรฐานที่มีเว้นวรรคตามไฟล์ List ครับ

name_map = {
    'Chainat': 'Chai Nat',
    'Lopburi': 'Lop Buri',
    'Nong Bua Lamphu': 'Nong Bua Lam Phu',
    'Prachinburi': 'Prachin Buri',
    'Si Saket': 'Si Sa Ket',
    'Singburi': 'Sing Buri',
    'Suphanburi': 'Suphan Buri',
    'Buriram': 'Buri Ram',   # เพิ่มตัวนี้เข้าไปครับ
    'Burirum': 'Buri Ram'    # กันเหนียวสำหรับบางไฟล์ที่สะกดด้วยตัว u
}

# ปรับปรุงชื่อใน Master
df_main['ProvinceEN'] = df_main['ProvinceEN'].str.strip().replace(name_map)

# ปรับปรุงชื่อใน List (เผื่อมีช่องว่างหลงเหลือ)
province_list['ProvinceEN'] = province_list['ProvinceEN'].str.strip()

# --- 3. RE-CALCULATE (Data driven 100%) ---
df_agg = df_main.groupby('ProvinceEN').agg({'total_visitors': 'mean', 'real_revenue': 'mean'}).reset_index()
secondary_base = province_list[province_list['City_type_EN'].str.contains('Secondary', na=False, case=False)].copy()

# Merge ใหม่ (ควรจะติดครบ 55 จังหวัดแล้ว)
secondary_only = pd.merge(secondary_base[['ProvinceEN', 'Region_EN']], df_agg, on='ProvinceEN', how='left')

# ตรวจสอบหลัง Merge
missing_count = secondary_only['real_revenue'].isna().sum()
if missing_count > 0:
    missing_list = secondary_only[secondary_only['real_revenue'].isna()]['ProvinceEN'].tolist()
    print(f"⚠️ ยังมี {missing_count} จังหวัดที่หาข้อมูลไม่เจอ: {missing_list}")
else:
    print("✅ ยอดเยี่ยม! ครบ 55 จังหวัดแบบมีข้อมูลจริงทั้งหมดแล้ว")

# --- 4. PREP & CLASSIFY ---
secondary_only['yield_per_head'] = (secondary_only['real_revenue'] * 1000000) / secondary_only['total_visitors']
secondary_only['contribution_pct'] = (secondary_only['real_revenue'] / secondary_only['real_revenue'].sum()) * 100

x_mid, y_mid = secondary_only['yield_per_head'].median(), secondary_only['contribution_pct'].median()

def classify(row):
    if row['yield_per_head'] >= x_mid and row['contribution_pct'] >= y_mid: return 'STARS'
    if row['yield_per_head'] < x_mid and row['contribution_pct'] >= y_mid: return 'MASS MARKET'
    if row['yield_per_head'] >= x_mid and row['contribution_pct'] < y_mid: return 'PREMIUM NICHE'
    return 'EMERGING'

secondary_only['Quadrant'] = secondary_only.apply(classify, axis=1)

# --- 5. DRAW FIGURE 9 (Strategic Scorecard) ---
# (ใช้โค้ดวาดรูป Scorecard 4 Blocks ตัวล่าสุดได้เลยครับ)