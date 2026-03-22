import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

# ─── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  'white',
    'axes.facecolor':    '#F8F9FA',
    'axes.grid':         False,  # Global grid off
    'font.family':       'sans-serif',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom':False,
})

# 1. LOAD DATA
file_path = 'data/processed/final_master_with_trends.csv'
if not os.path.exists(file_path):
    file_path = 'final_master_with_trends.csv'

df = pd.read_csv(file_path)

# 2. [PATCH] Fix Nakhon Ratchasima & Data Cleaning
df['ProvinceThai'] = df['ProvinceThai'].astype(str).str.strip()

mask_korat = df['ProvinceThai'] == 'นครราชสีมา'
df.loc[mask_korat, 'ProvinceEN'] = 'Nakhon Ratchasima'
df.loc[mask_korat, 'City_type_TH'] = 'เมืองหลัก'
df.loc[mask_korat, 'City_type_EN'] = 'Primary City'

df['thai_revenue'] = df['thai_revenue'].fillna(0)
df['foreign_revenue'] = df['foreign_revenue'].fillna(0)
df['Price_Index'] = df['Price_Index'].fillna(100)

# 3. CALCULATE REAL REVENUE
df['thai_rev_real'] = df['thai_revenue'] / (df['Price_Index'] / 100)
df['fore_rev_real'] = df['foreign_revenue'] / (df['Price_Index'] / 100)

# 4. AGGREGATION
agg_df = (
    df.groupby(['ProvinceEN', 'City_type_TH'])[['thai_rev_real', 'fore_rev_real']]
    .sum()
    .reset_index()
)
agg_df['total_rev'] = agg_df['thai_rev_real'] + agg_df['fore_rev_real']

# 5. SPLIT
primary_df = agg_df[
    agg_df['City_type_TH'].str.contains('หลัก', na=False)
].copy().sort_values('total_rev', ascending=True)

secondary_df = agg_df[
    agg_df['City_type_TH'].str.contains('รอง', na=False)
].copy().sort_values('total_rev', ascending=True)

# 6. VISUALIZATION (Same Size Subplots)
row_height = 0.35
# Calculate height based on the longest list (Secondary Cities)
fig_height = max(len(primary_df), len(secondary_df)) * row_height + 1.5

# Using standard subplots guarantees ax_left and ax_right are exactly the same height
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(24, fig_height), facecolor='white')

bg_color = '#fcfcfc'

# --- LEFT PANEL: Major Cities ---
ax_left.set_facecolor(bg_color)
ax_left.barh(primary_df['ProvinceEN'], primary_df['thai_rev_real'], color='#89c4e1', label='Domestic (Thai)')
ax_left.barh(primary_df['ProvinceEN'], primary_df['fore_rev_real'], left=primary_df['thai_rev_real'], color='#1a6fa8', label='International (Foreign)')

# Value Labels: fontsize=8, fontweight='bold'
max_l = primary_df['total_rev'].max()
for i, total in enumerate(primary_df['total_rev']):
    ax_left.text(total + (max_l * 0.01), i, f'{total:,.0f}', va='center', fontsize=8, fontweight='bold')

# Subplot Title: fontsize=14, fontweight='bold'
ax_left.set_title('Major Cities: Revenue Powerhouses', fontsize=16, fontweight='bold', pad=10)
ax_left.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

# Legend Title: fontsize=14, fontweight='normal' | Legend Text: fontsize=14
ax_left.legend(title='Revenue Type', title_fontsize=14, loc='lower right', frameon=True, fontsize=14)
# X-axis Ticks: fontsize=12 | Y-axis Label: fontsize=12
ax_left.tick_params(axis='x', labelsize=12)
ax_left.tick_params(axis='y', labelsize=12)

# --- RIGHT PANEL: Secondary Cities ---
ax_right.set_facecolor(bg_color)
ax_right.barh(secondary_df['ProvinceEN'], secondary_df['thai_rev_real'], color='#a8ddb5', label='Domestic (Thai)')
ax_right.barh(secondary_df['ProvinceEN'], secondary_df['fore_rev_real'], left=secondary_df['thai_rev_real'], color='#2a8f48', label='International (Foreign)')

# Value Labels: fontsize=8, fontweight='bold'
max_r = secondary_df['total_rev'].max()
for i, total in enumerate(secondary_df['total_rev']):
    ax_right.text(total + (max_r * 0.01), i, f'{total:,.0f}', va='center', fontsize=8, fontweight='bold')

# Subplot Title: fontsize=12, fontweight='bold'
ax_right.set_title('Secondary Cities: Emerging Potential', fontsize=16, fontweight='bold', pad=10)
ax_right.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

# Legend Title: fontsize=10, fontweight='normal' | Legend Text: fontsize=9
ax_right.legend(title='Revenue Type', title_fontsize=14, loc='lower right', frameon=True, fontsize=14)
# X-axis Ticks: fontsize=12 | Y-axis Label: fontsize=12
ax_right.tick_params(axis='x', labelsize=12)
ax_right.tick_params(axis='y', labelsize=12)

# 7. FINAL TOUCHES
# Figure Title (suptitle): fontsize=18, fontweight='bold', y=0.87
plt.suptitle('Major vs. Secondary Cities: Total Revenue Comparison', fontsize=18, fontweight='bold', y=0.87)

# FIXED SPACING: Stop the subplots at 0.86 so they don't crash into the title at 0.87
plt.tight_layout(rect=[0.05, 0.01, 0.95, 0.86], w_pad=10)

# SAVE
os.makedirs('visualizations', exist_ok=True)
output_path = 'visualizations/Figure_7B_Revenue_Comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"🚀 กราฟถูกสร้างสำเร็จและบันทึกไว้ที่: {output_path}")