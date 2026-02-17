import requests
import pandas as pd
import time
import os

def fetch_all_provinces_cpi(start_year=2566, end_year=2568, output_file='data/raw/cpi_all_provinces.csv'):
    url = "https://index-api.tpso.go.th/OpenApi/Cpip/Month"
    
    # รหัสจังหวัดมาตรฐาน 77 จังหวัดของไทย (ใช้ในระบบ สนค.)
    province_codes = [
        '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', 
        '20', '21', '22', '23', '24', '25', '26', '27', '30', '31', 
        '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', 
        '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', 
        '52', '53', '54', '55', '56', '57', '58', '60', '61', '62', 
        '63', '64', '65', '66', '67', '70', '71', '72', '73', '74', 
        '75', '76', '77', '80', '81', '82', '83', '84', '85', '86', 
        '90', '91', '92', '93', '94', '95', '96'
    ]

    all_data = []
    years = range(start_year, end_year + 1)
    months = range(1, 13)

    print(f"🚀 Starting extraction for {len(province_codes)} provinces...")

    for year in years:
        for month in months:
            for province in province_codes:
                payload = {
                    "yearBase": 2562,
                    "year": year,
                    "month": month,
                    "type": province,
                    "commodities": [] # ดึงดัชนีรวม
                }
                
                try:
                    response = requests.post(url, json=payload, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            for item in data:
                                # เพิ่ม Metadata เพื่อให้ Merge ข้อมูลง่ายขึ้น
                                item['ext_year'] = year
                                item['ext_month'] = month
                                item['province_code'] = province
                                all_data.append(item)
                    else:
                        print(f"⚠️ Warning: Code {response.status_code} for Prov {province} at {month}/{year}")
                
                except Exception as e:
                    print(f"❌ Failed at Prov {province} {month}/{year}: {e}")
                
                # หน่วงเวลาสั้นๆ เพื่อป้องกันโดนบล็อก (Rate Limit)
                # 0.1 วินาที เพราะเราดึงเยอะ (77 จังหวัด x 12 เดือน x 3 ปี = ~2,700 requests)
                time.sleep(0.1) 
            
            print(f"✅ Finished Month {month} Year {year}")

    # สร้าง DataFrame และบันทึกไฟล์
    if all_data:
        df = pd.DataFrame(all_data)
        
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"🎉 Successfully saved data to {output_file}")
        return df
    else:
        print("Empty data.")
        return None

if __name__ == "__main__":
    # รันสคริปต์นี้โดยตรงเพื่อดึงข้อมูล
    fetch_all_provinces_cpi()