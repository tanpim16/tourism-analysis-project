import pandas as pd

df = pd.read_csv('data/processed/master_tourism_analysis.csv')

# กรองเฉพาะแถวที่เป็นนครราชสีมา
korat_raw = df[df['ProvinceThai'] == 'นครราชสีมา']

print("--- ตรวจสอบข้อมูลดิบ: นครราชสีมา ---")
if not korat_raw.empty:
    # โชว์ 5 แถวแรกและคอลัมน์ที่จำเป็น
    print(korat_raw[['ProvinceThai', 'ProvinceEN', 'City_type_EN', 'real_revenue']].head())
    print(f"\nTotal rows for Korat: {len(korat_raw)}")
    print(f"Is City_type_EN missing?: {korat_raw['City_type_EN'].isnull().any()}")
else:
    print("❌ ไม่พบข้อมูลนครราชสีมาเลยในไฟล์นี้")