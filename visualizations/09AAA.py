# Created by Pimkanit – Foreign Visitor Analysis (6 Figures)
# Data: data/processed/foreign_visitors_combined.csv (MOTS 2023-2025)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import os

# ─── Style & Configuration ────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   "#2875C2",
    'axes.grid':        True,
    'grid.color':       "#7C7373",
    'grid.linewidth':   1.2,
    'font.family':      'sans-serif',
    'axes.spines.top':  False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom': False,
})

MONTH_ORDER = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

YEAR_COLORS = {2023: '#95A5A6', 2024: '#3498DB', 2025: '#E74C3C'}

REGION_COLORS = {
    'Asia and the Pacific': '#1B4F8A',
    'Europe':               '#E74C3C',
    'America':              '#2ECC71',
    'Middle East':          '#F39C12',
    'Oceania':              '#9B59B6',
    'Africa':               '#16A085',
}

OUT_DIR = 'visualizations'
os.makedirs(OUT_DIR, exist_ok=True)


def fmt(x):
    if x >= 1e6: return f'{x/1e6:.1f}M'
    if x >= 1e3: return f'{x/1e3:.0f}K'
    return f'{x:,.0f}'


# ─── Load Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/foreign_visitors_combined.csv')
ind = df[df['is_aggregate'] == False].copy()   # individual countries only
agg = df[df['is_aggregate'] == True].copy()    # region aggregates

ind['month_num'] = ind['month'].map({m: i for i, m in enumerate(MONTH_ORDER)})


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 – Top 15 Source Markets (Total Arrivals 2023–2025)
# ══════════════════════════════════════════════════════════════════════════════
print('Creating Figure 1: Top Source Markets ...')

top15 = (ind.groupby('country')['visitors'].sum()
         .sort_values(ascending=False).head(15))

fig1, ax1 = plt.subplots(figsize=(14, 8))
colors = plt.cm.Blues(np.linspace(0.85, 0.35, 15))
bars = ax1.barh(range(14, -1, -1), top15.values, color=colors, height=0.7,
                edgecolor='white', linewidth=0.5)

for i, (country, val) in enumerate(top15.items()):
    ax1.text(val + top15.max() * 0.01, 14 - i, fmt(val),
             va='center', ha='left', fontsize=9, fontweight='bold', color='#2C3E50')

ax1.set_yticks(range(14, -1, -1))
ax1.set_yticklabels(top15.index, fontsize=10)
ax1.set_xlabel('')
ax1.set_title('Top 15 Source Markets for International Tourists to Thailand',
              fontsize=16, fontweight='bold', color='#2C3E50', pad=15)
ax1.text(0.5, 1.02, 'Total arrivals 2023–2025 (MOTS)',
         transform=ax1.transAxes, ha='center', fontsize=10, color='#7F8C8D', style='italic')
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax1.set_xlim(0, top15.max() * 1.18)

plt.tight_layout()
fig1.savefig(f'{OUT_DIR}/F1_Top_Source_Markets.png', dpi=300, bbox_inches='tight')
plt.close(fig1)
print('  ✓ F1_Top_Source_Markets.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 – Year-over-Year Growth by Top 15 Countries
# ══════════════════════════════════════════════════════════════════════════════
print('Creating Figure 2: Year-over-Year Growth ...')

top15_names = top15.index.tolist()
yearly = (ind[ind['country'].isin(top15_names)]
          .groupby(['country', 'year'])['visitors'].sum()
          .unstack(fill_value=0))

# Calculate YoY % change
yoy = pd.DataFrame(index=top15_names)
if 2024 in yearly.columns and 2023 in yearly.columns:
    yoy['2023→2024'] = ((yearly[2024] - yearly[2023]) / yearly[2023] * 100).reindex(top15_names)
if 2025 in yearly.columns and 2024 in yearly.columns:
    yoy['2024→2025'] = ((yearly[2025] - yearly[2024]) / yearly[2024] * 100).reindex(top15_names)

fig2, ax2 = plt.subplots(figsize=(14, 9))
x = np.arange(len(top15_names))
width = 0.35

if '2023→2024' in yoy.columns:
    bars1 = ax2.barh(x + width/2, yoy['2023→2024'], width, label='2023 → 2024',
                     color='#3498DB', edgecolor='white', linewidth=0.5)
if '2024→2025' in yoy.columns:
    bars2 = ax2.barh(x - width/2, yoy['2024→2025'], width, label='2024 → 2025',
                     color='#E74C3C', edgecolor='white', linewidth=0.5)

# Add value labels
for col_name, offset, color in [('2023→2024', width/2, '#3498DB'), ('2024→2025', -width/2, '#E74C3C')]:
    if col_name in yoy.columns:
        for i, val in enumerate(yoy[col_name]):
            if pd.notna(val):
                ha = 'left' if val >= 0 else 'right'
                xpos = val + (2 if val >= 0 else -2)
                ax2.text(xpos, i + offset, f'{val:+.1f}%',
                         va='center', ha=ha, fontsize=7.5, fontweight='bold', color='#2C3E50')

ax2.axvline(0, color='#2C3E50', linewidth=0.8, alpha=0.5)
ax2.set_yticks(x)
ax2.set_yticklabels(top15_names, fontsize=9)
ax2.set_xlabel('% Change in Arrivals', fontsize=11)
ax2.set_title('Year-over-Year Growth: Top 15 Source Markets',
              fontsize=16, fontweight='bold', color='#2C3E50', pad=15)
ax2.text(0.5, 1.02, 'Annual % change in tourist arrivals',
         transform=ax2.transAxes, ha='center', fontsize=10, color='#7F8C8D', style='italic')
ax2.legend(loc='lower right', fontsize=10, framealpha=0.9)
ax2.invert_yaxis()

plt.tight_layout()
fig2.savefig(f'{OUT_DIR}/F2_YoY_Growth.png', dpi=300, bbox_inches='tight')
plt.close(fig2)
print('  ✓ F2_YoY_Growth.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 – Seasonality Heatmap (Top 12 Countries × Month)
# ══════════════════════════════════════════════════════════════════════════════
print('Creating Figure 3: Seasonality Heatmap ...')

top12_names = top15.index[:12].tolist()
heat_data = (ind[ind['country'].isin(top12_names)]
             .groupby(['country', 'month'])['visitors'].sum()
             .unstack())
heat_data = heat_data[MONTH_ORDER].reindex(top12_names)

# Normalize per country (row-wise) for seasonality pattern
heat_norm = heat_data.div(heat_data.max(axis=1), axis=0)

fig3, ax3 = plt.subplots(figsize=(14, 7))
im = ax3.imshow(heat_norm.values, cmap='YlOrRd', aspect='auto', vmin=0.3, vmax=1.0)

ax3.set_xticks(range(12))
ax3.set_xticklabels(MONTH_ORDER, fontsize=10)
ax3.set_yticks(range(len(top12_names)))
ax3.set_yticklabels(top12_names, fontsize=10)

# Annotate cells with actual values
for i in range(len(top12_names)):
    for j in range(12):
        val = heat_data.values[i, j]
        norm_val = heat_norm.values[i, j]
        text_color = 'white' if norm_val > 0.7 else '#2C3E50'
        ax3.text(j, i, fmt(val), ha='center', va='center',
                 fontsize=6.5, color=text_color, fontweight='bold')

ax3.set_title('Seasonality of Tourist Arrivals by Nationality',
              fontsize=16, fontweight='bold', color='#2C3E50', pad=15)
ax3.text(0.5, 1.04, 'Monthly total 2023–2025 (darker = peak season for each country)',
         transform=ax3.transAxes, ha='center', fontsize=10, color='#7F8C8D', style='italic')

cbar = plt.colorbar(im, ax=ax3, shrink=0.6, pad=0.02)
cbar.set_label('Relative intensity (per country)', fontsize=9)

plt.tight_layout()
fig3.savefig(f'{OUT_DIR}/F3_Seasonality_Heatmap.png', dpi=300, bbox_inches='tight')
plt.close(fig3)
print('  ✓ F3_Seasonality_Heatmap.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 – Regional Share Shift (Stacked Bar by Year)
# ══════════════════════════════════════════════════════════════════════════════
print('Creating Figure 4: Regional Shift Analysis ...')

# Use region-level aggregates from the data
region_agg_names = list(REGION_COLORS.keys())
region_yearly = (agg[agg['country'].isin(region_agg_names)]
                 .groupby(['country', 'year'])['visitors'].sum()
                 .unstack(fill_value=0))

# Calculate shares
region_shares = region_yearly.div(region_yearly.sum(axis=0), axis=1) * 100

fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(18, 8), gridspec_kw={'width_ratios': [3, 2]})

# Left: stacked bar chart
years = sorted(region_yearly.columns)
bar_width = 0.6
bottoms = {y: 0 for y in years}

for region in region_agg_names:
    if region not in region_yearly.index:
        continue
    vals = [region_yearly.loc[region, y] if y in region_yearly.columns else 0 for y in years]
    color = REGION_COLORS[region]
    ax4a.bar(years, vals, bar_width, bottom=[bottoms[y] for y in years],
             label=region, color=color, edgecolor='white', linewidth=0.5)
    for i, y in enumerate(years):
        bottoms[y] += vals[i]

ax4a.set_ylabel('Total Arrivals', fontsize=11)
ax4a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax4a.set_xticks(years)
ax4a.set_title('Total Arrivals by Region',
               fontsize=14, fontweight='bold', color='#2C3E50')
ax4a.legend(loc='upper left', fontsize=8, framealpha=0.9)

# Right: share % change table-like horizontal bars
if len(years) >= 2:
    first_yr, last_yr = years[0], years[-1]
    share_change = region_shares[last_yr] - region_shares[first_yr]
    share_change = share_change.reindex(region_agg_names).dropna().sort_values()

    colors_bar = [REGION_COLORS.get(r, '#95A5A6') for r in share_change.index]
    ax4b.barh(range(len(share_change)), share_change.values, color=colors_bar,
              edgecolor='white', linewidth=0.5, height=0.6)
    ax4b.set_yticks(range(len(share_change)))
    ax4b.set_yticklabels(share_change.index, fontsize=10)
    ax4b.axvline(0, color='#2C3E50', linewidth=0.8, alpha=0.5)
    ax4b.set_xlabel('Change in share (pp)', fontsize=11)
    ax4b.set_title(f'Market Share Shift ({first_yr}→{last_yr})',
                   fontsize=14, fontweight='bold', color='#2C3E50')

    for i, val in enumerate(share_change.values):
        ha = 'left' if val >= 0 else 'right'
        ax4b.text(val + (0.2 if val >= 0 else -0.2), i, f'{val:+.1f}pp',
                  va='center', ha=ha, fontsize=9, fontweight='bold', color='#2C3E50')

fig4.suptitle('Regional Composition of International Tourists to Thailand',
              fontsize=16, fontweight='bold', color='#2C3E50', y=1.02)

plt.tight_layout()
fig4.savefig(f'{OUT_DIR}/F4_Regional_Shift.png', dpi=300, bbox_inches='tight')
plt.close(fig4)
print('  ✓ F4_Regional_Shift.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 – Post-COVID Recovery Trajectories (Top 10, Monthly Line)
# ══════════════════════════════════════════════════════════════════════════════
print('Creating Figure 5: Recovery Trajectories ...')

top10_names = top15.index[:10].tolist()
monthly = (ind[ind['country'].isin(top10_names)]
           .copy())
monthly['date_sort'] = monthly['year'] * 100 + monthly['month_num']
monthly = monthly.sort_values('date_sort')
monthly['date_label'] = monthly['month'].str[:3] + '\n' + monthly['year'].astype(str).str[-2:]

# Create a sequential x position
date_keys = monthly[['year', 'month']].drop_duplicates().sort_values(['year', 'month'],
            key=lambda col: col.map({m: i for i, m in enumerate(MONTH_ORDER)}) if col.name == 'month' else col)
# Actually re-sort properly
monthly = monthly.sort_values(['year', 'month_num'])
date_order = monthly.groupby(['year', 'month']).ngroups

# Pivot for plotting
pivot = monthly.pivot_table(index=['year', 'month_num', 'month'],
                            columns='country', values='visitors', aggfunc='sum')
pivot = pivot.sort_index()

fig5, ax5 = plt.subplots(figsize=(18, 9))
line_colors = plt.cm.tab10(np.linspace(0, 1, 10))

x = range(len(pivot))
for i, country in enumerate(top10_names):
    if country in pivot.columns:
        ax5.plot(x, pivot[country].values, label=country, color=line_colors[i],
                 linewidth=1.8, alpha=0.85)

# X axis labels (every 3 months)
labels = [f"{row[2]}\n{row[0]}" for row in pivot.index]
ax5.set_xticks(range(0, len(labels), 3))
ax5.set_xticklabels([labels[i] for i in range(0, len(labels), 3)], fontsize=8, rotation=0)
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))

ax5.set_title('Monthly Arrival Trends: Top 10 Source Markets (2023–2025)',
              fontsize=16, fontweight='bold', color='#2C3E50', pad=15)
ax5.text(0.5, 1.02, 'Recovery and growth trajectories post-COVID',
         transform=ax5.transAxes, ha='center', fontsize=10, color='#7F8C8D', style='italic')
ax5.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=9, framealpha=0.9)
ax5.set_ylabel('Monthly Arrivals', fontsize=11)

plt.tight_layout()
fig5.savefig(f'{OUT_DIR}/F5_Recovery_Trajectories.png', dpi=300, bbox_inches='tight')
plt.close(fig5)
print('  ✓ F5_Recovery_Trajectories.png')


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 7 – Foreign Arrivals vs Provincial Foreign Revenue
# ══════════════════════════════════════════════════════════════════════════════
print('Creating Figure 7: Arrivals × Provincial Foreign Revenue ...')

# Load provincial tourism data
prov_df = pd.read_csv('data/processed/tourism_combined_final.csv')

# Enrich with master for province English name
master = pd.read_csv('data/processed/master_tourism_analysis.csv')
lookup = (master[['ProvinceThai', 'ProvinceEN', 'Region_EN', 'City_type_EN']]
          .drop_duplicates('ProvinceThai'))
prov_df = prov_df.merge(lookup, left_on='province', right_on='ProvinceThai', how='left')
prov_df = prov_df.dropna(subset=['ProvinceEN'])

# Monthly foreign arrivals total (from MOTS Grand Total)
grand = agg[agg['country'] == 'Grand Total'].copy()
grand['month_num'] = grand['month'].map({m: i for i, m in enumerate(MONTH_ORDER)})

# Provincial foreign revenue & visitors aggregated yearly
prov_df['Year_CE'] = prov_df['year'].astype(int) - 543
prov_yearly = (prov_df.groupby(['ProvinceEN', 'Year_CE', 'City_type_EN'])
               .agg(foreign_visitors=('foreign_visitors', 'sum'),
                    foreign_revenue=('foreign_revenue', 'sum'))
               .reset_index())

# ── Fig 7a: Scatter – provincial foreign visitors vs foreign revenue ──
prov_total = (prov_df.groupby(['ProvinceEN', 'City_type_EN'])
              .agg(foreign_visitors=('foreign_visitors', 'sum'),
                   foreign_revenue=('foreign_revenue', 'sum'))
              .reset_index())

fig7, (ax7a, ax7b) = plt.subplots(1, 2, figsize=(18, 8))

# Scatter: foreign visitors vs revenue by province
for ctype, color in [('Major City', '#1B4F8A'), ('Secondary City', '#16A085')]:
    mask = prov_total['City_type_EN'] == ctype
    sub = prov_total[mask]
    ax7a.scatter(sub['foreign_visitors'], sub['foreign_revenue'],
                 c=color, label=ctype, alpha=0.65, s=50, edgecolors='white', linewidth=0.5)
    # Label top provinces
    top_prov = sub.nlargest(5, 'foreign_revenue')
    for _, row in top_prov.iterrows():
        ax7a.annotate(row['ProvinceEN'], (row['foreign_visitors'], row['foreign_revenue']),
                      fontsize=6.5, color='#2C3E50', fontweight='bold',
                      xytext=(5, 5), textcoords='offset points')

ax7a.set_xlabel('Total Foreign Visitors', fontsize=11)
ax7a.set_ylabel('Total Foreign Revenue (M THB)', fontsize=11)
ax7a.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax7a.set_title('Foreign Visitors vs Revenue by Province',
               fontsize=14, fontweight='bold', color='#2C3E50')
ax7a.legend(fontsize=10, framealpha=0.9)

# ── Fig 7b: Monthly trend – MOTS arrivals vs domestic foreign revenue ──
# Align by year-month
grand_monthly = (grand.groupby(['year', 'month_num', 'month'])['visitors'].sum()
                 .reset_index().sort_values(['year', 'month_num']))

# Convert provincial year to CE and aggregate monthly
prov_df['month_num'] = prov_df['month'].map({m: i for i, m in enumerate(MONTH_ORDER)})
prov_monthly = (prov_df.groupby(['Year_CE', 'month_num'])
                .agg(foreign_revenue=('foreign_revenue', 'sum'))
                .reset_index()
                .rename(columns={'Year_CE': 'year'}))

merged = grand_monthly.merge(prov_monthly, on=['year', 'month_num'], how='inner')
merged = merged.sort_values(['year', 'month_num'])

ax7b_twin = ax7b.twinx()
x = range(len(merged))
ax7b.bar(x, merged['visitors'], color='#3498DB', alpha=0.5, label='MOTS Int\'l Arrivals')
ax7b_twin.plot(x, merged['foreign_revenue'], color='#E74C3C', linewidth=2.5,
               label='Provincial Foreign Revenue', marker='o', markersize=4)

labels_7 = [f"{merged.iloc[i]['month'][:3]}\n{int(merged.iloc[i]['year'])}" for i in range(len(merged))]
ax7b.set_xticks(range(0, len(labels_7), 3))
ax7b.set_xticklabels([labels_7[i] for i in range(0, len(labels_7), 3)], fontsize=7)
ax7b.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax7b_twin.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))

ax7b.set_ylabel('International Arrivals (MOTS)', fontsize=10, color='#3498DB')
ax7b_twin.set_ylabel('Foreign Revenue in Provinces (M THB)', fontsize=10, color='#E74C3C')
ax7b.set_title('International Arrivals vs Provincial Foreign Revenue',
               fontsize=14, fontweight='bold', color='#2C3E50')

# Combined legend
lines1, labels1 = ax7b.get_legend_handles_labels()
lines2, labels2 = ax7b_twin.get_legend_handles_labels()
ax7b.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9, framealpha=0.9)

fig7.suptitle('Connecting International Arrivals with Provincial Tourism Revenue',
              fontsize=16, fontweight='bold', color='#2C3E50', y=1.02)

plt.tight_layout()
fig7.savefig(f'{OUT_DIR}/F7_Arrivals_vs_Revenue.png', dpi=300, bbox_inches='tight')
plt.close(fig7)
print('  ✓ F7_Arrivals_vs_Revenue.png')


print('\n✅ All 6 figures saved to visualizations/')
