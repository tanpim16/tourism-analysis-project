# Created by Pimkanit – Heatmap: Top 10 Countries Monthly Foreign Visitors (2023–2025)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import os

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'font.family':      'sans-serif',
})

# ─── Data ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/foreign_visitors_combined.csv')
df.columns = df.columns.str.strip()
if 'ne year' in df.columns:
    df.rename(columns={'ne year': 'year'}, inplace=True)
df['country'] = df['country'].replace('Korea (Republic of)', 'South Korea')
ind = df[df['is_aggregate'] == False].copy()

# Top 10 countries by total visitors
top10 = (ind.groupby('country')['visitors'].sum()
         .sort_values(ascending=False).head(10).index.tolist())

# Build pivot: country × month_year
heat = (ind[ind['country'].isin(top10)]
        .groupby(['country', 'month_year'])['visitors'].sum()
        .reset_index()
        .pivot(index='country', columns='month_year', values='visitors')
        .fillna(0))

# Sort months chronologically Jan-2023 → Dec-2025
month_order = []
for y in [2023, 2024, 2025]:
    for m in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        label = f'{m}-{y}'
        if label in heat.columns:
            month_order.append(label)

heat = heat[month_order]
heat = heat.reindex(top10)

# ─── Plot: 3 Heatmaps stacked vertically (one per year) ──────────────────────
months_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(14, 18))
gs = GridSpec(3, 2, figure=fig, width_ratios=[1, 0.03], hspace=0.3, wspace=0.05)

# Global vmin/vmax for consistent color scale
vmin = heat.values.min()
vmax = heat.values.max()

axes = []
for idx, yr in enumerate([2023, 2024, 2025]):
    ax = fig.add_subplot(gs[idx, 0])
    axes.append(ax)
    cols = [f'{m}-{yr}' for m in months_short if f'{m}-{yr}' in heat.columns]
    data_yr = heat[cols]

    # Format values as xxK
    annot_data = data_yr.map(lambda x: f'{x/1e3:.0f}K' if x >= 1e3 else f'{x:.0f}')

    sns.heatmap(data_yr, ax=ax, cmap='YlOrRd', linewidths=0.3, linecolor='white',
                annot=annot_data, fmt='', annot_kws={'fontsize': 8},
                vmin=vmin, vmax=vmax,
                cbar=False)

    # Show only month names (without year) on x-axis
    ax.set_xticklabels([c.split('-')[0] for c in cols], rotation=0, ha='center', fontsize=9)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title(str(yr), fontsize=13, fontweight='bold', color='#2C3E50', pad=8)

# Shared colorbar in the middle row's right column
cbar_ax = fig.add_subplot(gs[1, 1])
sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm.set_array([])
fig.colorbar(sm, cax=cbar_ax, label='Number of Visitors')

fig.suptitle('Monthly Foreign Tourist Arrivals – Top 10 Countries',
             fontsize=16, fontweight='bold', color='#2C3E50', y=0.98)
fig.text(0.5, 0.955, 'Jan 2023 – Dec 2025 (MOTS data)',
         ha='center', fontsize=10, color='#7F8C8D', style='italic')

plt.subplots_adjust(top=0.93)
os.makedirs('visualizations', exist_ok=True)
fig.savefig('visualizations/Figure_9B_Heatmap_Foreign_Visitors.png', dpi=300, bbox_inches='tight')
plt.show()
print('✓ Saved: visualizations/Figure_9B_Heatmap_Foreign_Visitors.png')
