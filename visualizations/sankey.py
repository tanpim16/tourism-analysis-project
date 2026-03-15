# Created by Pimkanit – Sankey Diagram
# Visitors → Secondary Cities → Revenue

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import numpy as np
import os

# ─── Style & Configuration ────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor':   'white',
    'font.family':      'sans-serif',
})

TOP_N = 15  # Show top N secondary cities; rest grouped as "Others"

# ─── Data Loading ─────────────────────────────────────────────────────────────
df = pd.read_csv('data/processed/tourism_combined_final.csv')

# Enrich with Region & City Type from master
master = pd.read_csv('data/processed/master_tourism_analysis.csv')
lookup = (
    master[['ProvinceThai', 'ProvinceEN', 'Region_EN', 'City_type_EN']]
    .drop_duplicates('ProvinceThai')
)
df = df.merge(lookup, left_on='province', right_on='ProvinceThai', how='left')
df = df.dropna(subset=['City_type_EN'])

# Filter to Secondary Cities only
df = df[df['City_type_EN'] == 'Secondary City'].copy()

# ─── Aggregate per Secondary City ────────────────────────────────────────────
city_agg = df.groupby('ProvinceEN').agg(
    thai_visitors   = ('thai_visitors',    'sum'),
    foreign_visitors= ('foreign_visitors', 'sum'),
    thai_revenue    = ('thai_revenue',     'sum'),
    foreign_revenue = ('foreign_revenue',  'sum'),
).reset_index()

city_agg['total_visitors'] = city_agg['thai_visitors'] + city_agg['foreign_visitors']
city_agg = city_agg.sort_values('total_visitors', ascending=False)

# Top N + Others
top_cities = city_agg.head(TOP_N)
others     = city_agg.iloc[TOP_N:]

others_row = pd.DataFrame([{
    'ProvinceEN':       f'Others ({len(others)} cities)',
    'thai_visitors':    others['thai_visitors'].sum(),
    'foreign_visitors': others['foreign_visitors'].sum(),
    'thai_revenue':     others['thai_revenue'].sum(),
    'foreign_revenue':  others['foreign_revenue'].sum(),
    'total_visitors':   others['total_visitors'].sum(),
}])

city_data = pd.concat([top_cities, others_row], ignore_index=True)
city_names = city_data['ProvinceEN'].tolist()

# ─── Build Nodes ─────────────────────────────────────────────────────────────
visitor_nodes = ['Thai Visitors', 'Foreign Visitors']
revenue_nodes = ['Thai Revenue', 'Foreign Revenue']

all_nodes = visitor_nodes + city_names + revenue_nodes
node_idx  = {n: i for i, n in enumerate(all_nodes)}

# ─── Build Links (source_idx, target_idx, value) ─────────────────────────────
links = []
for _, row in city_data.iterrows():
    city = row['ProvinceEN']
    # Left → Middle: visitor counts
    links.append((node_idx['Thai Visitors'],    node_idx[city], row['thai_visitors']))
    links.append((node_idx['Foreign Visitors'], node_idx[city], row['foreign_visitors']))
    # Middle → Right: revenue
    links.append((node_idx[city], node_idx['Thai Revenue'],    row['thai_revenue']))
    links.append((node_idx[city], node_idx['Foreign Revenue'], row['foreign_revenue']))

# ─── Color Palette ───────────────────────────────────────────────────────────
CITY_PALETTE = [
    '#3498DB', '#E74C3C', '#2ECC71', '#9B59B6', '#F39C12',
    '#1ABC9C', '#E67E22', '#8E44AD', '#2980B9', '#27AE60',
    '#D35400', '#16A085', '#C0392B', '#7F8C8D', '#2C3E50',
    '#95A5A6',
]

NODE_COLORS = {
    'Thai Visitors':    '#1B4F8A',
    'Foreign Visitors': '#E67E22',
    'Thai Revenue':     '#1B4F8A',
    'Foreign Revenue':  '#E67E22',
}
for i, c in enumerate(city_names):
    NODE_COLORS[c] = CITY_PALETTE[i % len(CITY_PALETTE)]

# ─── Helpers ─────────────────────────────────────────────────────────────────
def fmt_num(x):
    if x >= 1e9: return f'{x / 1e9:,.1f}B'
    if x >= 1e6: return f'{x / 1e6:,.1f}M'
    if x >= 1e3: return f'{x / 1e3:,.0f}K'
    return f'{x:,.0f}'

def fmt_rev(x):
    """Revenue is already in millions of THB in the CSV."""
    if x >= 1e6: return f'{x / 1e6:,.1f}T฿'
    if x >= 1e3: return f'{x / 1e3:,.1f}B฿'
    return f'{x:,.0f}M฿'

# ─── Sankey Drawing ──────────────────────────────────────────────────────────
def draw_sankey():
    fig, ax = plt.subplots(figsize=(20, 14))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Three columns
    col_x = [0.01, 0.38, 0.82]
    col_w = 0.08
    col_groups = [visitor_nodes, city_names, revenue_nodes]

    # Compute total in/out per node
    node_out = {n: 0.0 for n in all_nodes}
    node_in  = {n: 0.0 for n in all_nodes}
    for s, t, v in links:
        node_out[all_nodes[s]] += v
        node_in[all_nodes[t]]  += v
    node_size = {n: max(node_out[n], node_in[n]) for n in all_nodes}

    # Layout nodes vertically in each column
    gap = 0.008
    node_pos = {}  # name → (x, y_top, y_bot)

    for ci, nodes in enumerate(col_groups):
        total = sum(node_size[n] for n in nodes)
        usable = 1.0 - gap * (len(nodes) - 1)
        y = 1.0
        for n in nodes:
            h = (node_size[n] / total * usable) if total > 0 else 0
            node_pos[n] = (col_x[ci], y, y - h)
            y -= h + gap

    # Draw node rectangles
    for n in all_nodes:
        x, yt, yb = node_pos[n]
        color = NODE_COLORS.get(n, '#95A5A6')
        rect = mpatches.FancyBboxPatch(
            (x, yb), col_w, yt - yb,
            boxstyle='round,pad=0.003',
            facecolor=color, edgecolor='white', linewidth=1.2, alpha=0.92,
        )
        ax.add_patch(rect)

        mid_y = (yt + yb) / 2
        height = yt - yb

        if n in visitor_nodes:
            label = f'{n}\n{fmt_num(node_size[n])}'
            ax.text(x + col_w + 0.012, mid_y, label,
                    va='center', ha='left', fontsize=10, fontweight='bold', color='#2C3E50')
        elif n in revenue_nodes:
            label = f'{n}\n{fmt_rev(node_size[n])}'
            ax.text(x - 0.012, mid_y, label,
                    va='center', ha='right', fontsize=10, fontweight='bold', color='#2C3E50')
        else:
            # City label: inside if tall enough, else to the right
            if height > 0.035:
                ax.text(x + col_w / 2, mid_y + 0.006, n,
                        va='center', ha='center', fontsize=6.5, fontweight='bold', color='white')
                ax.text(x + col_w / 2, mid_y - 0.010, fmt_num(node_size[n]),
                        va='center', ha='center', fontsize=5.5, color='white', alpha=0.9)
            else:
                ax.text(x + col_w + 0.006, mid_y, f'{n}  {fmt_num(node_size[n])}',
                        va='center', ha='left', fontsize=5.5, fontweight='bold', color='#2C3E50')

    # Draw flow bands (bezier curves)
    out_cursor = {n: node_pos[n][1] for n in all_nodes}
    in_cursor  = {n: node_pos[n][1] for n in all_nodes}

    for s_i, t_i, val in links:
        sn, tn = all_nodes[s_i], all_nodes[t_i]
        sx, st, sb = node_pos[sn]
        tx, tt, tb = node_pos[tn]

        s_h = st - sb
        t_h = tt - tb

        sf = (val / node_size[sn] * s_h) if node_size[sn] > 0 else 0
        tf = (val / node_size[tn] * t_h) if node_size[tn] > 0 else 0

        sy_top = out_cursor[sn];  sy_bot = sy_top - sf;  out_cursor[sn] = sy_bot
        ty_top = in_cursor[tn];   ty_bot = ty_top - tf;   in_cursor[tn]  = ty_bot

        x0 = sx + col_w
        x1 = tx
        xm = (x0 + x1) / 2

        verts = [
            (x0, sy_top), (xm, sy_top), (xm, ty_top), (x1, ty_top),
            (x1, ty_bot), (xm, ty_bot), (xm, sy_bot), (x0, sy_bot),
            (x0, sy_top),
        ]
        codes = [
            Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
            Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
            Path.CLOSEPOLY,
        ]
        patch = mpatches.PathPatch(
            Path(verts, codes),
            facecolor=NODE_COLORS.get(sn, '#95A5A6'),
            edgecolor='none', alpha=0.20,
        )
        ax.add_patch(patch)

    # ─── Titles & column headers ─────────────────────────────────────────────
    ax.set_xlim(-0.06, 1.06)
    ax.set_ylim(-0.04, 1.12)
    ax.axis('off')

    ax.text(0.50, 1.09,
            'Secondary Cities: Visitors → City → Revenue',
            transform=ax.transAxes, fontsize=17, fontweight='bold',
            ha='center', va='top', color='#2C3E50')
    ax.text(0.50, 1.04,
            f'Top {TOP_N} secondary cities by total visitors  •  tourism_combined_final.csv  •  BE 2566–2568',
            transform=ax.transAxes, fontsize=10, ha='center', va='top',
            color='#7F8C8D', style='italic')

    for ci, label in enumerate(['No. of Visitors', 'Secondary Cities', 'Revenue']):
        ax.text(col_x[ci] + col_w / 2, 1.05, label,
                ha='center', fontsize=11, fontweight='bold', color='#34495E')

    plt.tight_layout()
    return fig


# ─── Generate & Save ─────────────────────────────────────────────────────────
fig = draw_sankey()

os.makedirs('visualizations', exist_ok=True)
fig.savefig('visualizations/Sankey_Revenue_Flow.png', dpi=300, bbox_inches='tight')
plt.show()
print('✓ Saved: visualizations/Sankey_Revenue_Flow.png')
