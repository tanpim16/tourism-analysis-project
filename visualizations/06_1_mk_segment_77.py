import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os
from matplotlib.patches import Patch

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  'white',
    'axes.facecolor':    '#F8F9FA',
    'axes.grid':         True,
    'grid.color':        '#FFFFFF',
    'grid.linewidth':    1.2,
    'font.family':       'sans-serif',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom':False,
})

# 1. LOAD DATA
file_path = 'data/processed/final_master_with_trends.csv'
if not os.path.exists(file_path):
    # กรณีรันจาก root โดยไม่มีโฟลเดอร์ data
    file_path = 'final_master_with_trends.csv'

df = pd.read_csv(file_path)

# ────────────────────────────────────────────────────────────
# 2. [PATCH] Fix Nakhon Ratchasima & Data Cleaning
# ────────────────────────────────────────────────────────────
# ตัดช่องว่างแฝงในคอลัมน์ภาษาไทย (ถ้ามี)
df['ProvinceThai'] = df['ProvinceThai'].astype(str).str.strip()

# เติมข้อมูลที่หายไปสำหรับนครราชสีมา (ตัวการที่ทำให้เหลือ 21 จังหวัด)
mask_korat = df['ProvinceThai'] == 'นครราชสีมา'
df.loc[mask_korat, 'ProvinceEN'] = 'Nakhon Ratchasima'
df.loc[mask_korat, 'City_type_TH'] = 'เมืองหลัก'
df.loc[mask_korat, 'City_type_EN'] = 'Primary City'

# ล้างค่าว่างในส่วนของรายได้และ Price Index
df['thai_revenue'] = df['thai_revenue'].fillna(0)
df['foreign_revenue'] = df['foreign_revenue'].fillna(0)
df['Price_Index'] = df['Price_Index'].fillna(100)

# 3. CALCULATE REAL REVENUE (ปรับค่าเงินเฟ้อ)
df['thai_rev_real'] = df['thai_revenue'] / (df['Price_Index'] / 100)
df['fore_rev_real'] = df['foreign_revenue'] / (df['Price_Index'] / 100)

# 4. AGGREGATION (รวมรายได้รายจังหวัด)
# ใช้ 'City_type_TH' เป็นตัวแบ่งเพราะเราแก้ค่า 'เมืองหลัก' ไว้แล้ว
agg_df = (
    df.groupby(['ProvinceEN', 'City_type_TH'])[['thai_rev_real', 'fore_rev_real']]
    .sum()
    .reset_index()
)
agg_df['total_rev'] = agg_df['thai_rev_real'] + agg_df['fore_rev_real']

# 5. SPLIT: Primary (22) vs Secondary (55)
primary_df = agg_df[
    agg_df['City_type_TH'].str.contains('หลัก', na=False)
].copy().sort_values('total_rev', ascending=True) # เรียงน้อยไปมากเพื่อ barh

secondary_df = agg_df[
    agg_df['City_type_TH'].str.contains('รอง', na=False)
].copy().sort_values('total_rev', ascending=True)

print(f"✅ ตรวจสอบจำนวนจังหวัด: Primary = {len(primary_df)} | Secondary = {len(secondary_df)}")

# ────────────────────────────────────────────────────────────
# 6. VISUALIZATION (Side-by-Side)
# ────────────────────────────────────────────────────────────
# คำนวณความสูงให้เหมาะสมกับจำนวนจังหวัด
row_height = 0.35
fig_height = max(len(primary_df), len(secondary_df)) * row_height + 3
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(22, fig_height), facecolor='white')

bg_color = '#fcfcfc'

# --- LEFT PANEL: Major Cities (Blue) ---
ax_left.set_facecolor(bg_color)
ax_left.barh(primary_df['ProvinceEN'], primary_df['thai_rev_real'], color='#89c4e1', label='Domestic (Thai)')
ax_left.barh(primary_df['ProvinceEN'], primary_df['fore_rev_real'], left=primary_df['thai_rev_real'], color='#1a6fa8', label='International (Foreign)')

# ใส่ Data Labels ฝั่งซ้าย
max_l = primary_df['total_rev'].max()
for i, total in enumerate(primary_df['total_rev']):
    ax_left.text(total + (max_l * 0.01), i, f'{total:,.0f}', va='center', fontsize=9, fontweight='bold')

ax_left.set_title('Major Cities: Revenue Powerhouses', fontsize=16, fontweight='bold', pad=20)
ax_left.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
ax_left.grid(axis='x', linestyle='--', alpha=0.4)
ax_left.legend(loc='lower right', frameon=True)

# --- RIGHT PANEL: Secondary Cities (Green) ---
ax_right.set_facecolor(bg_color)
ax_right.barh(secondary_df['ProvinceEN'], secondary_df['thai_rev_real'], color='#a8ddb5', label='Domestic (Thai)')
ax_right.barh(secondary_df['ProvinceEN'], secondary_df['fore_rev_real'], left=secondary_df['thai_rev_real'], color='#2a8f48', label='International (Foreign)')

# ใส่ Data Labels ฝั่งขวา
max_r = secondary_df['total_rev'].max()
for i, total in enumerate(secondary_df['total_rev']):
    ax_right.text(total + (max_r * 0.01), i, f'{total:,.0f}', va='center', fontsize=9, fontweight='bold')

ax_right.set_title('Secondary Cities: Emerging Potential', fontsize=16, fontweight='bold', pad=20)
ax_right.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
ax_right.grid(axis='x', linestyle='--', alpha=0.4)
ax_right.legend(loc='lower right', frameon=True)

# 7. FINAL TOUCHES
plt.suptitle('Figure 12: Comparison of Revenue Structure between Primary and Secondary Tiers', 
             fontsize=24, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.03, 1, 0.95], w_pad=8)

# SAVE
os.makedirs('visualizations', exist_ok=True)
output_path = 'visualizations/Figure_12_Revenue_Comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"🚀 กราฟถูกสร้างสำเร็จและบันทึกไว้ที่: {output_path}")