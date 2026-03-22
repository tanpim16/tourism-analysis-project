import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os

# ─── Style & Colors ──────────────────────────────────────────────────────────
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
})

COLORS = {
    'Major City': '#1B4F8A',
    'Secondary City': '#16A085'
}

# ─── Load & Data Prep ────────────────────────────────────────────────────────
data_path = "data/processed/master_tourism_analysis.csv"
df = pd.read_csv(data_path)

if 'Year_CE' not in df.columns:
    df['Year_CE'] = df['Year'].astype(int) - 543

df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')

df_share = df.groupby(['date', 'City_type_EN'])['total_visitors'].sum().reset_index()
df_share['total_all'] = df_share.groupby('date')['total_visitors'].transform('sum')
df_share['visitor_share'] = df_share['total_visitors'] / df_share['total_all']

pivot = df_share.pivot(index='date', columns='City_type_EN', values='visitor_share').sort_index()

# ─── Visualization ───
fig, ax = plt.subplots(figsize=(16, 9))

# 100% Stacked Area
ax.stackplot(
    pivot.index,
    pivot['Major City'],
    pivot['Secondary City'],
    colors=[COLORS['Major City'], COLORS['Secondary City']],
    alpha=0.85,
    labels=['Major City', 'Secondary City']
)

# ─── FIX: no gap on X-axis ───
ax.set_xlim(pivot.index.min(), pivot.index.max())
ax.margins(x=0)

# ─── Layout Fix (no overlap) ───
plt.subplots_adjust(top=0.83)

# ─── Legend ───
ax.legend(
    loc='lower left',
    bbox_to_anchor=(0, 1.0),
    ncol=2,
    frameon=False,
    fontsize=14,
    title_fontsize=14
)

# ─── Subtitle ───
ax.text(
    0.5, 1.08,
    "100% stacked distribution of visitors by city type · Jan 2023 – Dec 2025",
    transform=ax.transAxes,
    fontsize=14,
    color='#888888',
    ha='center'
)

# ─── Figure Title ───
fig.suptitle(
    "Tourism Redistribution Share",
    x=0.5,
    ha='center',
    fontsize=18,
    fontweight='bold',
    y=0.95
)

# ─── Formatting ───
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_ylim(0, 1)
ax.set_yticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])

ax.set_ylabel("Visitor Share", fontsize=14, color='#666')
ax.tick_params(axis='both', which='major', labelsize=14)

# ─── Save ───
os.makedirs('visualizations', exist_ok=True)
plt.savefig(
    "visualizations/Figure_2_Marketshare_Distribution.png",
    dpi=300,
    bbox_inches='tight'
)
plt.close()

print("✅ Figure 2 (Final Clean Version) created successfully!")