import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# --- 1. SETUP PATHS ---
output_path = 'visualizations/Figure_4_Choropleth_Map_EN.png'
geojson_path = 'data/raw/tha_admin1.geojson' #
csv_path = 'data/processed/master_tourism_data.csv'

os.makedirs('visualizations', exist_ok=True)

# --- 2. LOAD & OPTIMIZE GEODATA ---
print("🌐 Loading 96MB GeoJSON file...")
thailand_provinces = gpd.read_file(geojson_path)
print("🧹 Simplifying geometry for better performance...")
thailand_provinces['geometry'] = thailand_provinces.simplify(0.005) #

# --- 3. LOAD TOURISM DATA ---
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"✅ CSV Loaded: {len(df)} records.")
    
    # ตรวจสอบว่าในไฟล์ CSV ของคุณมีคอลัมน์ชื่ออะไรบ้างที่น่าจะเป็นชื่อจังหวัด
    possible_cols = ['Province', 'ProvinceTH', 'จังหวัด', 'province', 'Province_TH']
    thai_column_in_csv = next((col for col in possible_cols if col in df.columns), df.columns[0])
    print(f"🔎 Auto-detected province column in CSV: '{thai_column_in_csv}'")
else:
    print("⚠️ CSV not found at data/processed/! Using dummy Thai data for preview...")
    # สร้างข้อมูลสมมติที่ชื่อคอลัมน์ตรงกับตัวแปรที่จะใช้ merge
    thai_column_in_csv = 'Province'
    df = pd.DataFrame({
        thai_column_in_csv: ['กรุงเทพมหานคร', 'เชียงใหม่', 'ภูเก็ต', 'ชลบุรี', 'สุราษฎร์ธานี', 'กระบี่', 'แม่ฮ่องสอน'],
        'real_revenue': [5000000, 2000000, 3500000, 2800000, 1800000, 1500000, 800000]
    })

# --- 4. MERGE DATA (Joining by Thai Names) ---
# ในไฟล์ HDX: 'adm1_name' คือชื่อไทย, 'adm1_name1' คือชื่ออังกฤษ
print(f"🔗 Joining GeoJSON ('adm1_name') with CSV ('{thai_column_in_csv}')...")

try:
    merged = thailand_provinces.merge(df, left_on='adm1_name', right_on=thai_column_in_csv, how='left')
except KeyError as e:
    print(f"❌ Merge Failed: Could not find column {e} in your data.")
    print(f"Available columns in CSV: {df.columns.tolist()}")
    exit()

# --- 5. PLOTTING THE MAP ---
fig, ax = plt.subplots(figsize=(10, 15), facecolor='#ffffff')

# Background: All provinces in light gray
thailand_provinces.plot(ax=ax, color='#f2f2f2', edgecolor='#d9d9d9', linewidth=0.5)

# Choropleth Layer: Color by revenue
# ใช้สีแดง-เหลือง (OrRd) เพื่อให้เห็นความต่างชัดเจน
merged.plot(column='real_revenue', 
            ax=ax, 
            cmap='OrRd', 
            legend=True,
            legend_kwds={
                'label': "Tourism Revenue (Real Wealth Scale)", 
                'orientation': "horizontal", 
                'pad': 0.02,
                'shrink': 0.8
            })

# Labels: Showing Top 12 Wealthiest (Using English names from GeoJSON)
# เรากรองเฉพาะแถวที่มีรายได้ (revenue) และหาค่ามากที่สุด 12 อันดับ
top_labels = merged.dropna(subset=['real_revenue']).nlargest(12, 'real_revenue')

for _, row in top_labels.iterrows():
    centroid = row.geometry.centroid
    # 'adm1_name1' คือชื่อจังหวัดภาษาอังกฤษในไฟล์ GeoJSON
    ax.annotate(text=row['adm1_name1'], 
                xy=(centroid.x, centroid.y), 
                ha='center', fontsize=9, fontweight='bold', color='#2c3e50',
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7, ec='none'))

# Final decorations (English as requested)
ax.set_title('Thailand Tourism Real Wealth Distribution Map\n(Data Integrated by Thai Province Names)', 
             fontsize=18, fontweight='bold', pad=25)
ax.axis('off')

# --- 6. SAVE ---
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"🎉 SUCCESS! Map has been saved to: {output_path}")