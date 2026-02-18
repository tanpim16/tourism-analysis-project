import pandas as pd
from pytrends.request import TrendReq
import time
import random
import os

def fetch_google_trends_thailand(provinces_list):
    # 1. ตั้งค่า pytrends
    # hl=th-TH (ภาษาไทย), tz=360 (Timezone ไทย)
    pytrends = TrendReq(hl='th-TH', tz=360, retries=5, backoff_factor=1)
    
    all_data = []
    chunk_size = 5 # Google ให้ดึงได้สูงสุดครั้งละ 5 keywords
    
    for i in range(0, len(provinces_list), chunk_size):
        chunk = provinces_list[i : i + chunk_size]
        keywords = [f"เที่ยว{p}" for p in chunk]
        
        print(f"📡 กำลังดึงข้อมูลกลุ่ม {i//chunk_size + 1}: {keywords}...")
        
        try:
            # 2. ส่ง Request (cat=67 คือหมวดหมู่ Travel)
            # ดึงช่วงปี 2023-2025 (ค.ศ.)
            pytrends.build_payload(
                keywords, 
                cat=67, 
                timeframe='2023-01-01 2025-12-31', 
                geo='TH'
            )
            
            df = pytrends.interest_over_time()
            
            if not df.empty:
                df = df.drop(columns=['isPartial']).reset_index()
                
                # จัดรูปข้อมูลจากแนวนอนเป็นแนวตั้ง (Melt)
                df_melted = df.melt(id_vars=['date'], value_vars=keywords, 
                                    var_name='Keyword', value_name='Search_Interest')
                
                # สกัดชื่อจังหวัด (ลบคำว่า 'เที่ยว' ออก)
                df_melted['ProvinceThai'] = df_melted['Keyword'].str.replace('เที่ยว', '', regex=False)
                
                # 3. จัดการเรื่อง "ปี" (ค.ศ. และ พ.ศ.) และ "เดือน"
                df_melted['Year_AD'] = df_melted['date'].dt.year  # ปี ค.ศ.
                df_melted['Year_BE'] = df_melted['Year_AD'] + 543 # ปี พ.ศ.
                df_melted['Month'] = df_melted['date'].dt.strftime('%b') # ชื่อเดือนย่อ (Jan, Feb...)
                
                all_data.append(df_melted)
                print(f"✅ สำเร็จ!")
            
            # 4. 🛡️ ระบบป้องกันโดนแบน (Cooldown)
            wait_time = random.uniform(5, 12)
            if (i // chunk_size) % 3 == 0 and i > 0:
                print("💤 พักเบรกยาว 20 วินาทีเพื่อความปลอดภัย...")
                wait_time += 20
                
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"❌ Error กลุ่ม {chunk}: {e}")
            print("💤 พัก 60 วินาทีแล้วจะลองใหม่...")
            time.sleep(60)
            continue

    if all_data:
        # --- 🌟 ขั้นตอนการ Aggregation (ยุบเป็นรายเดือน) 🌟 ---
        raw_df = pd.concat(all_data, ignore_index=True)
        
        print("\n🔄 กำลังประมวลผลยุบข้อมูลสัปดาห์ -> รายเดือน...")
        
        # ยุบข้อมูลด้วยการหาค่าเฉลี่ย (Mean) แยกตามจังหวัดและช่วงเวลา
        final_df = raw_df.groupby(
            ['ProvinceThai', 'Year_AD', 'Year_BE', 'Month'], 
            as_index=False
        )['Search_Interest'].mean()
        
        # ปัดเศษทศนิยม
        final_df['Search_Interest'] = final_df['Search_Interest'].round(2)
        
        return final_df
    return None

if __name__ == "__main__":
    # ตรวจสอบ Path และโหลดรายชื่อจังหวัด
    input_prov = 'data/processed/ProvinceThailandList.csv'
    output_file = 'data/processed/Google_Trends_Data.csv'
    
    if os.path.exists(input_prov):
        df_prov = pd.read_csv(input_prov)
        # ตรวจสอบว่าใช้ชื่อคอลัมน์ ProvinceThai
        provinces = df_prov['ProvinceThai'].unique().tolist()
        
        # รันการดึงข้อมูล
        result_df = fetch_google_trends_thailand(provinces)
        
        if result_df is not None:
            # สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            # บันทึกไฟล์
            result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n🎉 เสร็จสมบูรณ์! บันทึกไฟล์ที่: {output_file}")
            print(result_df.head())
    else:
        print(f"❌ ไม่พบไฟล์รายชื่อจังหวัดที่: {input_prov}")