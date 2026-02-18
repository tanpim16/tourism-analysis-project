import pandas as pd
import glob
import re
import os
import unicodedata

def normalize_thai(text):
    """ ปรับรหัสตัวอักษรไทยให้เป็นมาตรฐาน เพื่อให้เทียบคำง่ายขึ้น """
    return unicodedata.normalize('NFC', str(text))

def clean_tourism_data(input_dir, output_dir):
    # ค้นหาไฟล์ .xlsx และ .csv
    search_path_xlsx = os.path.join(input_dir, "**/*.xlsx")
    search_path_csv = os.path.join(input_dir, "**/*.csv")
    file_list = glob.glob(search_path_xlsx, recursive=True) + glob.glob(search_path_csv, recursive=True)
    
    # กรองไฟล์ที่ไม่เกี่ยวข้องออก
    monthly_files = [f for f in file_list if 'สะสม' not in f and 'ผ่านกำกับ' not in f and '~$' not in f]
    
    # ดิกชันนารีสำหรับแปลงชื่อเดือน (เน้นคำสำคัญที่มักเจอในชื่อชีท)
    month_lookup = [
        ('Jan', ['มกรา', 'ม.ค']), ('Feb', ['กุมภา', 'ก.พ']), ('Mar', ['มีนา', 'มี.ค']),
        ('Apr', ['เมษา', 'เม.ย']), ('May', ['พฤษภา', 'พ.ค']), ('Jun', ['มิถุนา', 'มิ.ย']),
        ('Jul', ['กรกฎา', 'ก.ค']), ('Aug', ['สิงหา', 'ส.ค']), ('Sep', ['กันยา', 'ก.ย']),
        ('Oct', ['ตุลา', 'ต.ค']), ('Nov', ['พฤศจิกา', 'พ.ย']), ('Dec', ['ธันวา', 'ธ.ค'])
    ]

    final_data = []
    print(f"--- Starting Process (All Sheets Mode) ---")

    for file_path in monthly_files:
        file_name = normalize_thai(os.path.basename(file_path))
        print(f"📦 Opening File: {file_name}")
        
        try:
            sheets_to_process = []
            
            if file_path.endswith('.xlsx'):
                # 🛠️ อ่านทุก Sheet (13 ชีท)
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    normalized_sheet = normalize_thai(sheet_name)
                    
                    # 🚫 ข้ามชีทสรุปยอดสะสม หรือชีทที่ไม่ใช่รายเดือน
                    if any(x in normalized_sheet for x in ['สะสม', 'รวม', 'ทั้งปี', 'ม.ค.-', 'ม.ค. -']):
                        print(f"   ⏩ Skipping summary sheet: {sheet_name}")
                        continue
                        
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheets_to_process.append((df, normalized_sheet))
            else:
                df = pd.read_csv(file_path)
                sheets_to_process.append((df, file_name))

            for df, ref_name in sheets_to_process:
                month_eng = "Unknown"
                
                # 1. ลองหาจากชื่อชีทก่อน
                for eng, th_keywords in month_lookup:
                    if any(kw in ref_name for kw in th_keywords):
                        month_eng = eng
                        break
                
                # 2. ถ้าในชื่อชีทไม่มี (เช่น Sheet1) ให้หาจากเนื้อหาใน 3 แถวแรก
                if month_eng == "Unknown":
                    header_content = normalize_thai(str(df.columns.tolist()) + str(df.iloc[0:3].values.tolist()))
                    for eng, th_keywords in month_lookup:
                        if any(kw in header_content for kw in th_keywords):
                            month_eng = eng
                            break

                # หาปี (25xx)
                year_match = re.search(r'25\d{2}', ref_name + normalize_thai(str(df.iloc[0:1])))
                base_year = int(year_match.group(0)) if year_match else 0

                if month_eng != "Unknown":
                    print(f"   ✅ Detected: {month_eng} {base_year} (from sheet: {ref_name})")
                    
                    # คอลัมน์ที่ต้องดึง (Index: จังหวัด, อัตราเข้าพัก, ฯลฯ)
                    curr_idx = [1, 2, 5, 8, 11, 14, 17, 20, 23]
                    last_idx = [1, 3, 6, 9, 12, 15, 18, 21, 24]
                    cols = ['province', 'occupancy_rate', 'total_guests', 'total_visitors', 'thai_visitors', 'foreign_visitors', 'total_revenue', 'thai_revenue', 'foreign_revenue']

                    for mode in ['current', 'last']:
                        indices = curr_idx if mode == 'current' else last_idx
                        target_year = base_year if mode == 'current' else base_year - 1
                        
                        if target_year <= 0: continue
                        
                        temp_df = df.iloc[3:, indices].copy()
                        temp_df.columns = cols
                        temp_df.insert(0, 'year', target_year)
                        temp_df.insert(1, 'month', month_eng)
                        final_data.append(temp_df)
                else:
                    print(f"   ⚠️ Could not identify month for sheet: {ref_name}")
                
        except Exception as e:
            print(f"❌ Error in {file_name}: {e}")

    if not final_data:
        print("No data collected. Check file structure.")
        return

    # รวมไฟล์และ Clean ขั้นสุดท้าย
    full_df = pd.concat(final_data, ignore_index=True)
    full_df = full_df.dropna(subset=['province'])
    full_df['province'] = full_df['province'].astype(str).str.strip()
    
    noise = ['ภาค', 'รวมทั้งหมด', 'หมายเหตุ', 'ที่มา', 'Update', 'P หมายถึง', 'R หมายถึง', 'จังหวัด']
    full_df = full_df[~full_df['province'].str.contains('|'.join(noise))]
    
    for col in full_df.columns[3:]:
        full_df[col] = pd.to_numeric(full_df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    # ลบแถวที่อาจเป็นค่าว่างหรือ 0 ทั้งหมดออก
    full_df = full_df.dropna(subset=['total_visitors'])
    
    # ลบข้อมูลซ้ำ
    full_df = full_df.drop_duplicates(subset=['year', 'month', 'province'])
    full_df = full_df.sort_values(['year', 'month', 'province'])

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'tourism_combined_final.csv')
    full_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("-" * 30)
    print(f"DONE! Data saved to: {output_file}")
    print(f"Total Rows: {len(full_df)}")

if __name__ == "__main__":
    # 1. หาตำแหน่งของไฟล์โค้ดนี้ (src/)
    CURRENT_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    
    # 2. ถอยออกมา 1 ชั้นเพื่อไปที่ตัวโปรเจคหลัก (Root)
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_FILE_PATH, ".."))
    
    # 3. ระบุโฟลเดอร์ที่เก็บไฟล์ดิบ
    INPUT_DIR = os.path.join(PROJECT_ROOT, "ImportData", "Tourism Data")
    
    # 4. ระบุโฟลเดอร์ที่จะเซฟไฟล์คลีน
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
    
    print(f"Checking for files in: {INPUT_DIR}") 
    clean_tourism_data(INPUT_DIR, OUTPUT_DIR)