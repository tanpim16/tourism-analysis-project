import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
from matplotlib.gridspec import GridSpec
import numpy as np
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
    'Major City':     '#1B4F8A',
    'Secondary City': '#16A085',
}
FILL_ALPHA = 0.12

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt(x):
    if x >= 1e9:  return f'{x/1e9:.1f}B'
    if x >= 1e6:  return f'{x/1e6:.1f}M'
    if x >= 1e3:  return f'{x/1e3:.0f}K'
    return f'{x:,.0f}'

def moving_avg(series, window=3):
    return series.rolling(window, min_periods=1, center=True).mean()

# ─── Data Loading ─────────────────────────────────────────────────────────────
data_path = 'data/processed/master_tourism_analysis.csv'
if not os.path.exists(data_path):
    print("❌ ไม่พบไฟล์ข้อมูล"); exit()

df = pd.read_csv(data_path)
df['Year_CE'] = df['Year'].astype(int) - 543
df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')
df_plot = (
    df.groupby(['date', 'City_type_EN'])[['total_visitors', 'total_revenue', 'real_revenue']]
    .sum()
    .reset_index()
    .query("'2023-01-01' <= date <= '2025-12-01'")
    .sort_values('date')
)

os.makedirs('visualizations', exist_ok=True)

# ─── Chart factory ────────────────────────────────────────────────────────────
CHART_CONFIGS = [
    {
        'col':      'total_visitors',
        'title':    'Monthly Tourist Arrivals',
        'subtitle': 'Number of visitors  ·  Jan 2023 – Dec 2025',
        'ylabel':   'Visitors',
        'filename': 'Figure 1.png',
    # Figure 4 moved to figure_4.py
    },
    # Figure 3 removed
]

def create_chart(cfg):
    col      = cfg['col']
    filename = cfg['filename']

    groups = {}
    for name in ['Major City', 'Secondary City']:
        sub = df_plot[df_plot['City_type_EN'] == name].sort_values('date').copy()
        sub['ma'] = moving_avg(sub[col])
        groups[name] = sub

    fig = plt.figure(figsize=(16, 8))
    gs  = GridSpec(1, 1, figure=fig, left=0.07, right=0.96, top=0.78, bottom=0.12)
    ax  = fig.add_subplot(gs[0, 0])

    for name, color in [('Major City', COLORS['Major City']),
                         ('Secondary City', COLORS['Secondary City'])]:
        sub   = groups[name]
        dates = sub['date']
        raw   = sub[col]
        ma    = sub['ma']

        ax.fill_between(dates, raw, alpha=FILL_ALPHA, color=color, zorder=1)
        # 1. ข้อมูลจริง (Actual) — ทำให้เด่นขึ้น (เส้นทึบ หนาปานกลาง)
        ax.plot(dates, raw, color=color, alpha=0.8, linewidth=2.5, 
                label='Monthly actual', zorder=3)
        
        # 2. เส้น MA — ทำให้เป็นตัวสนับสนุน (เส้นทึบ หนาขึ้นแต่จางลง)
        ax.plot(dates, ma, color=color, linewidth=5, alpha=0.2, 
                solid_capstyle='round', zorder=2)
        
        q_mask = dates.dt.month.isin([1, 4, 7, 10])
        ax.scatter(dates[q_mask], ma[q_mask], color=color, s=45, zorder=4, edgecolors='white', linewidths=1.5)

    for name, color in [('Major City', COLORS['Major City']),
                         ('Secondary City', COLORS['Secondary City'])]:
        sub  = groups[name]
        peak = sub.loc[sub[col].idxmax()]
        drop = sub.loc[sub[col].idxmin()]

        ax.annotate(f'▲ {fmt(peak[col])}', xy=(peak['date'], peak[col]), xytext=(0, 16),
                    textcoords='offset points', fontsize=9, color=color, ha='center', va='bottom', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=color, lw=1, mutation_scale=10))
        
        ax.annotate(f'▼ {fmt(drop[col])}', xy=(drop['date'], drop[col]), xytext=(0, -18),
                    textcoords='offset points', fontsize=9, color=color, ha='center', va='top', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=color, lw=1, mutation_scale=10))

    global_max = df_plot[col].max()
    ax.set_ylim(0, global_max * 1.35)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt(x)))
    ax.tick_params(axis='y', labelsize=10, colors='#555')

    ticks = pd.date_range('2023-01-01', '2026-01-01', freq='QS-JAN')
    ax.set_xticks(ticks)
    ax.set_xticklabels([d.strftime('%b\n%Y') for d in ticks], fontsize=9.5, color='#555')
    ax.set_xlim(pd.Timestamp('2022-12-01'), pd.Timestamp('2025-12-31'))
    ax.set_ylabel(cfg['ylabel'], fontsize=10, color='#666', labelpad=8)

   # ── Legend (ปรับให้ตรงกับเส้นที่เปลี่ยนไป) ──
    handles = [
        mpatches.Patch(color=COLORS['Major City'],     label='Major City'),
        mpatches.Patch(color=COLORS['Secondary City'], label='Secondary City'),
        
        # 1. ปรับ Monthly actual ให้เป็นเส้นทึบตามกราฟใหม่
        plt.Line2D([0], [0], color='#888', linewidth=2, linestyle='-', 
                   alpha=0.8, label='Monthly actual'),
        
        # 2. ปรับ 3-mo moving avg ให้ดูหนาขึ้นแต่จางลง (เป็นเงาหลัง)
        plt.Line2D([0], [0], color='#888', linewidth=4, 
                   alpha=0.2, solid_capstyle='round', label='Trend (3-mo MA)'),
    ]
    ax.legend(handles=handles, loc='upper left', fontsize=9.5, framealpha=0.9, edgecolor='#DDD')

    fig.text(0.07, 0.92, cfg['title'], fontsize=20, fontweight='bold', color='#1A1A2E', va='bottom')
    fig.text(0.07, 0.865, cfg['subtitle'], fontsize=11, color='#888', va='bottom')

    fig.text(0.07, 0.04, 'Source: Thailand Tourism Authority  ·  Shaded area = raw monthly data', fontsize=8.5, color='#AAA')

    plt.savefig(f'visualizations/{filename}', dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f'✅ {filename}')

for cfg in CHART_CONFIGS:
    create_chart(cfg)
    # Figure 4 moved to figure_4.py

print('\n🚀 ALL CHARTS DONE!')