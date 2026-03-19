import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# ─── Load Data ────────────────────────────────────────────────────────────────
file_path = 'data/processed/final_master_with_trends.csv'

if not os.path.exists(file_path):
    print(f"❌ Error: ไม่พบไฟล์ '{file_path}'")
    exit()

df = pd.read_csv(file_path)

# ─── Column Detection ─────────────────────────────────────────────────────────
revenue_candidates = [c for c in df.columns if 'revenue' in c.lower() and 'real' in c.lower()]
if not revenue_candidates:
    revenue_candidates = [c for c in df.columns if 'revenue' in c.lower()]

if not revenue_candidates:
    print("❌ ไม่พบคอลัมน์รายได้:", df.columns.tolist())
    exit()

target_revenue_col = revenue_candidates[0]
print(f"✅ Using column: {target_revenue_col}")

# ─── Compute Yield ────────────────────────────────────────────────────────────
df['yield_per_head'] = (df[target_revenue_col] * 1_000_000) / df['total_visitors']

# ─── Aggregate ────────────────────────────────────────────────────────────────
yield_stats = (
    df.groupby('City_type_EN')['yield_per_head']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

# ─── Plot ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="white")

fig, ax = plt.subplots(figsize=(10, 8))

palette = [
    "#1084e3" if 'Major' in city else "#139829"
    for city in yield_stats['City_type_EN']
]

sns.barplot(
    data=yield_stats,
    x='City_type_EN',
    y='yield_per_head',
    palette=palette,
    edgecolor=".2",
    linewidth=1.5,
    ax=ax
)

# ─── Value Labels (fontsize = 8) ──────────────────────────────────────────────
for p in ax.patches:
    height = p.get_height()
    ax.annotate(
        f'{height:,.0f}',
        (p.get_x() + p.get_width() / 2., height),
        ha='center',
        va='bottom',
        xytext=(0, 6),
        textcoords='offset points',
        fontsize=8,
        fontweight='bold',
        color='#2c3e50'
    )

# ─── Title ────────────────────────────────────────────────────────────────────
fig.suptitle(
    'Average Yield per Head (Real Revenue per Visitor)',
    fontsize=16,
    fontweight='bold',
    y=0.90
)

# ─── Axis ─────────────────────────────────────────────────────────────────────
ax.set_xlabel('')
ax.set_ylabel(
    'Average Real Revenue (THB per Person)',
    fontsize=10,
    fontweight='normal',
    labelpad=8
)

ax.tick_params(axis='x', labelsize=9)
ax.tick_params(axis='y', labelsize=9)

# ─── ✅ FIX Y = 8000 ──────────────────────────────────────────────────────────
ax.set_ylim(0, 8000)
ax.set_yticks(range(0, 8001, 1000))

# ─── Grid ─────────────────────────────────────────────────────────────────────
ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7')
ax.xaxis.grid(False)

sns.despine(left=True)

# ─── Layout (tight + balanced) ────────────────────────────────────────────────
plt.subplots_adjust(
    top=0.85,
    bottom=0.12,
    left=0.10,
    right=0.95
)

# ─── Footnote ────────────────────────────────────────────────────────────────
plt.text(
    0.5, -0.12,
    "* Yield = (Real Revenue × 1M) / Total Visitors",
    ha='center',
    va='center',
    transform=ax.transAxes,
    fontsize=9,
    style='italic',
    color='#7f8c8d'
)

# ─── Save ─────────────────────────────────────────────────────────────────────
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

output_file = 'visualizations/Figure_1C_Yield_efficiency.png'

plt.savefig(
    output_file,
    facecolor='white',
    transparent=False,
    bbox_inches='tight',
    dpi=300
)

print("📊 DONE")
plt.show()