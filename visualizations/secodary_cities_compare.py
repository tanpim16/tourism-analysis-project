import pandas as pd
import matplotlib.pyplot as plt
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
    'Visitors': '#16A085',
    'Revenue':  '#1B4F8A',
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

# ─── Secondary City Aggregation ───────────────────────────────────────────────
df_sec = (
    df[df['City_type_EN'] == 'Secondary City']
    .groupby('date')[['total_visitors','total_revenue']]
    .sum()
    .reset_index()
    .sort_values('date')
)

df_sec = df_sec.query("'2023-01-01' <= date <= '2025-12-01'")

# Convert to MILLIONS
df_sec['visitors_million'] = df_sec['total_visitors'] / 1_000_000
df_sec['revenue_million'] = df_sec['total_revenue']

os.makedirs('visualizations', exist_ok=True)

# ─── Plot (taller figure for dual axis clarity) ────────────────────────────────
fig, ax1 = plt.subplots(figsize=(16,9.5))

# reserve header space
plt.subplots_adjust(top=0.80)

# Visitors (left axis)
ax1.plot(
    df_sec['date'],
    df_sec['visitors_million'],
    color=COLORS['Visitors'],
    linewidth=3,
    label='Visitors (Million people)'
)

ax1.set_ylabel("Visitors (Million people)", color=COLORS['Visitors'])
ax1.tick_params(axis='y', labelcolor=COLORS['Visitors'])

# Revenue (right axis)
ax2 = ax1.twinx()

ax2.plot(
    df_sec['date'],
    df_sec['revenue_million'],
    color=COLORS['Revenue'],
    linewidth=3,
    label='Revenue (Million THB)'
)

ax2.set_ylabel("Revenue (Million THB)", color=COLORS['Revenue'])
ax2.tick_params(axis='y', labelcolor=COLORS['Revenue'])

# ─── X axis ───────────────────────────────────────────────────────────────────
ticks = pd.date_range('2023-01-01','2026-01-01',freq='QS-JAN')
ax1.set_xticks(ticks)
ax1.set_xticklabels([d.strftime('%b\n%Y') for d in ticks])
ax1.set_xlim(pd.Timestamp('2022-12-01'), pd.Timestamp('2025-12-31'))

# ─── Title ────────────────────────────────────────────────────────────────────
fig.text(
    0.07, 0.93,
    "Secondary City Tourism Performance",
    fontsize=20,
    fontweight='bold',
    color='#1A1A2E'
)

fig.text(
    0.07, 0.895,
    "Total visitors and tourism revenue in secondary cities · Jan 2023 – Dec 2025",
    fontsize=11,
    color='#888'
)

# ─── Combined legend in header zone ───────────────────────────────────────────
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()

ax1.legend(
    lines_1 + lines_2,
    labels_1 + labels_2,
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
    "visualizations/Figure 4.png",
    dpi=300,
    facecolor='white',
    bbox_inches='tight'
)

plt.close()

print("✅ Figure 4 created successfully (layout fixed)")