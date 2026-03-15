import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
import os

# Label auto adjustment
try:
    from adjustText import adjust_text
except ImportError:
    adjust_text = None


# ─── Style ─────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA',
    'axes.grid': True,
    'grid.color': '#FFFFFF',
    'grid.linewidth': 1.2,
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
})

# ─── 1. LOAD DATA ───────────────────────────────────────
df_raw = pd.read_csv('data/processed/final_master_with_trends.csv')

prov_cols = [c for c in df_raw.columns if 'prov' in c.lower() and 'en' in c.lower()]
if not prov_cols:
    prov_cols = [c for c in df_raw.columns if 'prov' in c.lower()]

province_col = prov_cols[0] if prov_cols else None
city_type_col = 'City_type_EN' if 'City_type_EN' in df_raw.columns else 'City_type'

df_raw['total_search'] = df_raw['search_thai'].fillna(0) + df_raw['search_foreign'].fillna(0)
df_raw['total_visitors'] = df_raw['total_visitors'].fillna(0)

# Aggregate
df = df_raw.groupby(province_col).agg(
    total_search=('total_search', 'mean'),
    total_visitors=('total_visitors', 'mean'),
    city_type=(city_type_col, 'first'),
).reset_index()

# Remove Bangkok
df_other = df[~df[province_col].str.contains('Bangkok', na=False)].copy()

# Medians
s_med = df_other['total_search'].median()
v_med = df_other['total_visitors'].median()

# Metrics
df_other['dist'] = ((df_other['total_search'] - s_med)**2 + (df_other['total_visitors'] - v_med)**2)**0.5
df_other['gap_score'] = df_other['total_search'] / (df_other['total_visitors'] + 1)
df_other['in_gap'] = (df_other['total_search'] >= s_med) & (df_other['total_visitors'] < v_med)

COLORS = {
    'Major': {'dot': '#4A90D9', 'text': '#1A5276'},
    'Secondary': {'dot': '#5BAD6F', 'text': '#1E8449'},
    'Gap': {'dot': '#E05C5C', 'text': '#C0392B'},
}

# ─── 2. FIGURE ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 9), facecolor='white')
ax.set_facecolor('#FAFAFA')

xmax_data = df_other['total_search'].max() * 1.12
ymax_data = df_other['total_visitors'].max() * 1.15

ax.set_xlim(-2, xmax_data)
ax.set_ylim(-v_med * 0.1, ymax_data)

# Shading digital gap area
ax.add_patch(
    plt.Rectangle((s_med, 0),
                  xmax_data - s_med,
                  v_med,
                  facecolor='#FFF0F0',
                  edgecolor='none',
                  zorder=0,
                  alpha=0.7)
)

ax.axhline(v_med, color='#CCCCCC', linestyle='--', linewidth=1.0)
ax.axvline(s_med, color='#CCCCCC', linestyle='--', linewidth=1.0)

# ─── 3. DOTS ───────────────────────────────────────────
for _, row in df_other.iterrows():

    if row['in_gap']:
        color, size, alpha, z = COLORS['Gap']['dot'], 100, 0.85, 4

    elif 'Major' in str(row['city_type']):
        color, size, alpha, z = COLORS['Major']['dot'], 75, 0.5, 3

    else:
        color, size, alpha, z = COLORS['Secondary']['dot'], 45, 0.5, 2

    ax.scatter(
        row['total_search'],
        row['total_visitors'],
        s=size,
        color=color,
        alpha=alpha,
        edgecolors='white',
        linewidth=0.5,
        zorder=z
    )

# ─── 4. LABELS ─────────────────────────────────────────
all_texts = []

quad_config = [
    (df_other['in_gap'], 'gap_score', 6),
    ((df_other['total_search'] < s_med) & (df_other['total_visitors'] >= v_med), 'dist', 3),
    ((df_other['total_search'] >= s_med) & (df_other['total_visitors'] >= v_med), 'dist', 3),
    ((df_other['total_search'] < s_med) & (df_other['total_visitors'] < v_med), 'dist', 4),
]

for cond, sort_col, n in quad_config:

    for _, row in df_other[cond].nlargest(n, sort_col).iterrows():

        if 'Major' in str(row['city_type']):
            t_color = COLORS['Major']['text']
        else:
            t_color = COLORS['Secondary']['text']

        txt = ax.text(
            row['total_search'],
            row['total_visitors'],
            row[province_col],
            fontsize=8.5,
            fontweight='bold',
            color=t_color,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')],
            zorder=5
        )

        all_texts.append(txt)

# ─── 5. AUTO LABEL ADJUSTMENT ──────────────────────────
if adjust_text:

    np.random.seed(42)

    adjust_text(
        all_texts,
        ax=ax,
        expand_points=(3, 3),
        expand_text=(2, 2),
        force_text=1.5,
        force_points=1.5,
        arrowprops=dict(
            arrowstyle='-',
            color='#BBBBBB',
            lw=0.7
        )
    )

# ─── 6. ZONE LABELS ────────────────────────────────────
ax.text(0.02, 0.97,
        'Word-of-Mouth\nHigh Arrivals · Low Search',
        transform=ax.transAxes,
        ha='left',
        va='top',
        fontsize=9,
        color='#27ae60')

ax.text(0.98, 0.97,
        'High Potential\nHigh Arrivals · High Search',
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=9,
        color='#2471A3')

ax.text(0.02, 0.03,
        'Undiscovered\nLow Arrivals · Low Search',
        transform=ax.transAxes,
        ha='left',
        va='bottom',
        fontsize=9,
        color='#888888')

ax.text(0.95, 0.18,
        '⚠ Digital Gap\nHigh Search · Low Arrivals\n(Action Required)',
        transform=ax.transAxes,
        ha='right',
        va='top',
        fontsize=10,
        color='#C0392B',
        fontweight='bold',
        bbox=dict(
            boxstyle='round,pad=0.45',
            facecolor='#FFF0F0',
            edgecolor='#F5B7B1',
            linewidth=1.2
        )
)

ax.text(0.015, 0.47,
        '* Bangkok excluded',
        transform=ax.transAxes,
        fontsize=8,
        color='#BBBBBB',
        style='italic')

# ─── 7. LEGEND ─────────────────────────────────────────
legend_handles = [
    mpatches.Patch(color=COLORS['Major']['dot'], label='Major City'),
    mpatches.Patch(color=COLORS['Secondary']['dot'], label='Secondary City'),
    mpatches.Patch(color=COLORS['Gap']['dot'], label='Digital Gap province'),
    plt.Line2D([0], [0], color='#CCCCCC', linestyle='--', lw=1, label='Median threshold'),
]

ax.legend(
    handles=legend_handles,
    loc='upper right',
    bbox_to_anchor=(0.98, 0.85),
    fontsize=9,
    framealpha=0.92,
    edgecolor='#DDDDDD',
    title='Legend'
)

# ─── 8. AXES ───────────────────────────────────────────
ax.set_xlabel('Search Intent (Digital Interest)', fontsize=11)
ax.set_ylabel('Total Arrivals (Actual Footprints)', fontsize=11)

ax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda x, _: f'{x/1e6:.1f}M' if x >= 1e6 else f'{int(x/1e3):,}K'
    )
)

ax.xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'{int(x):,}')
)

ax.tick_params(colors='#888888', labelsize=9)

# ─── 9. SAVE FIGURE ────────────────────────────────────
plt.tight_layout()


os.makedirs('visualizations', exist_ok=True)

plt.savefig(
    'visualizations/Figure_5_Conversion_Efficiency.png',
    facecolor='white',
    bbox_inches='tight',
    dpi=200
)

plt.show()

print("✅ Figure 5 (Conversion Efficiency) created successfully!")