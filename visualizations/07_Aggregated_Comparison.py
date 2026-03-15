import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.lines import Line2D

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
    print(f"❌ Error: ไม่พบไฟล์ที่ {file_path}")
    exit()

df = pd.read_csv(file_path)

# --- ระบบค้นหาชื่อคอลัมน์อัตโนมัติ ---
def find_col(keywords, columns):
    for col in columns:
        if all(k.lower() in col.lower() for k in keywords): return col
    return None

col_thai_rev = find_col(['thai', 'revenue'], df.columns)
col_fore_rev = find_col(['foreign', 'revenue'], df.columns)
col_city_type = find_col(['city', 'type', 'en'], df.columns)
col_price_idx = find_col(['price', 'index'], df.columns)

# 2. CALCULATE REAL REVENUE
df['thai_rev_real'] = df[col_thai_rev] / (df[col_price_idx] / 100)
df['fore_rev_real'] = df[col_fore_rev] / (df[col_price_idx] / 100)
df = df.dropna(subset=[col_city_type])

# 3. AGGREGATE BY CITY TYPE
type_agg = df.groupby(col_city_type)[['thai_rev_real', 'fore_rev_real']].sum()
if 'Major City' in type_agg.index and 'Secondary City' in type_agg.index:
    type_agg = type_agg.loc[['Major City', 'Secondary City']]

# 4. VISUALIZATION
fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')

labels = type_agg.index.tolist()
thai_revs = type_agg['thai_rev_real'].values
fore_revs = type_agg['fore_rev_real'].values
total_revs = thai_revs + fore_revs

# คำนวณ % สำหรับการวาง Label
pct_thai = (thai_revs / total_revs) * 100
pct_fore = (fore_revs / total_revs) * 100

# กำหนดคู่สี (Blue for Major, Green for Secondary)
colors_thai = ['#90CAF9', '#A8E6CF']  # ฟ้าอ่อน, มิ้นต์
colors_fore = ['#1565C0', '#1B5E20']  # น้ำเงินเข้ม, เขียวเข้ม

# วาดกราฟ 100% Stacked
ax.bar(labels, pct_thai, color=colors_thai, width=0.5, label='Domestic (Thai)')
ax.bar(labels, pct_fore, bottom=pct_thai, color=colors_fore, width=0.5, label='International (Foreign)')

# 5. ใส่ Data Labels (Value + %) และ Total ยอดรวมบนหัว
for i in range(len(labels)):
    # --- ยอดรวมบนหัวแท่ง (Total Value) ---
    ax.text(i, 102, f'Total: {total_revs[i]:,.0f} M THB', 
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='black')

    # --- Label ไทย (ด้านล่าง) ---
    ax.annotate(f'{thai_revs[i]:,.0f}\n({pct_thai[i]:.1f}%)', 
                (i, pct_thai[i]/2), 
                ha='center', va='center', 
                color='black' if i == 1 else 'black', # ปรับสีตามความเหมาะสม
                fontsize=10, fontweight='bold')
    
    # --- Label ต่างชาติ (ด้านบน) ---
    ax.annotate(f'{fore_revs[i]:,.0f}\n({pct_fore[i]:.1f}%)', 
                (i, pct_thai[i] + pct_fore[i]/2), 
                ha='center', va='center', 
                color='white', 
                fontsize=10, fontweight='bold')

# 6. ตกแต่งหัวข้อและแกน (ดำสนิท)
plt.title('Primary vs. Secondary Cities Structure Analysis\nRevenue Composition & Market Efficiency Gap', 
          fontsize=18, fontweight='bold', pad=45, color='black')
plt.ylabel('Market Composition Percentage (%)', fontsize=12, fontweight='bold', color='black')
plt.xlabel('City Tier', fontsize=12, fontweight='bold', color='black')
plt.xticks(fontsize=11, fontweight='bold', color='black')
ax.set_ylim(0, 115) # เผื่อที่ว่างด้านบนให้ Total Label

# Legend แบบมีกรอบสวยๆ
legend_elements = [
    Line2D([0], [0], color='#90CAF9', lw=8, label='Major City (Domestic)'),
    Line2D([0], [0], color='#1565C0', lw=8, label='Major City (International)'),
    Line2D([0], [0], color='#A8E6CF', lw=8, label='Secondary City (Domestic)'),
    Line2D([0], [0], color='#1B5E20', lw=8, label='Secondary City (International)')
]
ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), 
          ncol=2, frameon=True, fontsize=9)

plt.grid(axis='y', linestyle='--', alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

# SAVE
os.makedirs('visualizations', exist_ok=True)
output_path = 'visualizations/Figure_Primary_vs_Secondary.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ แก้ไขเรียบร้อย! กราฟสวยและข้อมูลครบถ้วนแล้วครับที่: {output_path}")