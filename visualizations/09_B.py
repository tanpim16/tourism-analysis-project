import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.ticker as mticker

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#F8F9FA',
    'font.family':      'sans-serif',
})

# ─── Data ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/foreign_visitors_combined.csv')
df.columns = df.columns.str.strip()

if 'ne year' in df.columns:
    df.rename(columns={'ne year': 'year'}, inplace=True)

# Clean country names
df['country'] = df['country'].replace({
    'Korea (Republic of)': 'South Korea',
    'Russian Federation': 'Russia',
    'The United States of America': 'United States',
    'United States of America': 'United States'
})

ind = df[df['is_aggregate'] == False].copy()

# Top 10 countries
top10 = (ind.groupby('country')['visitors'].sum()
         .sort_values(ascending=False)
         .head(10)
         .index.tolist())

# Pivot table
heat = (ind[ind['country'].isin(top10)]
        .groupby(['country', 'month_year'])['visitors'].sum()
        .reset_index()
        .pivot(index='country', columns='month_year', values='visitors')
        .fillna(0))

# Sort months
month_order = []
for y in [2023, 2024, 2025]:
    for m in ['Jan','Feb','Mar','Apr','May','Jun',
              'Jul','Aug','Sep','Oct','Nov','Dec']:
        label = f'{m}-{y}'
        if label in heat.columns:
            month_order.append(label)

heat = heat[month_order]
heat = heat.reindex(top10)

# ─── Plot ─────────────────────────────────────────────────────────────────────
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(14, 18))
gs = GridSpec(3, 2, figure=fig, width_ratios=[1, 0.03], hspace=0.25, wspace=0.05)

vmin = heat.values.min()
vmax = heat.values.max()

months_short = ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']

for idx, yr in enumerate([2023, 2024, 2025]):
    ax = fig.add_subplot(gs[idx, 0])

    cols = [f'{m}-{yr}' for m in months_short if f'{m}-{yr}' in heat.columns]
    data_yr = heat[cols]

    annot_data = data_yr.map(lambda x: f'{x/1e3:.0f}K' if x >= 1e3 else f'{x:.0f}')

    sns.heatmap(
        data_yr,
        ax=ax,
        cmap='YlOrRd',
        linewidths=0.5,
        linecolor='#FFFFFF',
        annot=annot_data,
        fmt='',
        annot_kws={
            'fontsize': 8,
            'color': '#2C3E50',
            'fontweight': 'bold'
        },
        vmin=vmin,
        vmax=vmax,
        cbar=False
    )

    # X-axis
    ax.set_xticklabels(
        [c.split('-')[0] for c in cols],
        rotation=0,
        ha='center',
        fontsize=9,
        color='#5D6D7E'
    )

    # Y-axis
    ax.set_yticklabels(
        ax.get_yticklabels(),
        fontsize=10,
        color='#34495E'
    )

    ax.set_xlabel('')
    ax.set_ylabel('')

    # Year title
    ax.set_title(
        str(yr),
        fontsize=14,
        fontweight='bold',
        color='#1F2D3D',
        pad=8
    )

# ─── Colorbar ─────────────────────────────────────────────────────────────────
cbar_ax = fig.add_subplot(gs[1, 1])
sm = plt.cm.ScalarMappable(
    cmap='YlOrRd',
    norm=plt.Normalize(vmin=vmin, vmax=vmax)
)
sm.set_array([])

cbar = fig.colorbar(sm, cax=cbar_ax)

# ✅ Format to XXK
cbar.ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f'{int(x/1e3)}K')
)

cbar.ax.tick_params(labelsize=9, colors='#5D6D7E')
cbar.set_label('Number of Visitors', fontsize=10, color='#34495E')

# ─── Title (tight spacing only) ───────────────────────────────────────────────
fig.suptitle(
    'Monthly visitor intensity for the Top 10 countries (2023–2025)',
    fontsize=14,
    fontweight='bold',
    color='#1F2D3D',
    y=0.93
)

# Layout
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save
os.makedirs('visualizations', exist_ok=True)
fig.savefig(
    'visualizations/Figure_9B_Heatmap_Foreign_Visitors.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()
print('✓ Saved: visualizations/Figure_9B_Heatmap_Foreign_Visitors.png')