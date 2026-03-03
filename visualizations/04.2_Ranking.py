import pandas as pd
import matplotlib.pyplot as plt
import os

# --- 1. LOAD & ANALYZE DATA ---
csv_path = 'data/processed/master_tourism_analysis.csv'
df_raw = pd.read_csv(csv_path)

# 🧹 Data Recovery (กู้ข้อมูลที่ nan กลับมา)
df_raw.loc[df_raw['ProvinceThai'] == 'นครราชสีมา', ['ProvinceEN', 'City_type_EN']] = ['Nakhon Ratchasima', 'Major City']
df_raw.loc[df_raw['ProvinceThai'] == 'กรุงเทพมหานคร', ['ProvinceEN', 'City_type_EN']] = ['Bangkok', 'Major City']
df_raw['ProvinceEN'] = df_raw['ProvinceEN'].astype(str).str.strip()
df_raw['City_type_EN'] = df_raw['City_type_EN'].astype(str).str.strip()

# 📈 Calculation
df_analyzed = df_raw.groupby('ProvinceEN').agg({'real_revenue': 'mean', 'City_type_EN': 'first'}).reset_index()

# 🏆 Ranking Logic
def get_top5(city_type):
    target_df = df_analyzed[df_analyzed['City_type_EN'].str.contains(city_type, case=False, na=False)]
    top5 = target_df.nlargest(5, 'real_revenue').copy()
    top5['Rank'] = range(1, 6)
    top5['Revenue'] = top5['real_revenue'].apply(lambda x: f"{int(x):,} M.Baht")
    return top5[['Rank', 'ProvinceEN', 'Revenue']]

df_major_final = get_top5('Major')
df_secon_final = get_top5('Secon')

# --- 2. VISUALIZATION (ปรับพื้นที่ให้กระชับ) ---
# บีบ figsize จาก (15, 5) เหลือ (15, 4) เพื่อลดพื้นที่ว่างด้านบน-ล่าง
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 4), facecolor='white')
ax1.axis('off')
ax2.axis('off')

def draw_table(ax, df, header_color, title, city_col_name):
    widths = [0.12, 0.48, 0.4]
    df.columns = ['Rank', city_col_name, 'Average Revenue']
    
    table = ax.table(cellText=df.values, 
                     colLabels=df.columns, 
                     colWidths=widths,
                     loc='center', 
                     cellLoc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0) # ลด scale ความสูงลงเล็กน้อย
    
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#dee2e6')
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor(header_color)
        elif row % 2 == 0:
            cell.set_facecolor('#f8f9fa')
            
    # 💡 ปรับ pad=10 เพื่อดึงชื่อตารางลงมาใกล้ตัวตารางมากขึ้น
    ax.set_title(title, fontsize=16, fontweight='bold', pad=10)

# วาดตาราง
draw_table(ax1, df_major_final, '#1a5276', 'Major City: Top 5 Revenue', 'Major Province')
draw_table(ax2, df_secon_final, '#1e8449', 'Secondary City: Top 5 Revenue', 'Secondary Province')

# --- 3. SAVE ---
# ใช้ pad_inches=0.05 เพื่อบีบขอบขาวรอบภาพให้เหลือน้อยที่สุด
plt.tight_layout()
output_path = 'visualizations/Figure_5_Ranking_Tight.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
print(f"🎉 ตารางฉบับกระชับพิเศษ (ลดสเปซว่าง) สร้างเสร็จแล้วที่: {output_path}")