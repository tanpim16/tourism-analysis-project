# ─── IMPORT ──────────────────────────────────────────────────────────────────
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
from matplotlib.gridspec import GridSpec
import os

# ─── Style ───────────────────────────────────────────────────────────────────
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
    if x >= 1e9: return f'{x/1e9:.1f}B'
    if x >= 1e6: return f'{x/1e6:.1f}M'
    if x >= 1e3: return f'{x/1e3:.0f}K'
    return f'{x:,.0f}'

def moving_avg(series, window=3):
    return series.rolling(window, min_periods=1, center=True).mean()

# ─── Load Data ────────────────────────────────────────────────────────────────
data_path = 'data/processed/master_tourism_analysis.csv'

if not os.path.exists(data_path):
    print("❌ ไม่พบไฟล์:", data_path)
    print("📂 Available:", os.listdir('data/processed'))
    raise FileNotFoundError

df = pd.read_csv(data_path)

df['Year_CE'] = df['Year'].astype(int) - 543
df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')

df_plot = (
    df.groupby(['date', 'City_type_EN'])[['total_visitors', 'total_revenue']]
    .sum()
    .reset_index()
    .query("'2023-01-01' <= date <= '2025-12-01'")
    .sort_values('date')
)

print("✅ Data loaded:", df_plot.shape)

# ─── Output Folder ────────────────────────────────────────────────────────────
os.makedirs('visualizations', exist_ok=True)

# ─── Chart Config (ใช้ filename เดิม) ────────────────────────────────────────
CHART_CONFIGS = [
    {
        'col':      'total_visitors',
        'title':    'Monthly Tourist Arrivals',
        'subtitle': 'Number of visitors  ·  Jan 2023 – Dec 2025',
        'ylabel':   'Visitors',
        'filename': 'Figure_1_total_visitors_trend.png',
    },
    {
        'col':      'total_revenue',
        'title':    'Monthly Tourism Income',
        'subtitle': 'Total revenue (Million THB)  ·  Jan 2023 – Dec 2025',
        'ylabel':   'Million THB',
        'filename': 'Figure_1_total_Revenue_trend.png',
    },
]

# ─── Create Chart ─────────────────────────────────────────────────────────────
def create_chart(cfg):
    col      = cfg['col']
    filename = cfg['filename']

    groups = {}
    for name in ['Major City', 'Secondary City']:
        sub = df_plot[df_plot['City_type_EN'] == name].sort_values('date').copy()
        sub['ma'] = moving_avg(sub[col])
        groups[name] = sub

    fig = plt.figure(figsize=(12, 6))
    gs  = GridSpec(1, 1, figure=fig, left=0.07, right=0.96, top=0.78, bottom=0.12)
    ax  = fig.add_subplot(gs[0, 0])

    # ─── Plot ─────────────────────────────────────────
    for name, color in COLORS.items():
        sub   = groups[name]
        dates = sub['date']
        raw   = sub[col]
        ma    = sub['ma']

        ax.fill_between(dates, raw, alpha=FILL_ALPHA, color=color)
        ax.plot(dates, ma, color=color, linewidth=5, alpha=0.15)
        ax.plot(dates, raw, color=color, linewidth=2.5, alpha=0.85)

        q_mask = dates.dt.month.isin([1, 4, 7, 10])
        ax.scatter(dates[q_mask], raw[q_mask], s=35,
                   color=color, edgecolors='white', linewidths=1.2)

    # ─── Peak / Drop (Value label size 6) ─────────────
    for name, color in COLORS.items():
        sub = groups[name]
        if sub.empty: continue

        peak = sub.loc[sub[col].idxmax()]
        drop = sub.loc[sub[col].idxmin()]

        ax.annotate(f'▲ {fmt(peak[col])}',
                    xy=(peak['date'], peak[col]),
                    xytext=(0, 14),
                    textcoords='offset points',
                    fontsize=6, fontweight='bold',
                    color=color, ha='center',
                    arrowprops=dict(arrowstyle='->', color=color))

        ax.annotate(f'▼ {fmt(drop[col])}',
                    xy=(drop['date'], drop[col]),
                    xytext=(0, -16),
                    textcoords='offset points',
                    fontsize=6, fontweight='bold',
                    color=color, ha='center',
                    arrowprops=dict(arrowstyle='->', color=color))

    # ─── Axis ─────────────────────────────────────────
    ax.set_ylim(0, df_plot[col].max() * 1.35)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: fmt(x)))
    ax.tick_params(axis='y', labelsize=10)

    ticks = pd.date_range('2023-01-01', '2026-01-01', freq='QS-JAN')
    ax.set_xticks(ticks)
    ax.set_xticklabels([d.strftime('%b\n%Y') for d in ticks], fontsize=9)

    ax.set_ylabel(cfg['ylabel'], fontsize=10)

    # ─── Subplot Title ───────────────────────────────
    ax.set_title(cfg['subtitle'], fontsize=12, fontweight='bold', pad=10)

    # ─── Legend ─────────────────────────────────────
    handles = [
        mpatches.Patch(color=COLORS['Major City'], label='Major City'),
        mpatches.Patch(color=COLORS['Secondary City'], label='Secondary City'),
    ]

    ax.legend(handles=handles,
              title='City Type',
              title_fontsize=10,
              fontsize=9,
              loc='upper left')

    # ─── Figure Title (สำคัญ) ───────────────────────
    fig.suptitle(cfg['title'],
                 fontsize=16,
                 fontweight='bold',
                 y=0.87)

    # Source
    fig.text(0.07, 0.04,
             'Source: Thailand Tourism Authority',
             fontsize=8)

    # Save
    save_path = f'visualizations/{filename}'
    print("💾 Saving:", save_path)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f'✅ Successfully generated: {filename}')

# ─── Run ──────────────────────────────────────────────────────────────────────
for cfg in CHART_CONFIGS:
    create_chart(cfg)

print('\n🚀 CHARTS ARE READY FOR YOUR REPORT!')