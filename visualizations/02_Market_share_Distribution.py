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

COLORS = {'Major City': '#1B4F8A', 'Secondary City': '#16A085'}

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
fig, ax = plt.subplots(figsize=(16, 9)) # เพิ่มความสูงอีกนิด

# 100% Stacked Area
ax.stackplot(pivot.index, pivot['Major City'], pivot['Secondary City'], 
              colors=[COLORS['Major City'], COLORS['Secondary City']], alpha=0.85,
              labels=['Major City', 'Secondary City'])

# ─── Spacing Fix: Legend, Subtitle, and Title (NO OVERLAP) ───
# วาง Legend ไว้เหนือ Plot พื้นที่ว่างๆ
ax.legend(loc='lower left', bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, fontsize=11)

# วาง Subtitle ไว้เหนือ Legend
ax.text(0, 1.12, "100% stacked distribution of visitors by city type · Jan 2023 – Dec 2025", 
         transform=ax.transAxes, fontsize=12, color='#888888', ha='left')

# วาง Title ไว้บนสุด
ax.set_title("Tourism Redistribution Share", loc='left', fontweight='bold', fontsize=24, pad=90)

# Formatting
ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_ylim(0, 1)
ax.set_ylabel("Visitor Share", fontsize=11, color='#666')
ax.tick_params(axis='both', which='major', labelsize=10)

os.makedirs('visualizations', exist_ok=True)
plt.savefig("visualizations/Figure_2_Marketshare_Distribution.png", dpi=300, bbox_inches='tight')
plt.close()

print("✅ Figure 3 (Polished & Balanced) created successfully!")