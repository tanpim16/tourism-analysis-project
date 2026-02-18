import pandas as pd
import os

def process_cpi_file(input_path, output_path):
    # 1. อ่านไฟล์ CSV
    df = pd.read_csv(input_path, skiprows=4, encoding='utf-8-sig')
    df = df.dropna(axis=1, how='all')
    
    # 2. Melt ข้อมูล
    df_melted = df.melt(id_vars=['จังหวัด'], var_name='Period', value_name='Price_Index')
    
    # 3. แยก "ม.ค. 2566" ออกเป็น "เดือน" และ "ปี"
    df_melted[['เดือน', 'ปี']] = df_melted['Period'].str.split(' ', expand=True)
    
    # 4. แปลงชื่อเดือนจากไทยเป็นอังกฤษ
    month_map = {
        'ม.ค.': 'Jan',
        'ก.พ.': 'Feb',
        'มี.ค.': 'Mar',
        'เม.ย.': 'Apr',
        'พ.ค.': 'May',
        'มิ.ย.': 'Jun',
        'ก.ค.': 'Jul',
        'ส.ค.': 'Aug',
        'ก.ย.': 'Sep',
        'ต.ค.': 'Oct',
        'พ.ย.': 'Nov',
        'ธ.ค.': 'Dec'
    }
    
    # ใช้ .map() เพื่อเปลี่ยนค่าในคอลัมน์ 'เดือน'
    df_melted['เดือน'] = df_melted['เดือน'].map(month_map)
    
    # 5. จัดเรียงคอลัมน์
    df_final = df_melted[['จังหวัด', 'เดือน', 'ปี', 'Price_Index']]
    
    # 6. ลบแถวที่ไม่มีข้อมูล
    df_final = df_final.dropna(subset=['Price_Index'])
    
    # 7. บันทึกไฟล์
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ ประมวลผลเสร็จสิ้น (เปลี่ยนเป็นชื่อเดือนภาษาอังกฤษแล้ว): {output_path}")
    return df_final

if __name__ == "__main__":
    # ตรวจสอบว่า path ถูกต้องตามโครงสร้างโฟลเดอร์ของคุณ
    input_file = 'ImportData/CPI Data/CPIP_2566_2568.csv' 
    output_file = 'data/processed/Cleaned_CPI_Data.csv'
    
    # ตรวจสอบก่อนว่ามีไฟล์อยู่จริงไหมเพื่อป้องกัน Error
    if os.path.exists(input_file):
        process_cpi_file(input_file, output_file)
    else:
        print(f"❌ ไม่พบไฟล์ที่: {input_file}")
        print("กรุณาตรวจสอบชื่อโฟลเดอร์ 'CPI Data' ว่าเว้นวรรคถูกต้องหรือไม่")