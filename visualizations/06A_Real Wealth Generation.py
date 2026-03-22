import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import FuncFormatter, LogLocator
import os

# ─── 1. STYLE & SETUP ────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  '#FFFFFF',
    'axes.facecolor':    '#FFFFFF',
    'font.family':       'sans-serif',
    'text.color':        '#111827', 
})

csv_path = 'data/processed/master_tourism_analysis.csv'
geojson_path = 'data/raw/tha_admin1.geojson'
output_path = 'visualizations/Figure_6A_map.png'

os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ─── 2. DATA PROCESSING ──────────────────────────────────────────────────────
if os.path.exists(geojson_path) and os.path.exists(csv_path):
    gdf = gpd.read_file(geojson_path)[['adm1_name', 'geometry']]
    df_raw = pd.read_csv(csv_path)

    df_raw.loc[df_raw['ProvinceThai'] == 'นครราชสีมา', ['ProvinceEN', 'City_type_EN']] = ['Nakhon Ratchasima', 'Major City']
    df_raw.loc[df_raw['ProvinceThai'] == 'กรุงเทพมหานคร', ['ProvinceEN', 'City_type_EN']] = ['Bangkok', 'Major City']

    df = df_raw.groupby('ProvinceEN').agg({'real_revenue': 'mean', 'City_type_EN': 'first'}).reset_index()
    merged = gdf.merge(df, left_on='adm1_name', right_on='ProvinceEN', how='left')

    # ─── 3. PLOTTING (Compact Layout) ────────────────────────────────────────
    # 📌 ลดความสูงจาก 8.5 เป็น 8.0 เพื่อลดพื้นที่ว่าง
    fig, ax = plt.subplots(figsize=(6, 7), dpi=150, facecolor='#FFFFFF')
    ax.axis('off')

    # 📌 ปรับ bottom ลงมาเพื่อยืดแผนที่ลงด้านล่างให้สุด
    plt.subplots_adjust(left=0.02, right=0.98, top=0.78, bottom=0.12)

    # วาดพื้นหลังเผื่อจังหวัดที่ไม่มีข้อมูล
    gdf.plot(ax=ax, color='#F8FAFC', edgecolor='#CBD5E1', linewidth=0.5)

    vmin, vmax = 100, 200000 
    norm = colors.LogNorm(vmin=vmin, vmax=vmax)
    def comma_fmt(x, pos): return f'{int(x):,}'

    border_color = '#CBD5E1'
    border_width = 0.5

    major = merged[merged['City_type_EN'].str.contains('Major', case=False, na=False)]
    if not major.empty:
        major.plot(column='real_revenue', ax=ax, cmap='Blues', norm=norm, 
                   edgecolor=border_color, linewidth=border_width)

    secondary = merged[merged['City_type_EN'].str.contains('Secon', case=False, na=False)]
    if not secondary.empty:
        secondary.plot(column='real_revenue', ax=ax, cmap='Greens', norm=norm, 
                       edgecolor=border_color, linewidth=border_width)

    # ─── 4. STRICT TYPOGRAPHY (ตามสเปก) ────────────────────────────────────────

    # 📌 Figure Title (suptitle) → fontsize=16, fontweight='bold', y=0.87
    plt.suptitle('Thailand Tourism Wealth Distribution', 
                 fontsize=14, fontweight='bold', color='#111827', y=0.87)

    # 📌 Subplot Title → fontsize=12, fontweight='bold'
    ax.set_title('Strategic Map: Comparison of Major and Secondary Cities', 
                 fontsize=10, color='#6B7280', pad=15)

    # ─── 5. COLORBARS & TICKS ────────────────────────────────────────────────
    
    # 📌 ขยับ Y ของ Colorbar ลงมาที่ 0.06 เพื่อให้ชิดขอบล่างมากขึ้น ไม่เหลือที่ว่าง
    
    # 🔵 Major City Colorbar
    cax1 = fig.add_axes([0.15, 0.06, 0.32, 0.012]) 
    cb1 = fig.colorbar(plt.cm.ScalarMappable(cmap='Blues', norm=norm), 
                       cax=cax1, orientation='horizontal')
    cb1.ax.xaxis.set_major_formatter(FuncFormatter(comma_fmt))
    cb1.ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0,)))
    
    # 📌 X-axis Ticks / Legend Text → fontsize=9
    cb1.ax.tick_params(labelsize=9, color='#9CA3AF', labelcolor='#4B5563', length=4) 
    cb1.ax.minorticks_off() 
    cb1.outline.set_visible(False)
    
    # 📌 Legend Title / Y-axis Label → fontsize=10, fontweight='normal'
    cb1.set_label('Major City (M. Baht)', fontsize=10, fontweight='normal', color='#1E3A8A', labelpad=8)


    # 🟢 Secondary City Colorbar
    cax2 = fig.add_axes([0.53, 0.06, 0.32, 0.012])
    cb2 = fig.colorbar(plt.cm.ScalarMappable(cmap='Greens', norm=norm), 
                       cax=cax2, orientation='horizontal')
    cb2.ax.xaxis.set_major_formatter(FuncFormatter(comma_fmt))
    cb2.ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0,)))
    
    # 📌 X-axis Ticks / Legend Text → fontsize=9
    cb2.ax.tick_params(labelsize=9, color='#9CA3AF', labelcolor='#4B5563', length=4)
    cb2.ax.minorticks_off() 
    cb2.outline.set_visible(False)
    
    # 📌 Legend Title / Y-axis Label → fontsize=10, fontweight='normal'
    cb2.set_label('Secondary City (M. Baht)', fontsize=10, fontweight='normal', color='#065F46', labelpad=8)

    # ─── 6. FINISH ────────────────────────────────────────────────────────────
    # 📌 Value Labels → fontsize=6, fontweight='bold' (Commented out if not needed)
    # for idx, row in major.nlargest(3, 'real_revenue').iterrows():
    #     ax.annotate(text=row['ProvinceEN'], xy=(row.geometry.centroid.x, row.geometry.centroid.y),
    #                 fontsize=6, fontweight='bold', ha='center', color='black')

    plt.savefig(output_path, dpi=200, bbox_inches='tight', pad_inches=0.1) # ลด pad_inches ลงเหลือ 0.1
    plt.show()
    print(f"✨ บันทึกแผนที่ฉบับ Clean Layout เรียบร้อย: {output_path}")

else:
    print("❌ Error: ไม่พบไฟล์ Data หรือ GeoJSON โปรดตรวจสอบ Path")