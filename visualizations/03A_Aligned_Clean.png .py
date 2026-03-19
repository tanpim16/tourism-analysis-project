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
    # Setting tick label size (X-axis Ticks)
    'xtick.labelsize': 9,
    'ytick.labelsize': 9
})

COLORS = {
    'Major City': '#1B4F8A',
    'Secondary City': '#16A085',
    'Total Intent': '#E67E22'
}

BBOX_PROPS = dict(boxstyle="round,pad=0.4", fc="white", ec="#CCCCCC", alpha=0.9, lw=0.5)

# ─── 2. DATA UTILITIES ───────────────────────────────────────────────────────
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def prepare_data(path):
    df = pd.read_csv(path)
    df['total_search_intent'] = df['search_thai'] + df['search_foreign']
    if 'Year_CE' not in df.columns:
        df['Year_CE'] = df['Year'].astype(int) - 543
    df['date'] = pd.to_datetime(df['Year_CE'].astype(str) + '-' + df['Month'], format='%Y-%b')
    return df

# ─── 3. MAIN VISUALIZATION LOGIC ──────────────────────────────────────────────
def generate_lag_analysis_plot(df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'hspace': 0.35})
    
    configs = [
        (ax1, 'Major City', -1, COLORS['Major City']),
        (ax2, 'Secondary City', -2, COLORS['Secondary City'])
    ]

    for ax, city_type, lag, city_color in configs:
        df_city = df[df['City_type_EN'] == city_type].groupby('date').sum().reset_index()
        
        # Normalize & Align
        df_city['visitors_norm'] = normalize(df_city['total_visitors'])
        df_city['intent_aligned'] = normalize(df_city['total_search_intent']).shift(lag)

        # Plot Lines
        line1, = ax.plot(df_city['date'], df_city['visitors_norm'], color=city_color, lw=2.5, label=f'Actual Visitors ({city_type})')
        line2, = ax.plot(df_city['date'], df_city['intent_aligned'], color=COLORS['Total Intent'], lw=1.8, ls='--', label='Aligned Search Intent')
        
        # ─── Value Labels (6pt) ───
        # Adding labels to local peaks to keep it clean
        peaks = df_city[df_city['visitors_norm'] > 0.8]
        for i, row in peaks.iterrows():
            ax.text(row['date'], row['visitors_norm'] + 0.02, f"{row['visitors_norm']:.2f}", 
                    fontsize=6, ha='center', color=city_color)

        # ─── Titles & Labels (Specified Sizes) ───
        # Subplot Title: 12pt
        ax.set_title(f"{city_type}: Aligned Patterns (Lag: {abs(lag)} Month(s))", 
                     fontweight='bold', fontsize=12, loc='left', pad=40)
        
        # Y-axis Label: 10pt
        ax.set_ylabel("Normalized Scale (0-1)", fontsize=10, color='#666')
        
        # Legend Text: 9pt
        ax.legend(loc='lower left', bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, fontsize=9)
        
        ax.set_ylim(-0.05, 1.2)

    # Figure Title: 16pt
    fig.suptitle("Bridging the Gap: Digital Planning vs. Physical Footprints", 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.xlabel("Timeline (Adjusted for Planning Lead Time)", fontsize=10, labelpad=15)
    
    # Save the output
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "Figure_3A_Predictive_Lead-Time.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Figure generated with updated typography.")

if __name__ == "__main__":
    DATA_PATH = "data/processed/final_master_with_trends.csv"
    if os.path.exists(DATA_PATH):
        generate_lag_analysis_plot(prepare_data(DATA_PATH))