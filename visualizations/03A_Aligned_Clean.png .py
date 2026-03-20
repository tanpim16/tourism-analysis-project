import pandas as pd
import matplotlib.pyplot as plt
import os

# ─── 1. GLOBAL CONFIGURATION & STYLE ──────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA',
    'axes.grid': True,
    'grid.color': '#FFFFFF',
    'grid.linewidth': 1.2,
    'font.family': 'sans-serif',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9
})

COLORS = {
    'Major City': '#1B4F8A',
    'Secondary City': '#16A085',
    'Total Intent': '#E67E22'
}

# ─── 2. DATA UTILITIES ───────────────────────────────────────────────────────
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def prepare_data(path):
    # กรณีรันเดโมถ้าไม่มีไฟล์จริง
    if not os.path.exists(path):
        dates = pd.date_range(start='2023-01-01', periods=24, freq='MS')
        np.random.seed(42) # เพื่อผลลัพธ์ที่เหมือนเดิม
        data = {
            'date': dates,
            'City_type_EN': ['Major City']*24 + ['Secondary City']*24,
            'total_visitors': np.random.randint(1000, 5000, 48),
            'total_search_intent': np.random.randint(500, 2000, 48)
        }
        return pd.DataFrame(data)
    
    df = pd.read_csv(path)
    # จัดการค่าว่างก่อนรวม
    df['search_thai'] = df['search_thai'].fillna(0)
    df['search_foreign'] = df['search_foreign'].fillna(0)
    df['total_search_intent'] = df['search_thai'] + df['search_foreign']
    
    if 'Year_CE' not in df.columns:
        df['Year_CE'] = df['Year'].astype(int) - 543
    df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')
    return df

# ─── 3. MAIN VISUALIZATION LOGIC ──────────────────────────────────────────────
def generate_lag_analysis_plot(df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    
    configs = [
        (ax1, 'Major City', -1, COLORS['Major City']),
        (ax2, 'Secondary City', -2, COLORS['Secondary City'])
    ]

    for i, (ax, city_type, lag, city_color) in enumerate(configs):
        # ตรวจสอบการสะกดให้ตรงกับดาต้า
        df_city = df[df['City_type_EN'] == city_type].groupby('date').sum().reset_index()
        
        # Normalize & Align
        df_city['visitors_norm'] = normalize(df_city['total_visitors'])
        df_city['intent_aligned'] = normalize(df_city['total_search_intent']).shift(lag)

        # Plot Lines
        ax.plot(df_city['date'], df_city['visitors_norm'], color=city_color, lw=2.5, label=f'Actual Visitors ({city_type})')
        ax.plot(df_city['date'], df_city['intent_aligned'], color=COLORS['Total Intent'], lw=1.8, ls='--', label='Aligned Search Intent')
        
        # Labels on peaks
        peaks = df_city[df_city['visitors_norm'] > 0.85]
        for _, row in peaks.iterrows():
            ax.text(row['date'], row['visitors_norm'] + 0.03, f"{row['visitors_norm']:.2f}", 
                    fontsize=7, ha='center', color=city_color, fontweight='bold')

        # --- แก้ไข Layout ตามโจทย์ตรงนี้ ---
        # 1. รักษาตำแหน่งชื่อ Major City ที่เอาลงมา (i=0 -> pad=10)
        title_pad = 10 if i == 0 else 25
        ax.set_title(f"{city_type}: Aligned Patterns (Lag: {abs(lag)} Month(s))", 
                    fontweight='bold', fontsize=12, loc='left', pad=title_pad)
        
        ax.set_ylabel("Normalized Scale (0-1)", fontsize=10, color='#666')
        
        # 2. บังคับให้ Legend อยู่ซ้ายหมด (upper left) เหมือนกันทั้งคู่
        ax.legend(loc='upper left', frameon=True, framealpha=0.8, fontsize=8, ncol=1)
        
        # 3. ขยับเพดาน Y ขึ้นเล็กน้อย (1.3 -> 1.35) เพื่อเว้นพื้นที่ให้ Title + Legend ในกราฟบน
        ax.set_ylim(-0.05, 1.35) 

    # ปรับระยะห่างระหว่าง Subplots
    plt.subplots_adjust(hspace=0.4, top=0.88)

    # Figure Title
    fig.suptitle("Bridging the Gap: Digital Planning vs. Physical Footprints", 
                 fontsize=16, fontweight='bold', y=0.96)
    
    plt.xlabel("Timeline (Adjusted for Planning Lead Time)", fontsize=10, labelpad=10)
    
    # Save output
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "Figure_3A_Predictive_Lead-Time.png"), dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Figure generated: Consistency updated (Both Legends Left).")

if __name__ == "__main__":
    DATA_PATH = "data/processed/final_master_with_trends.csv"
    df_data = prepare_data(DATA_PATH)
    generate_lag_analysis_plot(df_data)