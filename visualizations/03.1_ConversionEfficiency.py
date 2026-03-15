import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
import os

# 1. LOAD & AGGREGATE
df_raw = pd.read_csv('data/processed/final_master_with_trends.csv')

prov_cols = [c for c in df_raw.columns if 'prov' in c.lower() and 'en' in c.lower()]
if not prov_cols:
    prov_cols = [c for c in df_raw.columns if 'prov' in c.lower()]
province_col  = prov_cols[0] if prov_cols else None
city_type_col = 'City_type_EN' if 'City_type_EN' in df_raw.columns else 'City_type'

df_raw['total_search']   = df_raw['search_thai'].fillna(0) + df_raw['search_foreign'].fillna(0)
df_raw['total_visitors'] = df_raw['total_visitors'].fillna(0)

df = df_raw.groupby(province_col).agg(
    total_search   = ('total_search',   'mean'),
    total_visitors = ('total_visitors', 'mean'),
    city_type      = (city_type_col,    'first'),
).reset_index()

df_other = df[~df[province_col].str.contains('Bangkok', na=False)].copy()

s_med = df_other['total_search'].median()
v_med = df_other['total_visitors'].median()

df_other['dist']      = ((df_other['total_search'] - s_med)**2 + (df_other['total_visitors'] - v_med)**2) ** 0.5
df_other['gap_score'] = df_other['total_search'] / (df_other['total_visitors'] + 1)
df_other['in_gap']    = (df_other['total_search'] >= s_med) & (df_other['total_visitors'] < v_med)

COLORS = {
    'Major':     {'dot': '#4A90D9', 'text': '#1A5276'},
    'Secondary': {'dot': '#5BAD6F', 'text': '#1E8449'},
    'Gap':       {'dot': '#E05C5C', 'text': '#C0392B'},
}

# 2. FIGURE
fig, ax = plt.subplots(figsize=(13, 9), facecolor='white')
ax.set_facecolor('#FAFAFA')

xmax_data = df_other['total_search'].max() * 1.12
ymax_data = df_other['total_visitors'].max() * 1.15
ax.set_xlim(-2, xmax_data)
ax.set_ylim(-v_med * 0.1, ymax_data)

# Shading
ax.add_patch(plt.Rectangle((s_med, 0), xmax_data - s_med, v_med,
                            facecolor='#FFF0F0', edgecolor='none', zorder=0, alpha=0.7))
ax.axhline(v_med, color='#CCCCCC', linestyle='--', linewidth=1.0, zorder=1)
ax.axvline(s_med, color='#CCCCCC', linestyle='--', linewidth=1.0, zorder=1)

# 3. DOTS
for _, row in df_other.iterrows():
    if row['in_gap']:
        color, size, alpha, z = COLORS['Gap']['dot'], 100, 0.85, 4
    elif 'Major' in str(row['city_type']):
        color, size, alpha, z = COLORS['Major']['dot'], 75, 0.5, 3
    else:
        color, size, alpha, z = COLORS['Secondary']['dot'], 45, 0.5, 2
    ax.scatter(row['total_search'], row['total_visitors'],
               s=size, color=color, alpha=alpha,
               edgecolors='white', linewidth=0.5, zorder=z)

# 4. LABELS — 4 quadrants, color per zone
all_texts = []
quad_config = [
    (df_other['in_gap'],
     'gap_score', 6, COLORS['Gap']['text']),
    ((df_other['total_search'] <  s_med) & (df_other['total_visitors'] >= v_med),
     'dist', 3, COLORS['Secondary']['text']),
    ((df_other['total_search'] >= s_med) & (df_other['total_visitors'] >= v_med),
     'dist', 3, COLORS['Major']['text']),
    ((df_other['total_search'] <  s_med) & (df_other['total_visitors'] <  v_med),
     'dist', 4, '#777777'),
]

for cond, sort_col, n, _ in quad_config:
    for _, row in df_other[cond].nlargest(n, sort_col).iterrows():
        if 'Major' in str(row['city_type']):
            t_color = COLORS['Major']['text']
        else:
            t_color = COLORS['Secondary']['text']
        
        t = ax.text(row['total_search'], row['total_visitors'], row[province_col],
                    fontsize=8.5, fontweight='bold', color=t_color,
                    path_effects=[pe.withStroke(linewidth=2.5, foreground='white')], zorder=5)
        all_texts.append(t)

try:
    from adjustText import adjust_text
    adjust_text(all_texts, ax=ax, expand_points=(2, 2),
                arrowprops=dict(arrowstyle='-', color='#CCCCCC', lw=0.8))
except:
    pass

# 5. ZONE LABELS
ax.text(0.02, 0.97, 'Word-of-Mouth\nHigh Arrivals · Low Search',
        transform=ax.transAxes, ha='left', va='top',
        fontsize=8.5, color='#27ae60', alpha=0.8, linespacing=1.5)
ax.text(0.98, 0.97, 'High Potential\nHigh Arrivals · High Search',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=8.5, color='#2471A3', alpha=0.8, linespacing=1.5)
ax.text(0.02, 0.03, 'Undiscovered\nLow Arrivals · Low Search',
        transform=ax.transAxes, ha='left', va='bottom',
        fontsize=8.5, color='#888888', alpha=0.8, linespacing=1.5)
ax.text(0.95, 0.18, '⚠  Digital Gap\nHigh Search · Low Arrivals\n(Action Required)',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=9.5, color='#C0392B', fontweight='bold', linespacing=1.6,
        bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFF0F0',
                  edgecolor='#F5B7B1', linewidth=1.2))
ax.text(0.015, 0.47, '* Bangkok excluded',
        transform=ax.transAxes, ha='left', va='center',
        fontsize=7.5, color='#BBBBBB', style='italic')

# 6. LEGEND & AXES
legend_handles = [
    mpatches.Patch(color=COLORS['Major']['dot'],     label='Major City'),
    mpatches.Patch(color=COLORS['Secondary']['dot'], label='Secondary City'),
    mpatches.Patch(color=COLORS['Gap']['dot'],       label='Digital Gap province'),
    plt.Line2D([0],[0], color='#CCCCCC', linestyle='--', lw=1, label='Median threshold'),
]
ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(0.98, 0.85),
          fontsize=8.5, framealpha=0.92, edgecolor='#DDDDDD',
          title='Legend', title_fontsize=8.5)

ax.set_title('Tourism Conversion Matrix\nSearch Intent vs. Physical Arrivals  (avg per province, Bangkok excluded)',
             fontsize=13, fontweight='bold', color='#1A252F', loc='left', pad=16)
ax.set_xlabel('Search Intent (Digital Interest)', fontsize=11, color='#444', labelpad=10)
ax.set_ylabel('Total Arrivals (Actual Footprints)', fontsize=11, color='#444', labelpad=10)

ax.yaxis.set_major_formatter(plt.FuncFormatter(
    lambda x, _: f'{x/1e6:.1f}M' if x >= 1e6 else f'{int(x/1e3):,}K' if x >= 1000 else f'{int(x)}'))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#DDDDDD')
ax.spines['bottom'].set_color('#DDDDDD')
ax.tick_params(colors='#888888', labelsize=9)

plt.tight_layout()
os.makedirs('visualizations', exist_ok=True)
plt.savefig('visualizations/Figure_Conversion_Efficiency.png',
            facecolor='white', bbox_inches='tight', dpi=200)
plt.show()
print("Done")