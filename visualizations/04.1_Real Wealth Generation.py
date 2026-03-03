import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import FuncFormatter, LogLocator
import os

# --- 1. SETUP ---
csv_path = 'data/processed/master_tourism_analysis.csv'
geojson_path = 'data/raw/tha_admin1.geojson'
output_path = 'visualizations/Figure_4_Final_Classic_Clean.png'

# --- 2. LOAD & CLEAN ---
gdf = gpd.read_file(geojson_path)[['adm1_name', 'geometry']]
df_raw = pd.read_csv(csv_path)

# บังคับเติมข้อมูลที่หายไป (Fix Korat & Bangkok)
df_raw.loc[df_raw['ProvinceThai'] == 'นครราชสีมา', ['ProvinceEN', 'City_type_EN']] = ['Nakhon Ratchasima', 'Major City']
df_raw.loc[df_raw['ProvinceThai'] == 'กรุงเทพมหานคร', ['ProvinceEN', 'City_type_EN']] = ['Bangkok', 'Major City']

df_raw['ProvinceEN'] = df_raw['ProvinceEN'].astype(str).str.strip()
df_raw['City_type_EN'] = df_raw['City_type_EN'].astype(str).str.strip()

# รวมข้อมูลรายจังหวัด (Average Revenue)
df = df_raw.groupby('ProvinceEN').agg({'real_revenue': 'mean', 'City_type_EN': 'first'}).reset_index()
merged = gdf.merge(df, left_on='adm1_name', right_on='ProvinceEN', how='left')

# --- 3. PLOTTING ---
fig, ax = plt.subplots(figsize=(10, 14), facecolor='white')
ax.axis('off')

# 💡 เทคนิคสำคัญ: ดันก้นแผนที่ขึ้นเพื่อให้ Colorbar ด้านล่างไม่โดนเบียด
plt.subplots_adjust(bottom=0.18) 

# พื้นหลังสีเทาอ่อน
gdf.plot(ax=ax, color='#f8f9fa', edgecolor='#dee2e6', linewidth=0.5)

# ตั้งค่า Scale ให้ถึงแสนล้าน (100,000)
vmin, vmax = 100, 200000 
norm = colors.LogNorm(vmin=vmin, vmax=vmax)

def comma_fmt(x, pos): return f'{int(x):,}'

# 🔵 Major City (Blue) | 🟢 Secondary City (Green)
major = merged[merged['City_type_EN'].str.contains('Major', case=False, na=False)]
if not major.empty:
    major.plot(column='real_revenue', ax=ax, cmap='Blues', norm=norm, edgecolor='white', linewidth=0.3)

secondary = merged[merged['City_type_EN'].str.contains('Secon', case=False, na=False)]
if not secondary.empty:
    secondary.plot(column='real_revenue', ax=ax, cmap='Greens', norm=norm, edgecolor='white', linewidth=0.3)

# --- 4. COLORBARS (ปรับตำแหน่งใหม่ให้สูงขึ้น) ---
# เมืองหลัก - ขยับ Y ขึ้นเป็น 0.12 (เดิม 0.08) เพื่อให้ Label ไม่หลุดขอบ
cax1 = fig.add_axes([0.15, 0.12, 0.3, 0.015])
cb1 = fig.colorbar(plt.cm.ScalarMappable(cmap='Blues', norm=norm), cax=cax1, orientation='horizontal')
cb1.ax.xaxis.set_major_formatter(FuncFormatter(comma_fmt))
cb1.ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0,)))
# เพิ่ม labelpad เพื่อเว้นระยะห่างให้สวยงาม
cb1.set_label('Major City Revenue (Million Baht)', fontsize=11, fontweight='bold', labelpad=10)

# เมืองรอง - ขยับ Y ขึ้นเป็น 0.12
cax2 = fig.add_axes([0.55, 0.12, 0.3, 0.015])
cb2 = fig.colorbar(plt.cm.ScalarMappable(cmap='Greens', norm=norm), cax=cax2, orientation='horizontal')
cb2.ax.xaxis.set_major_formatter(FuncFormatter(comma_fmt))
cb2.ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0,)))
cb2.set_label('Secondary City Revenue (Million Baht)', fontsize=11, fontweight='bold', labelpad=10)

# หัวข้อและชื่อกราฟย่อย
plt.suptitle('Thailand Tourism Wealth Distribution', fontsize=22, fontweight='bold', y=0.96)
ax.set_title('Strategic Map: Comparison of Major and Secondary Cities', fontsize=14, color='#666666', pad=10)

# ตอน Save ใส่ pad_inches เพิ่มอีกนิดเพื่อให้ชัวร์ว่าไม่โดนตัด
plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.3)
print(f"🎉 แผนที่ฉบับ Perfect Layout บันทึกแล้วที่: {output_path}")