import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

sns.set_theme(style="white", rc={"axes.grid": True, "grid.alpha": 0.2, "grid.linestyle": "--"})
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'

data_path = 'data/processed/master_tourism_analysis.csv'
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    df['Year_CE'] = df['Year'].astype(int) - 543
    df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')
    df_plot = df.groupby(['date', 'City_type_EN'])[['total_visitors', 'total_revenue', 'real_revenue']].sum().reset_index()
    df_plot = df_plot[(df_plot['date'] >= '2023-01-01') & (df_plot['date'] <= '2025-12-01')].sort_values('date')
else:
    print("❌ ไม่พบไฟล์ข้อมูล"); exit()

os.makedirs('visualizations', exist_ok=True)
my_palette = {'Major City': '#2C3E50', 'Secondary City': '#16A085'}

def fmt(x):
    if x >= 1e9: return f'{x/1e9:.1f}B'
    elif x >= 1e6: return f'{x/1e6:.1f}M'
    return f'{x:,.0f}'

def create_clean_chart(y_col, title, subtitle, ylabel, filename):
    fig, ax = plt.subplots(figsize=(15, 7.5))

    sns.lineplot(data=df_plot, x='date', y=y_col, hue='City_type_EN',
                 palette=my_palette, linewidth=3, marker='o',
                 markersize=6, ax=ax, legend=False)

    for line_name, color in my_palette.items():
        subset = df_plot[df_plot['City_type_EN'] == line_name].sort_values('date')
        first, last = subset.iloc[0], subset.iloc[-1]

        # ✅ First label พร้อม background box
        ax.annotate(fmt(first[y_col]), xy=(first['date'], first[y_col]),
                    xytext=(0, 14), textcoords='offset points',
                    ha='center', fontsize=9, color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=color, alpha=0.85, lw=0.8))

        # ✅ End label ใส่กรอบแบบเดียวกับตอนเริ่มต้น และเอา Growth ออก
        ax.annotate(f'{line_name}\n{fmt(last[y_col])}',
                    xy=(last['date'], last[y_col]),
                    xytext=(15, 0), textcoords='offset points',
                    color=color, fontweight='bold', fontsize=10, va='center',
                    bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=color, alpha=0.85, lw=0.8))

    # Ticks สม่ำเสมอ ทุก Q ตั้งแต่ Jan 2023 ถึง Jan 2026
    ticks = pd.date_range(start='2023-01-01', end='2026-01-01', freq='QS-JAN')
    ax.set_xticks(ticks)
    ax.set_xticklabels([d.strftime('%b\n%Y') for d in ticks])

    ax.set_xlim(pd.Timestamp('2022-12-15'), pd.Timestamp('2026-03-01'))
    ax.spines['bottom'].set_bounds(mdates.date2num(pd.Timestamp('2023-01-01')),
                                   mdates.date2num(pd.Timestamp('2025-12-01')))

    # top=1.2 แทน 1.3 เส้นไม่แบนเกิน
    ax.set_ylim(bottom=0, top=df_plot[y_col].max() * 1.2)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: fmt(x)))

    # Minor grid รายเดือน
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.grid(which='minor', axis='x', alpha=0.05, linestyle=':')

    # แกน Y กลับมา (left=False)
    sns.despine(left=False, bottom=False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors='#555555', which='both')
    ax.tick_params(axis='x', which='major', labelsize=11, pad=5)

    fig.text(0.01, 0.97, title, fontsize=18, fontweight='bold', color='#2C3E50', va='top')
    fig.text(0.01, 0.92, subtitle, fontsize=11, color='#888888', va='top')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold', color='#555555', labelpad=15)
    ax.set_xlabel('')

    plt.subplots_adjust(right=0.88)
    for text in ax.texts: text.set_clip_on(False)
    plt.savefig(f'visualizations/{filename}', dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f'✅ {filename}')

create_clean_chart('total_visitors', 'Figure 1A: Monthly Tourist Arrivals (2023–2025)', 'Major City vs Secondary City', 'Arrivals (People)', 'figure_1A.png')
create_clean_chart('total_revenue',  'Figure 1B: Monthly Tourism Income — Nominal (2023–2025)', 'Major City vs Secondary City', 'Income (THB)', 'figure_1B.png')
create_clean_chart('real_revenue',   'Figure 1C: Real Local Income Generation (2023–2025)', 'CPI-adjusted revenue', 'Real Revenue (THB)', 'figure_1C.png')

print("🚀 DONE!")