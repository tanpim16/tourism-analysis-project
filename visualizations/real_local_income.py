import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter
import matplotlib.patches as mpatches

# Import or define COLORS, FILL_ALPHA, moving_avg, fmt, df_plot as needed
# ...existing code...

FIGURE_4_CONFIG = {
    'col':      'real_revenue',
    'title':    'Real Local Income Generation',
    'subtitle': 'Real revenue  ·  Jan 2023 – Dec 2025',
    'ylabel':   'THB (Real)',
    'filename': 'Figure 4.png',
}

def create_figure_4_chart(cfg):
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

if __name__ == "__main__":
    create_figure_4_chart(FIGURE_4_CONFIG)
    print('\n🚀 FIGURE 4 DONE!')
