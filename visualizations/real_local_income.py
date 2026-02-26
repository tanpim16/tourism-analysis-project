import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter
import matplotlib.patches as mpatches

# ─── Global Style ─────────────────────────────────────────────────────────────
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

FILL_ALPHA = 0.18


def moving_avg(series, window: int = 3):
    """Simple moving average with edge handling."""
    return series.rolling(window=window, min_periods=1).median()


def fmt(x: float) -> str:
    """Format numbers in million THB with commas."""
    if pd.isna(x):
        return ""
    return f"{x:,.0f}"


def load_real_revenue_data():
    """Load master data and aggregate real revenue by month and city type."""
    data_path = "data/processed/master_tourism_analysis.csv"
    df = pd.read_csv(data_path)

    # Convert Thai BE → CE and build monthly date
    df['Year_CE'] = df['Year'].astype(int) - 543
    df['date'] = pd.to_datetime(
        df['Year_CE'].astype(str) + '-' + df['Month'],
        format='%Y-%b'
    )

    # Filter to study window
    df = df.query("'2023-01-01' <= date <= '2025-12-01'")

    # Aggregate real revenue by month and city type
    df_agg = (
        df.groupby(['date', 'City_type_EN'])['real_revenue']
        .sum()
        .reset_index()
    )

    return df_agg


# Precompute plotting dataframe
df_plot = load_real_revenue_data()


FIGURE_6_CONFIG = {
    'col':      'real_revenue',
    'title':    'Real Local Income Generation',
    'subtitle': 'Real tourism revenue (CPI-adjusted) · Jan 2023 – Dec 2025',
    'ylabel':   'Revenue (Million THB, real)',
    'filename': 'Figure 6.png',
}

def create_figure_4_chart(cfg):
    col      = cfg['col']
    filename = cfg['filename']

    groups = {}
    for name in ['Major City', 'Secondary City']:
        sub = df_plot[df_plot['City_type_EN'] == name].sort_values('date').copy()
        sub['ma'] = moving_avg(sub[col])
        groups[name] = sub

    os.makedirs('visualizations', exist_ok=True)

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
        ax.plot(dates, raw, color=color, alpha=0.8, linewidth=2.5, 
                label='Monthly actual', zorder=3)
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

    handles = [
        mpatches.Patch(color=COLORS['Major City'],     label='Major City'),
        mpatches.Patch(color=COLORS['Secondary City'], label='Secondary City'),
        plt.Line2D([0], [0], color='#888', linewidth=2, linestyle='-', 
                   alpha=0.8, label='Monthly actual'),
        plt.Line2D([0], [0], color='#888', linewidth=4, 
                   alpha=0.2, solid_capstyle='round', label='Trend (3-mo MA)'),
    ]
    ax.legend(handles=handles, loc='upper left', fontsize=9.5, framealpha=0.9, edgecolor='#DDD')

    fig.text(0.07, 0.92, cfg['title'], fontsize=20, fontweight='bold', color='#1A1A2E', va='bottom')
    fig.text(0.07, 0.865, cfg['subtitle'], fontsize=11, color='#888', va='bottom')
    fig.text(0.07, 0.04, 'Source: Thailand Tourism Authority  ·  Shaded area = raw monthly data', fontsize=8.5, color='#AAA')

    plt.savefig(f"visualizations/{filename}", dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f'✅ {filename}')


def create_figure_6_chart(cfg):
    """Alias to reuse the same chart logic for Figure 6."""
    return create_figure_4_chart(cfg)

if __name__ == "__main__":
    create_figure_6_chart(FIGURE_6_CONFIG)
    print('\n🚀 FIGURE 6 DONE!')
