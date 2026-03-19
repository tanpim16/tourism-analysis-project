# ─── IMPORT ──────────────────────────────────────────────────────────────────
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

# ─── GLOBAL STYLE (Hierarchy) ────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   '#F8F9FA',
    'font.family':      'sans-serif',

    # Title
    'figure.titlesize': 18,
    'figure.titleweight': 'bold',

    # Axis / legend
    'axes.labelsize': 10,

    # Ticks
    'xtick.labelsize': 9,
    'ytick.labelsize': 10,

    # Grid
    'axes.grid': True,
    'grid.color': '#EAECEE',
    'grid.linewidth': 0.8,
})

# ─── DATA ────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/foreign_visitors_combined.csv')
df.columns = df.columns.str.strip()

if 'ne year' in df.columns:
    df.rename(columns={'ne year': 'year'}, inplace=True)

df['country'] = df['country'].replace({
    'Korea (Republic of)': 'South Korea',
    'Russian Federation': 'Russia',
    'The United States of America': 'United States',
    'United States of America': 'United States'
})

ind = df[df['is_aggregate'] == False].copy()

top10 = (ind.groupby('country')['visitors'].sum()
         .sort_values(ascending=False)
         .head(10)
         .index.tolist())

heat = (ind[ind['country'].isin(top10)]
        .groupby(['country', 'month_year'])['visitors'].sum()
        .reset_index()
        .pivot(index='country', columns='month_year', values='visitors')
        .fillna(0))

# ─── SORT MONTHS ─────────────────────────────────────────────────────────────
month_order = []
for y in [2023, 2024, 2025]:
    for m in ['Jan','Feb','Mar','Apr','May','Jun',
              'Jul','Aug','Sep','Oct','Nov','Dec']:
        label = f'{m}-{y}'
        if label in heat.columns:
            month_order.append(label)

heat = heat[month_order].reindex(top10)

# ─── PLOT ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 12), constrained_layout=True)  # ✅ พอดีจอ
gs = GridSpec(3, 2, figure=fig, width_ratios=[1, 0.04])

vmin, vmax = heat.values.min(), heat.values.max()
months_short = ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']

for idx, yr in enumerate([2023, 2024, 2025]):
    ax = fig.add_subplot(gs[idx, 0])

    cols = [f'{m}-{yr}' for m in months_short if f'{m}-{yr}' in heat.columns]
    data = heat[cols]

    annot = data.map(lambda x: f'{x/1e3:.0f}K')

    sns.heatmap(
        data,
        ax=ax,
        cmap='YlOrRd',
        linewidths=0.5,
        linecolor='#FFFFFF',
        annot=annot,
        fmt='',
        annot_kws={
            'fontsize': 8,
            'fontweight': 'bold',
            'color': '#2C3E50'
        },
        vmin=vmin,
        vmax=vmax,
        cbar=False
    )

    # ✅ X ticks (เดือน)
    ax.set_xticklabels(
        [c.split('-')[0] for c in cols],
        fontsize=9,
        color='#5D6D7E'
    )

    # ✅ Y ticks (ประเทศ)
    ax.set_yticklabels(
        ax.get_yticklabels(),
        fontsize=10,
        color='#34495E'
    )

    # ✅ ลบ label "month_year"
    ax.set_xlabel('')
    ax.xaxis.label.set_visible(False)

    # Subplot title
    ax.set_title(
        str(yr),
        fontsize=12,
        fontweight='bold',
        color='#1F2D3D',
        pad=12
    )

# ─── COLORBAR ────────────────────────────────────────────────────────────────
cbar_ax = fig.add_subplot(gs[:, 1])
sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm.set_array([])

cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f'{int(x/1e3)}K')
)

cbar.set_label(
    'Number of Visitors',
    fontsize=10
)

# ─── MAIN TITLE ──────────────────────────────────────────────────────────────
fig.suptitle(
    'Monthly visitor intensity for the Top 10 countries (2023–2025)',
    color='#1F2D3D'
)

# ─── SAVE ────────────────────────────────────────────────────────────────────
fig.savefig(
    'visualizations/Figure_9B_Heatmap_Foreign_Visitors.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()