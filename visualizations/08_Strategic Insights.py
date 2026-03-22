import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import os

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

# --- 1. LOAD & PREP ---
df_main   = pd.read_csv('data/processed/master_tourism_analysis.csv')
province_list = pd.read_csv('data/processed/ProvinceThailandList.csv')

df_main['ProvinceEN'] = df_main['ProvinceEN'].str.strip()
province_list['ProvinceEN'] = province_list['ProvinceEN'].str.strip()

name_map = {
    'Chai Nat': 'Chainat', 'Lop Buri': 'Lopburi', 'Sing Buri': 'Singburi',
    'Prachin Buri': 'Prachinburi', 'Nong Bua Lam Phu': 'Nong Bua Lamphu',
    'Si Sa Ket': 'Si Saket', 'Suphan Buri': 'Suphanburi', 'Buri Ram': 'Buriram'
}
df_main['ProvinceEN'] = df_main['ProvinceEN'].replace(name_map)

df_agg = df_main.groupby('ProvinceEN').agg({'total_visitors': 'mean', 'real_revenue': 'mean'}).reset_index()
secondary_base = province_list[province_list['City_type_EN'].str.contains('Secondary', na=False, case=False)].copy()
secondary_only = pd.merge(secondary_base[['ProvinceEN']], df_agg, on='ProvinceEN', how='left').fillna(0)

secondary_only['yield_per_head'] = (secondary_only['real_revenue'] * 1000000) / secondary_only['total_visitors'].replace(0, 1)
secondary_only['contribution_pct'] = (secondary_only['real_revenue'] / secondary_only['real_revenue'].sum()) * 100

valid_data = secondary_only[secondary_only['total_visitors'] > 0]
x_mid = valid_data['yield_per_head'].median()
y_mid = valid_data['contribution_pct'].median()

def classify(row):
    if row['total_visitors'] == 0: return 'EMERGING'
    if row['yield_per_head'] >= x_mid and row['contribution_pct'] >= y_mid: return 'STARS'
    if row['yield_per_head'] < x_mid and row['contribution_pct'] >= y_mid: return 'MASS MARKET'
    if row['yield_per_head'] >= x_mid and row['contribution_pct'] < y_mid: return 'PREMIUM NICHE'
    return 'EMERGING'

secondary_only['Quadrant'] = secondary_only.apply(classify, axis=1)

# --- 2. THE VISUALS ---
fig, ax = plt.subplots(figsize=(13, 10), facecolor='#FAFAFA')
sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.5})

QUAD_COLOR = {
    'STARS':         '#6A9FBF',  # soft steel blue
    'MASS MARKET':   '#E8A87C',  # soft terracotta
    'PREMIUM NICHE': '#A886C0',  # soft lavender
    'EMERGING':      '#7EBF9A',  # soft sage green
}

for quad, color in QUAD_COLOR.items():
    sub = secondary_only[secondary_only['Quadrant'] == quad]
    ax.scatter(sub['yield_per_head'], sub['contribution_pct'],
               s=150, color=color, alpha=0.7,
               edgecolors='white', linewidth=0.6, label=quad)

ax.legend(title='Strategic Group', fontsize=9, title_fontsize=9,
          loc='center right', framealpha=0.85, edgecolor='#DDDDDD')

ax.axvline(x=x_mid, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
ax.axhline(y=y_mid, color='black', linestyle='-', linewidth=0.8, alpha=0.3)

# --- 3. LABELING ---
labels = set(
    secondary_only[secondary_only['total_visitors'] > 0]
    .sort_values('contribution_pct', ascending=False)
    .groupby('Quadrant', group_keys=False)
    .head(2)['ProvinceEN']
)

QUAD_OFFSET = {
    'STARS':         [( 10,  8), ( 10, -14)],
    'MASS MARKET':   [(-10,  8), (-10, -14)],
    'PREMIUM NICHE': [( 10,  8), ( 10, -14)],
    'EMERGING':      [(-10,  8), (-10, -14)],
}
quad_counter = {q: 0 for q in QUAD_OFFSET}

top2_df = (
    secondary_only[secondary_only['total_visitors'] > 0]
    .sort_values('contribution_pct', ascending=False)
    .groupby('Quadrant', group_keys=False)
    .head(2)
    .reset_index(drop=True)
)

for _, row in top2_df.iterrows():
    q   = row['Quadrant']
    idx = quad_counter[q]
    ox, oy = QUAD_OFFSET[q][idx]
    quad_counter[q] += 1
    ax.annotate(row['ProvinceEN'], (row['yield_per_head'], row['contribution_pct']),
                xytext=(ox, oy), textcoords='offset points', fontsize=11,
                fontweight='bold', color=QUAD_COLOR[q],
                ha='left' if ox > 0 else 'right',
                path_effects=[
                    __import__('matplotlib.patheffects', fromlist=['withStroke'])
                    .withStroke(linewidth=3, foreground='white')
                ])

# --- 4. QUADRANT BOXES ---
bbox_style = dict(boxstyle="round4,pad=0.6", fc="white", ec="#CCCCCC", alpha=0.8, lw=1)
ax.text(0.97, 0.97, 'STARS\nHigh Value & Volume', transform=ax.transAxes, ha='right', va='top', fontsize=12, fontweight='bold', color='#2E4053', bbox=bbox_style)
ax.text(0.03, 0.97, 'MASS MARKET\nHigh Volume, Low Value', transform=ax.transAxes, ha='left', va='top', fontsize=12, fontweight='bold', color='#A04000', bbox=bbox_style)
ax.text(0.97, 0.03, 'PREMIUM NICHE\nHigh Value, Low Volume', transform=ax.transAxes, ha='right', va='bottom', fontsize=12, fontweight='bold', color='#512E5F', bbox=bbox_style)
ax.text(0.03, 0.03, 'EMERGING\nDeveloping Potential', transform=ax.transAxes, ha='left', va='bottom', fontsize=12, fontweight='bold', color='#707B7C', bbox=bbox_style)

# --- 5. FINISHING ---
ax.set_title('Secondary City Portfolio Analysis', fontsize=20, fontweight='bold', pad=25, loc='left', color='#333333')
ax.set_xlabel('Efficiency (Yield per Head in THB)', fontsize=12, fontweight='bold', labelpad=15)
ax.set_ylabel('Market Share (% Revenue Contribution)', fontsize=12, fontweight='bold', labelpad=15)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))

plt.margins(0.15)
plt.tight_layout()
os.makedirs('visualizations', exist_ok=True)
plt.savefig('visualizations/Figure_8_Quadrant_Professional.png', dpi=300, bbox_inches='tight')
plt.close()
print("Done")