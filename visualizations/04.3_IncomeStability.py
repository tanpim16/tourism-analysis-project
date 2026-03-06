import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
import os

# ─────────────────────────────────────────
# 1. LOAD & CALCULATE CV
# ─────────────────────────────────────────
df = pd.read_csv('data/processed/final_master_with_trends.csv')

revenue_col  = [c for c in df.columns if 'revenue' in c.lower() and 'real' in c.lower()][0]
province_col = [c for c in df.columns if 'prov' in c.lower() and 'en' in c.lower()]
province_col = province_col[0] if province_col else [c for c in df.columns if 'prov' in c.lower()][0]
city_type_col = 'City_type_EN' if 'City_type_EN' in df.columns else 'City_type'

stability = df.groupby([province_col, city_type_col])[revenue_col].agg(['mean','std']).reset_index()
stability.columns = [province_col, city_type_col, 'mean_rev', 'std_rev']
stability['cv'] = (stability['std_rev'] / stability['mean_rev']) * 100
stability = stability.dropna(subset=['cv'])

cv_med  = stability['cv'].median()
rev_med = stability['mean_rev'].median()
stability['dist'] = ((stability['cv'] - cv_med)**2 + (stability['mean_rev'] - rev_med)**2) ** 0.5

COLORS = {
    'Major City':     {'dot': '#4A90D9', 'text': '#1A5276'},
    'Secondary City': {'dot': '#5BAD6F', 'text': '#1E8449'},
}
def dot_color(ct):  return COLORS['Major City']['dot']  if 'Major' in str(ct) else COLORS['Secondary City']['dot']
def text_color(ct): return COLORS['Major City']['text'] if 'Major' in str(ct) else COLORS['Secondary City']['text']

# ─────────────────────────────────────────
# 2. FIGURE
# ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 9), facecolor='white')
ax.set_facecolor('#FAFAFA')

xmax = stability['cv'].max() * 1.12
ymin = stability['mean_rev'].min() * 0.7
ymax = stability['mean_rev'].max() * 1.5
ax.set_xlim(stability['cv'].min() * 0.9, xmax)
ax.set_ylim(ymin, ymax)
ax.set_yscale('log')

# Shading — Seasonal Giants zone (top-right)
ax.add_patch(plt.Rectangle(
    (cv_med, rev_med), xmax - cv_med, ymax - rev_med,
    facecolor='#FFF8EE', edgecolor='none', zorder=0, alpha=0.8
))

# Quadrant lines
ax.axvline(cv_med,  color='#CCCCCC', linestyle='--', linewidth=1.0, zorder=1)
ax.axhline(rev_med, color='#CCCCCC', linestyle='--', linewidth=1.0, zorder=1)

# Median hints
ax.text(cv_med + xmax*0.01, ymax*0.85,
        f'median CV  {cv_med:.1f}%',
        fontsize=8, color='#BBBBBB', ha='left', va='top')
ax.text(xmax*0.985, rev_med * 1.15,
        f'median  {rev_med:,.0f}M',
        fontsize=8, color='#BBBBBB', ha='right', va='bottom')

# ─────────────────────────────────────────
# 3. DOTS
# ─────────────────────────────────────────
for _, row in stability.iterrows():
    size = 90 if 'Major' in str(row[city_type_col]) else 55
    ax.scatter(row['cv'], row['mean_rev'],
               s=size, color=dot_color(row[city_type_col]),
               alpha=0.6, edgecolors='white', linewidth=0.6, zorder=3)

# ─────────────────────────────────────────
# 4. LABELS — top outliers per quadrant
# ─────────────────────────────────────────
all_texts = []
configs = [
    ((stability['cv'] <  cv_med) & (stability['mean_rev'] >= rev_med), 'dist', 2),
    ((stability['cv'] >= cv_med) & (stability['mean_rev'] >= rev_med), 'dist', 4),
    ((stability['cv'] <  cv_med) & (stability['mean_rev'] <  rev_med), 'dist', 3),
    ((stability['cv'] >= cv_med) & (stability['mean_rev'] <  rev_med), 'dist', 3),
]

for cond, sort_col, n in configs:
    for _, row in stability[cond].nlargest(n, sort_col).iterrows():
        t = ax.text(row['cv'], row['mean_rev'], row[province_col],
                    fontsize=8.5, fontweight='bold',
                    color=text_color(row[city_type_col]),
                    path_effects=[pe.withStroke(linewidth=2.5, foreground='white')],
                    zorder=5)
        all_texts.append(t)

try:
    from adjustText import adjust_text
    adjust_text(all_texts, ax=ax, expand_points=(2, 2),
                arrowprops=dict(arrowstyle='-', color='#CCCCCC', lw=0.8))
except:
    pass

# ─────────────────────────────────────────
# 5. ZONE LABELS
# ─────────────────────────────────────────
ax.text(0.02, 0.90, 'Stable Cash Cows\nHigh Revenue · Low Volatility',
        transform=ax.transAxes, ha='left', va='top',
        fontsize=9, color='#1e8449', fontweight='bold', linespacing=1.5)

ax.text(0.98, 0.97, '⚠  Seasonal Giants\nHigh Revenue · High Volatility',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=9, color='#e67e22', fontweight='bold', linespacing=1.5,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF8EE',
                  edgecolor='#F5CBA7', linewidth=1.2))

ax.text(0.02, 0.03, 'Stable but Small\nLow Revenue · Low Volatility',
        transform=ax.transAxes, ha='left', va='bottom',
        fontsize=8.5, color='#888888', alpha=0.8, linespacing=1.5)

ax.text(0.98, 0.03, 'High Risk · Low Reward\nLow Revenue · High Volatility',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=8.5, color='#c0392b', alpha=0.8, linespacing=1.5)

# ─────────────────────────────────────────
# 6. LEGEND, TITLE, AXES
# ─────────────────────────────────────────
legend_handles = [
    mpatches.Patch(color=COLORS['Major City']['dot'],     label='Major City'),
    mpatches.Patch(color=COLORS['Secondary City']['dot'], label='Secondary City'),
    plt.Line2D([0],[0], color='#CCCCCC', linestyle='--', lw=1, label='Median threshold'),
]
ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(0.98, 0.78),
          fontsize=8.5, framealpha=0.92, edgecolor='#DDDDDD',
          title='Legend', title_fontsize=8.5)

ax.set_title('Figure 5: Income Stability vs. Performance Matrix\nCV of Real Revenue — Higher CV = More Seasonal Risk',
             fontsize=13, fontweight='bold', color='#1A252F', loc='left', pad=16)
ax.set_xlabel('Income Volatility  (CV % — lower = more stable)', fontsize=11, color='#444', labelpad=10)
ax.set_ylabel('Avg Monthly Real Revenue (Million THB, log scale)', fontsize=11, color='#444', labelpad=10)

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}M'))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#DDDDDD')
ax.spines['bottom'].set_color('#DDDDDD')
ax.tick_params(colors='#888888', labelsize=9)

plt.tight_layout()
os.makedirs('visualizations', exist_ok=True)
plt.savefig('visualizations/Figure_Income_Stability.png',
            facecolor='white', bbox_inches='tight', dpi=200)
plt.show()
print("Done")