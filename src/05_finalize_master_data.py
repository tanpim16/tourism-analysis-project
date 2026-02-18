import pandas as pd
import os

def finalize_data_pipeline():
    # 1. กำหนด Path ไฟล์
    master_path = 'data/processed/master_tourism_analysis.csv'
    trends_path = 'data/processed/Google_Trends_Data.csv'
    output_path = 'data/processed/final_master_with_trends.csv'

    # ตรวจสอบว่ามีไฟล์พร้อมหรือยัง
    if not os.path.exists(master_path) or not os.path.exists(trends_path):
        print("❌ ยังหาไฟล์ไม่เจอ! รอให้สคริปต์ extract_trends รันเสร็จก่อนนะครับ")
        return

    # 2. โหลดข้อมูล
    print("📖 กำลังโหลดข้อมูล...")
    df_master = pd.read_csv(master_path)
    df_trends = pd.read_csv(trends_path)

    # 3. 🌟 ขั้นตอนสำคัญ: Pivot Table 🌟
    # เปลี่ยนจากหมวดหมู่แนวตั้ง (Long) ให้เป็นคอลัมน์แนวนอน (Wide)
    print("🔄 กำลัง Pivot ข้อมูล Google Trends (Thai vs Foreign)...")
    df_trends_pivot = df_trends.pivot_table(
        index=['ProvinceThai', 'Year_BE', 'Month'], # ใช้ พ.ศ. เป็นหลักตาม Master
        columns='Category', 
        values='Search_Interest'
    ).reset_index()

    # เปลี่ยนชื่อคอลัมน์ให้สื่อความหมายและง่ายต่อการใช้ใน Code
    df_trends_pivot = df_trends_pivot.rename(columns={
        'Thai_Intent': 'search_thai',
        'Foreign_Intent': 'search_foreign',
        'Year_BE': 'Year' # เปลี่ยนให้ชื่อตรงกับ Master Table
    })

    # 4. Merge เข้ากับ Master Table
    print("🔗 กำลังรวมร่างกับ Master Table...")
    df_final = pd.merge(
        df_master,
        df_trends_pivot,
        on=['ProvinceThai', 'Year', 'Month'],
        how='left'
    )

    # 5. Fill Missing Values (ถ้าบางเดือนไม่มีการค้นหา ให้เป็น 0)
    df_final['search_thai'] = df_final['search_thai'].fillna(0)
    df_final['search_foreign'] = df_final['search_foreign'].fillna(0)

    # 6. บันทึกผลลัพธ์
    df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print("-" * 30)
    print(f"🎉 เสร็จสมบูรณ์! ไฟล์ Final อยู่ที่: {output_path}")
    print(f"📊 ขนาดข้อมูลล่าสุด: {df_final.shape[0]} แถว, {df_final.shape[1]} คอลัมน์")
    print("-" * 30)
    print("💡 คอลัมน์ใหม่ที่เพิ่มเข้ามา: [search_thai, search_foreign]")

if __name__ == "__main__":
    finalize_data_pipeline()