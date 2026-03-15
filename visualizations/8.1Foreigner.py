# Created by Pimkanit – Top 10 Countries by Total Foreign Visitors (2023–2025)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#F8F9FA',
    'axes.grid':        True,
    'grid.color':       '#FFFFFF',
    'grid.linewidth':   1.2,
    'font.family':      'sans-serif',
    'axes.spines.top':  False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom': False,
})

YEAR_COLORS = {2023: '#95A5A6', 2024: '#3498DB', 2025: '#E74C3C'}

def fmt(x):
    if x >= 1e6: return f'{x/1e6:.1f}M'
    if x >= 1e3: return f'{x/1e3:.0f}K'
    return f'{x:,.0f}'

# ─── Data ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/foreign_visitors_combined.csv')
df.columns = df.columns.str.strip()
if 'ne year' in df.columns:
    df.rename(columns={'ne year': 'year'}, inplace=True)
df['country'] = df['country'].replace('Korea (Republic of)', 'South Korea')
ind = df[df['is_aggregate'] == False].copy()

# Top 10 countries by total visitors across all 3 years
top10 = (ind.groupby('country')['visitors'].sum()
         .sort_values(ascending=False).head(10).index.tolist())

# Yearly breakdown for top 10
yearly = (ind[ind['country'].isin(top10)]
          .groupby(['country', 'year'])['visitors'].sum()
          .unstack(fill_value=0)
          .reindex(top10))

# ─── Plot: Grouped Horizontal Bar ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))

years = sorted(yearly.columns)
n = len(top10)
bar_h = 0.22
y_pos = np.arange(n)

ax.set_axisbelow(True)

for i, yr in enumerate(years):
    vals = yearly[yr].values
    offset = (i - 1) * (bar_h + 0.02)
    bars = ax.barh(y_pos - offset, vals, bar_h,
                   label=str(yr), color=YEAR_COLORS[yr],
                   edgecolor='none', linewidth=0)
    for j, v in enumerate(vals):
        ax.text(v + yearly.values.max() * 0.008, y_pos[j] - offset,
                fmt(v), va='center', ha='left', fontsize=7.5,
                fontweight='bold', color='#2C3E50')

ax.set_yticks(y_pos)
ax.set_yticklabels(top10, fontsize=11)
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax.set_xlim(0, yearly.values.max() * 1.15)

fig.suptitle('Top 10 Countries with Highest Foreign Tourist Arrivals to Thailand',
             fontsize=16, fontweight='bold', color='#2C3E50', y=0.96)
fig.text(0.5, 0.885, 'Annual breakdown 2023–2025 (MOTS data)',
         ha='center', fontsize=10, color='#7F8C8D', style='italic')

ax.legend(loc='lower right', fontsize=11, framealpha=0.9, title='Year', title_fontsize=11)

plt.tight_layout(rect=[0, 0, 1, 0.95])
os.makedirs('visualizations', exist_ok=True)
fig.savefig('visualizations/F8.1_Top10_Foreigners.png', dpi=300, bbox_inches='tight')
plt.show()
print('✓ Saved: visualizations/F8.1_Top10_Foreigners.png')
