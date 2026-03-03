import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import os

# --- 1. LOAD & PREP ---
df_path = 'data/processed/master_tourism_analysis.csv'
list_path = 'data/processed/ProvinceThailandList.csv'
df_main = pd.read_csv(df_path)
province_list = pd.read_csv(list_path)

# ยุบข้อมูลรายเดือน/ปี ให้เหลือ 1 จังหวัด 1 ค่า
df_agg = df_main.groupby('ProvinceEN').agg({'total_visitors': 'mean', 'real_revenue': 'mean'}).reset_index()
df = pd.merge(df_agg, province_list[['ProvinceEN', 'City_type_EN']], on='ProvinceEN', how='left')
secondary_only = df[df['City_type_EN'].str.contains('Secondary', na=False, case=False)].copy()

# คำนวณแกน X (Yield) และ แกน Y (Contribution)
secondary_only['yield_per_head'] = (secondary_only['real_revenue'] * 1000000) / secondary_only['total_visitors']
secondary_only['contribution_pct'] = (secondary_only['real_revenue'] / secondary_only['real_revenue'].sum()) * 100

# --- 2. THE VISUALS ---
fig, ax = plt.subplots(figsize=(13, 10), facecolor='#FAFAFA') # พื้นหลังสีควันบุหรี่นิดๆ
sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.5})

# วาดจุด (ใช้ไล่เฉดสีตามความเก่ง จะดูแพงกว่าสีเดียว)
scatter = ax.scatter(secondary_only['yield_per_head'], secondary_only['contribution_pct'], 
                     s=150, c=secondary_only['yield_per_head'], cmap='summer_r', 
                     alpha=0.6, edgecolors='gray', linewidth=0.5)

# เส้นแบ่ง (ใช้สีเทาเข้มแต่เส้นบาง เพื่อไม่ให้ดูรก)
x_mid, y_mid = secondary_only['yield_per_head'].median(), secondary_only['contribution_pct'].median()
ax.axvline(x=x_mid, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
ax.axhline(y=y_mid, color='black', linestyle='-', linewidth=0.8, alpha=0.3)

# --- 3. LABELING (ใส่ชื่อเฉพาะ Outliers ที่โดดเด่นจริงๆ) ---
# เลือก Top 3 ของแต่ละด้าน เพื่อไม่ให้ชื่อรกกราฟ
labels = set(secondary_only.nlargest(3, 'contribution_pct')['ProvinceEN']) | \
         set(secondary_only.nlargest(3, 'yield_per_head')['ProvinceEN'])

for i, row in secondary_only.iterrows():
    if row['ProvinceEN'] in labels:
        ax.annotate(row['ProvinceEN'], (row['yield_per_head'], row['contribution_pct']),
                    xytext=(10, 5), textcoords='offset points', fontsize=11, 
                    fontweight='bold', alpha=0.8)

# --- 4. QUADRANT BOXES (Professional Boxes) ---
bbox_style = dict(boxstyle="round4,pad=0.6", fc="white", ec="#CCCCCC", alpha=0.8, lw=1)

# วางข้อความที่มุม 4 มุม แบบไม่ง้อพิกัดข้อมูล
# ขวาบน
ax.text(0.97, 0.97, 'STARS\nHigh Value & Volume', transform=ax.transAxes, 
        ha='right', va='top', fontsize=12, fontweight='bold', color='#2E4053', bbox=bbox_style)
# ซ้ายบน
ax.text(0.03, 0.97, 'MASS MARKET\nHigh Volume, Low Value', transform=ax.transAxes, 
        ha='left', va='top', fontsize=12, fontweight='bold', color='#A04000', bbox=bbox_style)
# ขวาล่าง
ax.text(0.97, 0.03, 'PREMIUM NICHE\nHigh Value, Low Volume', transform=ax.transAxes, 
        ha='right', va='bottom', fontsize=12, fontweight='bold', color='#512E5F', bbox=bbox_style)
# ซ้ายล่าง
ax.text(0.03, 0.03, 'EMERGING\nDeveloping Potential', transform=ax.transAxes, 
        ha='left', va='bottom', fontsize=12, fontweight='bold', color='#707B7C', bbox=bbox_style)

# --- 5. FINISHING ---
ax.set_title('Secondary City Portfolio Analysis', fontsize=20, fontweight='bold', pad=25, loc='left', color='#333333')
ax.set_xlabel('Efficiency (Yield per Head in THB)', fontsize=12, fontweight='bold', labelpad=15)
ax.set_ylabel('Market Share (% Revenue Contribution)', fontsize=12, fontweight='bold', labelpad=15)

# ลบ Scientific Notation และใส่ลูกน้ำ
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))

# เพิ่ม Margin ให้ข้อความไม่ตกขอบ
plt.margins(0.15)
plt.tight_layout()
plt.savefig('visualizations/Figure_8_Quadrant_Professional.png', dpi=300)
plt.show()