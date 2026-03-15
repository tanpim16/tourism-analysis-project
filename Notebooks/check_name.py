import pandas as pd

# โหลดไฟล์
df = pd.read_csv('data/processed/final_master_with_trends.csv')

# หาแถวที่มีคำว่า "Ratchasima" หรือ "ราชสีมา"
korat_check = df[df.apply(lambda row: row.astype(str).str.contains('Ratchasima|ราชสีมา', case=False).any(), axis=1)]

print("--- ข้อมูลของนครราชสีมาที่หาเจอ ---")
if korat_check.empty:
    print("❌ ไม่พบข้อมูลนครราชสีมาเลยในไฟล์นี้!")
else:
    # โชว์คอลัมน์สำคัญ
    cols = [c for c in df.columns if any(k in c.lower() for k in ['prov', 'city', 'type'])]
    print(korat_check[cols].drop_duplicates())
    