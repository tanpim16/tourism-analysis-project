import pandas as pd
import geopandas as gpd
import os

# --- SETTINGS ---
csv_path = 'data/processed/master_tourism_analysis.csv' 
geojson_path = 'data/raw/tha_admin1.geojson'

# --- 1. ตรวจสอบใน GEOJSON (มาตรฐาน) ---
print("🗺️ --- PROVINCE NAMES IN MAP (GeoJSON) ---")
gdf = gpd.read_file(geojson_path)
map_names = sorted(gdf['adm1_name'].unique().tolist())
print(f"Total: {len(map_names)} provinces found in map.")
print(map_names[:10], "... [and more]") # โชว์ 10 ตัวแรก

# --- 2. ตรวจสอบใน CSV (ข้อมูลของคุณ) ---
print("\n📊 --- PROVINCE NAMES IN YOUR CSV ---")
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    # หาคอลัมน์ที่เป็นข้อความ (เลี่ยง Year)
    text_cols = df.select_dtypes(include=['object', 'str']).columns.tolist()
    if text_cols:
        target_col = text_cols[0] 
        csv_names = sorted(df[target_col].astype(str).unique().tolist())
        print(f"Column used: '{target_col}'")
        print(f"Total: {len(csv_names)} unique names found in CSV.")
        print(csv_names[:10], "... [and more]")
    else:
        print("❌ No text columns found in CSV!")
else:
    print("❌ CSV File not found!")

# --- 3. หาจุดที่ไม่ตรงกัน (The Gap) ---
if 'csv_names' in locals():
    print("\n🧐 --- MISMATCH ANALYSIS ---")
    not_in_map = [name for name in csv_names if name not in map_names]
    if not_in_map:
        print(f"❌ {len(not_in_map)} names from CSV do NOT match the map.")
        print(f"Example mismatches: {not_in_map[:10]}")
    else:
        print("✅ All names in CSV match the map perfectly!")