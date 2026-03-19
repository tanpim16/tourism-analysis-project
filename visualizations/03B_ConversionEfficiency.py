# ──────────────────────────────────────────────────────
# 0. IMPORTS
# ──────────────────────────────────────────────────────
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe

# Label auto adjustment
try:
    from adjustText import adjust_text
except ImportError:
    print("⚠️ Warning: adjustText not found. Please 'pip install adjustText'")
    adjust_text = None


# ──────────────────────────────────────────────────────
# 1. STYLE
# ──────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA',
    'axes.grid': True,
    'grid.color': "#F3EDED",
    'grid.linewidth': 1.2,
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
})


# ──────────────────────────────────────────────────────
# 2. LOAD DATA
# ──────────────────────────────────────────────────────
file_path = 'data/processed/final_master_with_trends.csv'
if not os.path.exists(file_path):
    file_path = 'final_master_with_trends.csv'

df_raw = pd.read_csv(file_path)


# ──────────────────────────────────────────────────────
# 3. DATA CLEANING & PATCH
# ──────────────────────────────────────────────────────

# Fix Nakhon Ratchasima
df_raw.loc[df_raw['ProvinceThai'] == 'นครราชสีมา', 'ProvinceEN'] = 'Nakhon Ratchasima'
df_raw.loc[df_raw['ProvinceThai'] == 'นครราชสีมา', 'City_type_EN'] = 'Primary City'

# Detect columns
prov_cols = [c for c in df_raw.columns if 'prov' in c.lower() and 'en' in c.lower()]
province_col = prov_cols[0] if prov_cols else 'ProvinceEN'

city_type_col = 'City_type_EN' if 'City_type_EN' in df_raw.columns else 'City_type'

# Normalize
df_raw[province_col] = df_raw[province_col].astype(str).str.strip()

df_raw['total_search'] = (
    df_raw['search_thai'].fillna(0) +
    df_raw['search_foreign'].fillna(0)
)

df_raw['total_visitors'] = df_raw['total_visitors'].fillna(0)


# ──────────────────────────────────────────────────────
# 4. AGGREGATION
# ──────────────────────────────────────────────────────
df = df_raw.groupby(province_col).agg(
    total_search=('total_search', 'mean'),
    total_visitors=('total_visitors', 'mean'),
    city_type=(city_type_col, 'first'),
).reset_index()

# Remove Bangkok
df_other = df[
    ~df[province_col].str.contains('Bangkok|กรุงเทพ', case=False, na=False)
].copy()

print(f"📊 Total Unique Provinces: {len(df)}")
print(f"📍 Points to plot (Target 76): {len(df_other)}")


# ──────────────────────────────────────────────────────
# 5. METRICS CALCULATION
# ──────────────────────────────────────────────────────
s_med = df_other['total_search'].median()
v_med = df_other['total_visitors'].median()

df_other['dist'] = np.sqrt(
    (df_other['total_search'] - s_med) ** 2 +
    (df_other['total_visitors'] - v_med) ** 2
)

df_other['gap_score'] = df_other['total_search'] / (df_other['total_visitors'] + 1)

df_other['in_gap'] = (
    (df_other['total_search'] >= s_med) &
    (df_other['total_visitors'] < v_med)
)

COLORS = {
    'Major': {'dot': '#4A90D9', 'text': '#1A5276'},
    'Secondary': {'dot': '#5BAD6F', 'text': '#1E8449'},
    'Gap': {'dot': '#E05C5C', 'text': '#C0392B'},
}


# ──────────────────────────────────────────────────────
# 6. FIGURE SETUP & TITLE
# ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
ax.set_facecolor('#FAFAFA')

fig.suptitle(
    'Thailand Tourism Province Analysis: Search Intent vs. Total Arrivals',
    fontsize=16,
    fontfamily='sans-serif',
    fontweight='bold',
    color='#2C3E50',
    y=0.96
)

xmax_data = df_other['total_search'].max() * 1.15
ymax_data = df_other['total_visitors'].max() * 1.15

ax.set_xlim(-2, xmax_data)
ax.set_ylim(-v_med * 0.1, ymax_data)


# ──────────────────────────────────────────────────────
# 7. BACKGROUND & GRID LINES
# ──────────────────────────────────────────────────────
ax.add_patch(
    plt.Rectangle(
        (s_med, 0),
        xmax_data - s_med,
        v_med,
        facecolor='#FFF0F0',
        alpha=0.7,
        zorder=0
    )
)

ax.axhline(v_med, color='#CCCCCC', linestyle='--', linewidth=1.0)
ax.axvline(s_med, color='#CCCCCC', linestyle='--', linewidth=1.0)


# ──────────────────────────────────────────────────────
# 8. SCATTER PLOT
# ──────────────────────────────────────────────────────
for _, row in df_other.iterrows():

    if row['in_gap']:
        color, size, alpha, z = COLORS['Gap']['dot'], 110, 0.9, 4

    elif 'Major' in str(row['city_type']):
        color, size, alpha, z = COLORS['Major']['dot'], 85, 0.6, 3

    else:
        color, size, alpha, z = COLORS['Secondary']['dot'], 55, 0.6, 2

    ax.scatter(
        row['total_search'],
        row['total_visitors'],
        s=size,
        color=color,
        alpha=alpha,
        edgecolors='white',
        linewidth=0.6,
        zorder=z
    )


# ──────────────────────────────────────────────────────
# 9. LABELS
# ──────────────────────────────────────────────────────
all_texts = []

quad_config = [
    (df_other['in_gap'], 'gap_score', 8),
    ((df_other['total_search'] < s_med) & (df_other['total_visitors'] >= v_med), 'dist', 4),
    ((df_other['total_search'] >= s_med) & (df_other['total_visitors'] >= v_med), 'dist', 5),
    ((df_other['total_search'] < s_med) & (df_other['total_visitors'] < v_med), 'dist', 5),
]

for cond, sort_col, n in quad_config:
    subset = df_other[cond].nlargest(n, sort_col)

    for _, row in subset.iterrows():

        t_color = (
            COLORS['Major']['text']
            if 'Major' in str(row['city_type'])
            else COLORS['Secondary']['text']
        )

        txt = ax.text(
            row['total_search'],
            row['total_visitors'],
            row[province_col],
            fontsize=9,
            fontweight='bold',
            color=t_color,
            zorder=5,
            path_effects=[
                pe.withStroke(linewidth=2.5, foreground='white')
            ]
        )

        all_texts.append(txt)

# Adjust text
if adjust_text:
    adjust_text(
        all_texts,
        ax=ax,
        expand_points=(2.8, 2.8),
        expand_text=(2.0, 2.0),
        force_text=3.0,
        arrowprops=dict(arrowstyle='-', color='#BBBBBB', lw=0.7)
    )


# ──────────────────────────────────────────────────────
# 10. ZONE LABELS
# ──────────────────────────────────────────────────────
ax.text(
    0.98, 0.96,
    'High Potential\nHigh Arrivals · High Search',
    transform=ax.transAxes,
    ha='right',
    va='top',
    fontsize=10,
    color='#2471A3',
    fontweight='bold'
)

ax.text(
    0.02, 0.96,
    'Word-of-Mouth\nHigh Arrivals · Low Search',
    transform=ax.transAxes,
    ha='left',
    va='top',
    fontsize=10,
    color='#27ae60',
    fontweight='bold'
)

ax.text(
    0.05, 0.20,
    'Undiscovered\nLow Arrivals · Low Search\n(Emerging Area)',
    transform=ax.transAxes,
    ha='left',
    va='top',
    fontsize=10,
    color='#666666',
    fontweight='bold',
    bbox=dict(
        boxstyle='round,pad=0.5',
        facecolor='#F2F3F4',
        edgecolor='#D5D8DC',
        linewidth=1.5
    )
)

ax.text(
    0.95, 0.20,
    '⚠️ Digital Gap\nHigh Search · Low Arrivals\n(Action Required)',
    transform=ax.transAxes,
    ha='right',
    va='top',
    fontsize=11,
    color='#C0392B',
    fontweight='bold',
    bbox=dict(
        boxstyle='round,pad=0.5',
        facecolor='#FFF0F0',
        edgecolor='#F5B7B1',
        linewidth=1.5
    )
)

ax.text(
    0.02, 0.51,
    '* Bangkok excluded',
    transform=ax.transAxes,
    fontsize=9,
    color='#BBBBBB',
    style='italic'
)


# ──────────────────────────────────────────────────────
# 11. AXES & LEGEND
# ──────────────────────────────────────────────────────
ax.set_xlabel(
    'Search Intent (Digital Interest)',
    fontsize=12,
    fontweight='bold'
)

# 🆕 ปรับชื่อแกน Y เป็น Millions
ax.set_ylabel(
    'Total Arrivals (Millions)',
    fontsize=12,
    fontweight='bold'
)

# 🆕 ปรับตัวเลขบนแกน Y ให้หารด้วย 1 ล้าน (แสดงเป็น 0.0, 0.5, 1.0, ...)
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, _: f'{x/1e6:.1f}'
    )
)

ax.legend(
    handles=[
        mpatches.Patch(color=COLORS['Major']['dot'], label='Major City'),
        mpatches.Patch(color=COLORS['Secondary']['dot'], label='Secondary City'),
        mpatches.Patch(color=COLORS['Gap']['dot'], label='Digital Gap province'),
    ],
    loc='upper right',
    bbox_to_anchor=(0.98, 0.88),
    fontsize=10,
    frameon=True,
    shadow=True
)

plt.tight_layout(rect=[0, 0, 1, 0.95])


# ──────────────────────────────────────────────────────
# 12. SAVE OUTPUT
# ──────────────────────────────────────────────────────
output_dir = 'visualizations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
output_path = os.path.join(output_dir, 'Figure_3_Conversion_Efficiency.png')

plt.savefig(
    output_path,
    facecolor='white',
    bbox_inches='tight',
    dpi=300
)

plt.show()

print(f"🚀 Success! Figure saved to: {output_path}")
print(f"✅ Final Check: {len(df_other)} provinces plotted + Bangkok = 77 total.")