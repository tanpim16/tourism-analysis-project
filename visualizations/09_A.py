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
    'grid.color':       '#EAECEE',   # ✅ softer grid
    'grid.linewidth':   1.0,
    'font.family':      'sans-serif',
    'axes.spines.top':  False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom': False,
})

YEAR_COLORS = {2023: '#C8D6E5', 2024: '#5B9BD5', 2025: '#1B3A5C'}

def fmt(x):
    if x >= 1e6: return f'{x/1e6:.1f}M'
    if x >= 1e3: return f'{x/1e3:.0f}K'
    return f'{x:,.0f}'

# ─── Data ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/foreign_visitors_combined.csv')
df.columns = df.columns.str.strip()

# Fix column typo if exists
if 'ne year' in df.columns:
    df.rename(columns={'ne year': 'year'}, inplace=True)

# Clean country names
df['country'] = df['country'].replace({
    'Korea (Republic of)': 'South Korea',
    'Russian Federation': 'Russia',
    'The United States of America': 'United States',
    'United States of America': 'United States'
})

# Filter non-aggregate rows
ind = df[df['is_aggregate'] == False].copy()

# Top 10 countries by total visitors across all 3 years
top10 = (ind.groupby('country')['visitors'].sum()
         .sort_values(ascending=False)
         .head(10)
         .index.tolist())

# Yearly breakdown for top 10
yearly = (ind[ind['country'].isin(top10)]
          .groupby(['country', 'year'])['visitors'].sum()
          .unstack(fill_value=0)
          .reindex(top10))

# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))

years = sorted(yearly.columns)
n = len(top10)
bar_h = 0.22
y_pos = np.arange(n)

ax.set_axisbelow(True)

for i, yr in enumerate(years):
    vals = yearly[yr].values
    offset = (i - 1) * (bar_h + 0.02)

    ax.barh(
        y_pos - offset,
        vals,
        bar_h,
        label=str(yr),
        color=YEAR_COLORS[yr],
        edgecolor='none'
    )

    # Value labels
    for j, v in enumerate(vals):
        ax.text(
            v + yearly.values.max() * 0.008,
            y_pos[j] - offset,
            fmt(v),
            va='center',
            ha='left',
            fontsize=8,
            fontweight='bold',
            color='#2C3E50'
        )

# Y-axis
ax.set_yticks(y_pos)
ax.set_yticklabels(top10, fontsize=10, color='#34495E')
ax.invert_yaxis()

# X-axis
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax.tick_params(axis='x', labelsize=9, colors='#5D6D7E')
ax.set_xlim(0, yearly.values.max() * 1.15)

# Axis label (optional but recommended)
ax.set_xlabel('Number of Visitors', fontsize=10, color='#34495E', labelpad=8)

# Title
ax.set_title(
    'Annual breakdown of the Top 10 source countries (2023–2025)',
    fontsize=18,
    fontweight='bold',
    color='#1F2D3D',
    pad=10
)

# Legend
ax.legend(
    loc='lower right',
    fontsize=9,
    framealpha=0.9,
    title='Year',
    title_fontsize=10
)

# Layout
plt.tight_layout()

# Save
os.makedirs('visualizations', exist_ok=True)
fig.savefig(
    'visualizations/Figure_9A_Top10_Foreigners.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()
print('✓ Saved: visualizations/Figure_9A_Top10_Foreigners.png')