import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  'white',
    'axes.facecolor':    '#F8F9FA',
    'axes.grid':         True,
    'grid.color':        '#FFFFFF',
    'grid.linewidth':    1.2,
    'font.family':       'sans-serif',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom':False,
})

COLORS = {
    '2024 vs 2023': '#16A085',
    '2025 vs 2024': '#1B4F8A'
}

# ─── Load Data ────────────────────────────────────────────────────────────────
data_path = "data/processed/master_tourism_analysis.csv"
df = pd.read_csv(data_path)

# Convert Thai BE → CE
df['Year_CE'] = df['Year'].astype(int) - 543
df['date'] = pd.to_datetime(
    df['Year_CE'].astype(str) + '-' + df['Month'],
    format='%Y-%b'
)

# ─── KEEP ONLY SECONDARY CITIES ───────────────────────────────────────────────
df = df[df['City_type_EN'] == 'Secondary City']

# Extract month number
df['month_num'] = df['date'].dt.month

# Monthly revenue aggregation
df_sec = (
    df.groupby(['Year_CE','month_num'])['total_revenue']
    .sum()
    .reset_index()
)

# Pivot table (month × year)
pivot = df_sec.pivot(
    index='month_num',
    columns='Year_CE',
    values='total_revenue'
)

# ─── YoY Growth Calculations ───────────────────────────────────────────────────
yoy_24_23 = (pivot[2024] - pivot[2023]) / pivot[2023]
yoy_25_24 = (pivot[2025] - pivot[2024]) / pivot[2024]

months = range(1,13)

os.makedirs('visualizations', exist_ok=True)

# ─── Plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16,9))
plt.subplots_adjust(top=0.80)

# Line: 2024 vs 2023
ax.plot(
    months,
    yoy_24_23,
    linewidth=3,
    color=COLORS['2024 vs 2023'],
    label='2024 vs 2023'
)

# Line: 2025 vs 2024
ax.plot(
    months,
    yoy_25_24,
    linewidth=3,
    color=COLORS['2025 vs 2024'],
    label='2025 vs 2024'
)

# Zero reference line
ax.axhline(0, color='#555', linestyle='--', linewidth=1.2)

# ─── Axis Formatting ──────────────────────────────────────────────────────────
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_ylabel("YoY Tourism Income Growth")

month_labels = ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']
ax.set_xticks(months)
ax.set_xticklabels(month_labels)

# ─── Title ────────────────────────────────────────────────────────────────────
ax.set_title(
    "Year-over-Year Tourism Income Growth — Secondary Cities",
    fontsize=18,
    fontweight='bold',
    loc='left',
    pad=45
)

# ─── Subtitle ─────────────────────────────────────────────────────────────────
fig.text(
    0.07, 0.905,
    "Monthly revenue comparison: 2024 vs 2023 and 2025 vs 2024",
    fontsize=11,
    color='#888'
)

# ─── Legend ───────────────────────────────────────────────────────────────────
ax.legend(
    loc='upper left',
    bbox_to_anchor=(0, 1.05),
    framealpha=0.9
)

# ─── Source ───────────────────────────────────────────────────────────────────
fig.text(
    0.01, 0.02,
    "Source: Thailand Tourism Authority",
    fontsize=8.5,
    color='#AAA'
)

# ─── Save ─────────────────────────────────────────────────────────────────────
plt.savefig(
    "visualizations/Figure 5.png",
    dpi=300,
    facecolor='white',
    bbox_inches='tight'
)

plt.close()

print("✅ Figure 5 created successfully (Secondary Cities only)")