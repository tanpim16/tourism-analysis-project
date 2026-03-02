import pandas as pd
import matplotlib.pyplot as plt
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
})

COLORS = {
    'Major City': '#1B4F8A',
    'Secondary City': '#16A085',
    'Total Intent': '#E67E22'
}

# ─── Load & Data Prep ────────────────────────────────────────────────────────
data_path = "data/processed/final_master_with_trends.csv"
df = pd.read_csv(data_path)
df['total_search_intent'] = df['search_thai'] + df['search_foreign']

if 'Year_CE' not in df.columns:
    df['Year_CE'] = df['Year'].astype(int) - 543
df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

# ─── Visualization (Lag-Aligned & Clean Layout) ───
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 14), sharex=True, gridspec_kw={'hspace': 0.3})
bbox_props = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9, lw=0.5)

# รายละเอียดการเลื่อนเวลา (Lag Adjustment)
configs = [
    (ax1, 'Major City', -1, COLORS['Major City']),
    (ax2, 'Secondary City', -2, COLORS['Secondary City'])
]

for ax, city_type, lag, city_color in configs:
    df_city = df[df['City_type_EN'] == city_type].groupby('date').sum().reset_index()
    
    # Normalize & Align
    df_city['visitors_norm'] = normalize(df_city['total_visitors'])
    df_city['intent_aligned'] = normalize(df_city['total_search_intent']).shift(lag)

    # Plot
    ax.plot(df_city['date'], df_city['visitors_norm'], color=city_color, lw=3, label=f'Actual Visitors ({city_type})')
    ax.plot(df_city['date'], df_city['intent_aligned'], color=COLORS['Total Intent'], lw=2, ls='--', label='Aligned Search Intent')
    
    # ─── Fix Legend: ย้ายไปวางข้างบน ───
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, fontsize=11)
    
    # ─── Fix Title & Annotation: เพิ่มระยะห่างไม่ให้ทับ ───
    ax.set_title(f"{city_type}: Aligned Patterns (Lag: {abs(lag)} Month(s))", 
                 fontweight='bold', fontsize=18, loc='left', pad=45)
    
    # ย้าย Annotation ไปไว้มุมขวาเพื่อเลี่ยงการทับเส้นกราฟในช่วงต้น
    ax.text(0.98, 0.92, f"Conversion Analysis: {city_type}", transform=ax.transAxes, 
            fontweight='bold', color='#666', ha='right', bbox=bbox_props)

    ax.set_ylabel("Normalized Scale (0-1)", color='#666')
    ax.set_ylim(-0.05, 1.15)

plt.xlabel("Timeline (Adjusted for Planning Lead Time)", fontsize=12, labelpad=15)
fig.suptitle("Bridging the Gap: Digital Planning vs. Physical Footprints", fontsize=24, fontweight='bold', y=0.98)

os.makedirs('visualizations', exist_ok=True)
plt.savefig("visualizations/Figure 4_Lag_Aligned_Clean.png", dpi=300, bbox_inches='tight')
plt.close()

print("✅ Figure 4 (Clean Layout) created successfully!")