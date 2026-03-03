import pandas as pd
import os

# --- 1. SETUP ---
csv_path = 'data/processed/master_tourism_analysis.csv'

# --- 2. DICTIONARY สำหรับแก้ชื่อ (Map จากชื่อเดิมใน CSV -> ชื่อที่แผนที่ต้องการ) ---
# ผมอ้างอิงรายชื่อจากที่ Terminal คุณแจ้งมาเลยครับ
correction_map = {
    'Chainat': 'Chai Nat',
    'Chonburi': 'Chon Buri',
    'Lopburi': 'Lop Buri',
    'Korat': 'Nakhon Ratchasima',
    'Nakhon Ratchasima (Korat)': 'Nakhon Ratchasima',
    'Nong Bua Lamphu': 'Nong Bua Lam Phu',
    'Phang Nga': 'Phangnga',
    'Prachinburi': 'Prachin Buri',
    'Sisaket': 'Si Sa Ket',
    'Singburi': 'Sing Buri',
    'Suphanburi': 'Suphan Buri',
    'Nakhonratchasima': 'Nakhon Ratchasima',
    'Korat': 'Nakhon Ratchasima',
    'Nakhon Ratchasima (Korat)': 'Nakhon Ratchasima',
    'Sisaket': 'Si Sa Ket',
    'Srisaket': 'Si Sa Ket',
    'Si Saket': 'Si Sa Ket'
}

# --- 3. EXECUTE FIX ---
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    
    # แก้ไขชื่อในคอลัมน์ ProvinceEN
    # .replace() จะเปลี่ยนเฉพาะตัวที่ตรงกับ Key ใน Dictionary ของเราครับ
    df['ProvinceEN'] = df['ProvinceEN'].replace(correction_map)
    
    # บันทึกทับไฟล์เดิม (หรือเปลี่ยนชื่อไฟล์ถ้าอยากเก็บ Backup)
    df.to_csv(csv_path, index=False)
    print("✅ แก้ไขชื่อจังหวัดทั้ง 10 จังหวัดเรียบร้อยแล้ว!")
else:
    print("❌ ไม่พบไฟล์ CSV")