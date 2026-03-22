import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.lines import Line2D
import matplotlib.ticker as mtick
import numpy as np

# ─── Global Style + Font ─────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA',
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
})

# 1. LOAD DATA
file_path = 'data/processed/final_master_with_trends.csv'
if not os.path.exists(file_path):
    print(f"❌ Error: ไม่พบไฟล์ที่ {file_path}")
    exit()

df = pd.read_csv(file_path)

# --- Auto detect columns ---
def find_col(keywords, columns):
    for col in columns:
        if all(k.lower() in col.lower() for k in keywords):
            return col
    return None

col_thai_rev = find_col(['thai', 'revenue'], df.columns)
col_fore_rev = find_col(['foreign', 'revenue'], df.columns)
col_city_type = find_col(['city', 'type', 'en'], df.columns)
col_price_idx = find_col(['price', 'index'], df.columns)

# 2. CALCULATE REAL REVENUE
df['thai_rev_real'] = df[col_thai_rev] / (df[col_price_idx] / 100)
df['fore_rev_real'] = df[col_fore_rev] / (df[col_price_idx] / 100)
df = df.dropna(subset=[col_city_type])

# 3. AGGREGATE
type_agg = df.groupby(col_city_type)[['thai_rev_real', 'fore_rev_real']].sum()

if 'Major City' in type_agg.index and 'Secondary City' in type_agg.index:
    type_agg = type_agg.loc[['Major City', 'Secondary City']]

# 4. VISUALIZATION
fig, ax = plt.subplots(figsize=(10, 8))

labels = type_agg.index.tolist()
thai_revs = type_agg['thai_rev_real'].values
fore_revs = type_agg['fore_rev_real'].values
total_revs = thai_revs + fore_revs

pct_thai = (thai_revs / total_revs) * 100
pct_fore = (fore_revs / total_revs) * 100

colors_thai = ['#90CAF9', '#A8E6CF']
colors_fore = ['#1565C0', '#1B5E20']

ax.bar(labels, pct_thai, color=colors_thai, width=0.5)
ax.bar(labels, pct_fore, bottom=pct_thai, color=colors_fore, width=0.5)

# 5. VALUE LABELS (6 Bold)
for i in range(len(labels)):

    ax.text(i, 102,
            f'Total: {total_revs[i]:,.0f} M THB',
            ha='center', va='bottom',
            fontsize=10, fontweight='bold')

    ax.annotate(
        f'{thai_revs[i]:,.0f}\n({pct_thai[i]:.1f}%)',
        (i, pct_thai[i] / 2),
        ha='center', va='center',
        fontsize=10, fontweight='bold', color='black'
    )

    ax.annotate(
        f'{fore_revs[i]:,.0f}\n({pct_fore[i]:.1f}%)',
        (i, pct_thai[i] + pct_fore[i] / 2),
        ha='center', va='center',
        fontsize=10, fontweight='bold', color='white'
    )

# 6. TITLE (ใช้ suptitle กันหาย 100%)
fig.suptitle(
    'Market Structure Analysis (Primary vs. Secondary)',
    fontsize=16,
    fontweight='bold',
    y=0.87
)

# Subplot title
ax.set_title('', fontsize=12, fontweight='bold')

# Axis
plt.ylabel('Market Consumption', fontsize=10)
plt.xticks(fontsize=12, fontweight='bold')

# Y scale + ticks
ax.set_ylim(0, 115)
ax.set_yticks(np.arange(0, 101, 20))
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

# Grid (horizontal subtle)
ax.grid(axis='y', linestyle='--', linewidth=0.8, alpha=0.25)

# Legend
legend_elements = [
    Line2D([0], [0], color='#90CAF9', lw=10, label='Major City (Domestic)'),
    Line2D([0], [0], color='#1565C0', lw=10, label='Major City (International)'),
    Line2D([0], [0], color='#A8E6CF', lw=10, label='Secondary City (Domestic)'),
    Line2D([0], [0], color='#1B5E20', lw=10, label='Secondary City (International)')
]

ax.legend(
    handles=legend_elements,
    loc='upper center',
    bbox_to_anchor=(0.5, -0.1),
    ncol=2,
    frameon=True,
    fontsize=9,
    title='Market Segment',
    title_fontsize=10
)

# Layout fix (กันชน legend + title)
plt.tight_layout()
plt.subplots_adjust(top=0.88)

# SAVE
os.makedirs('visualizations', exist_ok=True)
output_path = 'visualizations/Figure_7_Primary_vs_Secondary.png'

plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ เรียบร้อย: {output_path}")