import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap
import os

# ─────────────────────────────────────────
# 1. DATA PREP (Stable Logic)
# ─────────────────────────────────────────
df_main = pd.read_csv('data/processed/master_tourism_analysis.csv')
prov_list = pd.read_csv('data/processed/ProvinceThailandList.csv')

name_map = {
    'Chai Nat':'Chainat','Lop Buri':'Lopburi','Sing Buri':'Singburi',
    'Prachin Buri':'Prachinburi','Nong Bua Lam Phu':'Nong Bua Lamphu',
    'Si Sa Ket':'Si Saket','Suphan Buri':'Suphanburi',
    'Sa Kaeo': 'Sra Kaeo', 'Buriram': 'Buri Ram'
}
df_main['ProvinceEN'] = df_main['ProvinceEN'].str.strip().replace(name_map)
prov_list['ProvinceEN'] = prov_list['ProvinceEN'].str.strip().replace(name_map)

df_agg = df_main.groupby('ProvinceEN').agg({'total_visitors':'mean','real_revenue':'mean'}).reset_index()
sec_base = prov_list[prov_list['City_type_EN'].str.contains('Secondary', na=False, case=False)].copy()
sec = pd.merge(sec_base[['ProvinceEN','Region_EN']], df_agg, on='ProvinceEN', how='left').fillna(0)

sec['yield_per_head'] = (sec['real_revenue']*1e6) / sec['total_visitors'].replace(0,1)
sec['contribution_pct'] = (sec['real_revenue'] / sec['real_revenue'].sum()) * 100
valid = sec[sec['total_visitors']>0]
x_mid, y_mid = valid['yield_per_head'].median(), valid['contribution_pct'].median()

def classify(row):
    if row['total_visitors']==0: return 'EMERGING'
    hy, hc = row['yield_per_head']>=x_mid, row['contribution_pct']>=y_mid
    if hy and hc: return 'STARS'
    if not hy and hc: return 'MASS MARKET'
    if hy and not hc: return 'PREMIUM NICHE'
    return 'EMERGING'
sec['Quadrant'] = sec.apply(classify, axis=1)

# ─────────────────────────────────────────
# 2. THE VISUAL (Symmetrical & Modernized)
# ─────────────────────────────────────────
plt.close('all')
fig = plt.figure(figsize=(15, 12), facecolor='#F8F9FA') 

# Title & Subtitle (จัดวางใหม่ให้ชิดขึ้น)
plt.text(0.5, 0.965, 'SECONDARY CITY STRATEGIC PORTFOLIO', 
         ha='center', fontsize=22, fontweight='800', color='#1A5276', transform=fig.transFigure)
plt.text(0.5, 0.94, f'Median Efficiency: ฿{x_mid:,.0f}  |  Median Market Share: {y_mid:.2f}%', 
         ha='center', fontsize=11, color='#5D6D7E', transform=fig.transFigure)

# --- Grid Configuration (คำนวณพิกัดให้เท่ากันเป๊ะ) ---
QUADS = ['STARS', 'PREMIUM NICHE', 'MASS MARKET', 'EMERGING']
COLORS = {'STARS': '#2471A3', 'PREMIUM NICHE': '#7D3C98', 'MASS MARKET': '#BA4A00', 'EMERGING': '#626567'}
BG_COLORS = {'STARS': '#EBF5FB', 'PREMIUM NICHE': '#F5EEF8', 'MASS MARKET': '#FDF2E9', 'EMERGING': '#F4F6F7'}

# พิกัดกล่อง (x, y, width, height) - เว้น Gap 0.02 ระหว่างกล่อง และ Margin 0.03
panels = [
    (0.03, 0.49, 0.455, 0.42), (0.515, 0.49, 0.455, 0.42), 
    (0.03, 0.05, 0.455, 0.42), (0.515, 0.05, 0.455, 0.42)
]

for i, quad in enumerate(QUADS):
    x0, y0, w, h = panels[i]
    color = COLORS[quad]
    bg_c = BG_COLORS[quad]
    q_df = sec[sec['Quadrant']==quad]
    count = len(q_df)

    # สร้าง Axis สำหรับแต่ละกล่อง
    ax = fig.add_axes([x0, y0, w, h])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')

    # 1. วาดตัวกล่อง (ขอบมน FancyBbox)
    rect = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03",
                                   facecolor='white', edgecolor='#D5DBDB', lw=1, alpha=1)
    ax.add_patch(rect)

    # 2. แถบ Header (สีอ่อนแยกตามกลุ่ม)
    header = patches.FancyBboxPatch((0, 0.88), 1, 0.12, boxstyle="round,pad=0,rounding_size=0.03",
                                     facecolor=bg_c, edgecolor='none', alpha=0.5)
    ax.add_patch(header)

    # 3. ใส่ Text หมวดหมู่
    ax.text(0.04, 0.94, quad, fontsize=14, fontweight='900', color=color, va='center')
    ax.text(0.96, 0.94, f'{count} Cities', fontsize=11, fontweight='bold', color=color, va='center', ha='right')

    # 4. รายชื่อจังหวัด (Grouping by Region)
    y_cursor = 0.83
    for region in sorted(q_df['Region_EN'].unique()):
        provs = q_df[q_df['Region_EN']==region]['ProvinceEN'].sort_values().tolist()
        
        # Region Tag (เล็กและคม)
        ax.text(0.04, y_cursor, region.upper(), fontsize=7.5, fontweight='bold', color='#909497', va='top')
        y_cursor -= 0.04
        
        # Province Names (จัดบรรทัดใหม่ให้กระชับ)
        wrapped = textwrap.fill(', '.join(provs), width=52) 
        ax.text(0.04, y_cursor, wrapped, fontsize=9.5, color='#2C3E50', va='top', linespacing=1.4)
        y_cursor -= 0.045 * (wrapped.count('\n') + 1) + 0.025

# ─────────────────────────────────────────
# 3. EXPORT
# ─────────────────────────────────────────
os.makedirs('visualizations', exist_ok=True)
plt.savefig('visualizations/Figure_9_Strategic_Summary.png', 
            dpi=300, bbox_inches='tight', pad_inches=0.05)
plt.close()

print("✅ Perfect-Aligned Version Ready! Check 'visualizations/Figure_9_Strategic_Summary.png'")