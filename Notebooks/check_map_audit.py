import pandas as pd
import geopandas as gpd

# --- SETUP ---
csv_path = 'data/processed/master_tourism_analysis.csv'
geojson_path = 'data/raw/tha_admin1.geojson'

# LOAD
gdf = gpd.read_file(geojson_path)
df = pd.read_csv(csv_path)

# MERGE (ใช้ Logic เดียวกับไฟล์วาดรูปหลัก)
df['clean_province'] = df['ProvinceEN'].astype(str).str.strip()
merged = gdf.merge(df, left_on='adm1_name', right_on='clean_province', how='left')

# ค้นหาตัวที่ยังไม่มีค่า real_revenue (ที่เป็นสีเทา)
gray_list = merged[merged['real_revenue'].isna()]['adm1_name'].tolist()

print(f"🕵️‍♂️ ยังเหลือจังหวัดสีเทาอีก {len(gray_list)} จังหวัด:")
for i, name in enumerate(sorted(gray_list), 1):
    print(f"{i}. {name}")