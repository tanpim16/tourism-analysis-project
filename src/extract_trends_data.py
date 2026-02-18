import pandas as pd
from pytrends.request import TrendReq
import time
import random
import os

def fetch_comprehensive_trends(provinces_df):
    """
    ดึงข้อมูล Google Trends แยกเป็น 2 Category: 
    1. Thai Intent (เที่ยว + ชื่อจังหวัด)
    2. Foreign Intent (Province Name + Tourism)
    """
    pytrends = TrendReq(hl='th-TH', tz=360, retries=5, backoff_factor=1)
    
    all_combined_data = []
    chunk_size = 5 # Google Limit
    
    # ดึงรายชื่อจังหวัดทั้งไทยและอังกฤษ
    provinces_th = provinces_df['ProvinceThai'].tolist()
    provinces_en = provinces_df['ProvinceEN'].tolist()

    for i in range(0, len(provinces_th), chunk_size):
        chunk_th = provinces_th[i : i + chunk_size]
        chunk_en = provinces_en[i : i + chunk_size]
        
        # สร้างชุด Keywords 2 แบบตามที่เราตบไอเดียกัน
        # 1. สำหรับตลาดในประเทศ (Thai)
        kw_thai = [f"เที่ยว{p}" for p in chunk_th]
        # 2. สำหรับตลาดต่างประเทศ (Foreign)
        kw_foreign = [f"{p} Tourism" for p in chunk_en]

        # --- ส่วนที่ 1: ดึงข้อมูลฝั่งไทย ---
        print(f"📡 [{i//chunk_size + 1}] กำลังดึงข้อมูลฝั่งไทย: {kw_thai}...")
        df_thai = get_trends_data(pytrends, kw_thai, "Thai_Intent")
        if df_thai is not None:
            all_combined_data.append(df_thai)
        
        # พักเบรกสั้นๆ ระหว่างดึงชุดไทยกับต่างชาติ
        time.sleep(random.uniform(3, 6))

        # --- ส่วนที่ 2: ดึงข้อมูลฝั่งต่างชาติ ---
        print(f"📡 [{i//chunk_size + 1}] กำลังดึงข้อมูลฝั่งต่างชาติ: {kw_foreign}...")
        df_foreign = get_trends_data(pytrends, kw_foreign, "Foreign_Intent")
        if df_foreign is not None:
            # Map ชื่อภาษาอังกฤษกลับเป็นภาษาไทยเพื่อให้ Merge ง่าย
            en_to_th = dict(zip(kw_foreign, chunk_th))
            df_foreign['ProvinceThai'] = df_foreign['Keyword'].map(en_to_th)
            all_combined_data.append(df_foreign)

        # --- ระบบป้องกันโดนแบน (Cooldown) ---
        wait_time = random.uniform(8, 15)
        if (i // chunk_size) % 2 == 0 and i > 0:
            print("💤 พักเบรกยาว 30 วินาที เพื่อหลบระบบตรวจจับบอท...")
            wait_time += 20
        
        print(f"⏳ รอ {wait_time:.2f} วินาที... \n")
        time.sleep(wait_time)

    # --- รวมร่างและยุบข้อมูล (Aggregation) ---
    if all_combined_data:
        full_df = pd.concat(all_combined_data, ignore_index=True)
        print("🔄 กำลังยุบข้อมูลรายสัปดาห์ -> รายเดือน และจัดการเรื่องปี พ.ศ./ค.ศ. ...")
        
        # 1. จัดการเรื่องวันที่
        full_df['Year_AD'] = full_df['date'].dt.year
        full_df['Year_BE'] = full_df['Year_AD'] + 543
        full_df['Month'] = full_df['date'].dt.strftime('%b')

        # 2. Groupby เพื่อหาค่าเฉลี่ยรายเดือน แยกตาม Category
        final_df = full_df.groupby(
            ['ProvinceThai', 'Year_AD', 'Year_BE', 'Month', 'Category'], 
            as_index=False
        )['Search_Interest'].mean()

        final_df['Search_Interest'] = final_df['Search_Interest'].round(2)
        return final_df
    
    return None

def get_trends_data(pytrends_obj, keywords, category_name):
    """ฟังก์ชันช่วยดึงข้อมูลและจัดการ Error"""
    try:
        pytrends_obj.build_payload(keywords, cat=67, timeframe='2023-01-01 2025-12-31', geo='TH')
        df = pytrends_obj.interest_over_time()
        
        if not df.empty:
            df = df.drop(columns=['isPartial']).reset_index()
            # Melt ข้อมูลจากกว้างเป็นยาว
            df_long = df.melt(id_vars=['date'], value_vars=keywords, 
                              var_name='Keyword', value_name='Search_Interest')
            df_long['Category'] = category_name
            
            # ถ้าเป็นฝั่งไทย ให้สกัดชื่อจังหวัดไว้เลย
            if category_name == "Thai_Intent":
                df_long['ProvinceThai'] = df_long['Keyword'].str.replace('เที่ยว', '', regex=False)
            
            return df_long
    except Exception as e:
        print(f"⚠️ Error ในหมวด {category_name}: {e}")
        return None

if __name__ == "__main__":
    input_path = 'data/processed/ProvinceThailandList.csv'
    output_path = 'data/processed/Google_Trends_Data.csv'

    if os.path.exists(input_path):
        prov_df = pd.read_csv(input_path)
        final_result = fetch_comprehensive_trends(prov_df)

        if final_result is not None:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            final_result.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"🎉 เสร็จสมบูรณ์! ข้อมูลถูกบันทึกไว้ที่: {output_path}")
            print(final_result.sample(10)) # สุ่มตัวอย่างมาโชว์ 10 แถว
    else:
        print("❌ ไม่พบไฟล์รายชื่อจังหวัด!")