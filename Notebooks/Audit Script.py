import pandas as pd

# --- 1. LOAD & PREP ---
df_main = pd.read_csv('data/processed/master_tourism_analysis.csv')
province_list = pd.read_csv('data/processed/ProvinceThailandList.csv')

# ล้างช่องว่าง
df_main['ProvinceEN'] = df_main['ProvinceEN'].str.strip()
province_list['ProvinceEN'] = province_list['ProvinceEN'].str.strip()

# Mapping ชื่อ (ลองเช็กตรงนี้ดูครับว่า สระแก้ว ในไฟล์ Master ของคุณสะกดแบบไหน)
name_map = {
    'Chai Nat': 'Chainat', 'Lop Buri': 'Lopburi', 'Sing Buri': 'Singburi',
    'Prachin Buri': 'Prachinburi', 'Nong Bua Lam Phu': 'Nong Bua Lamphu',
    'Si Sa Ket': 'Si Saket', 'Suphan Buri': 'Suphanburi', 'Buri Ram': 'Buriram',
    'Sra Kaeo': 'Sra Kaeo', # ลองสลับเป็น 'Sa Kaeo': 'Sra Kaeo' ถ้าสระแก้วยังเป็น 0
}
df_main['ProvinceEN'] = df_main['ProvinceEN'].replace(name_map)

# --- 2. CALCULATION ---
df_agg = df_main.groupby('ProvinceEN').agg({'total_visitors': 'mean', 'real_revenue': 'mean'}).reset_index()
secondary_base = province_list[province_list['City_type_EN'].str.contains('Secondary', na=False, case=False)].copy()
audit_df = pd.merge(secondary_base[['ProvinceEN', 'Region_EN']], df_agg, on='ProvinceEN', how='left').fillna(0)

# คำนวณค่าจริง
total_secondary_rev = audit_df['real_revenue'].sum()
audit_df['Yield'] = (audit_df['real_revenue'] * 1000000) / audit_df['total_visitors'].replace(0, 1)
audit_df['Share_Pct'] = (audit_df['real_revenue'] / total_secondary_rev) * 100

# เกณฑ์ Median
x_mid = audit_df[audit_df['total_visitors'] > 0]['Yield'].median()
y_mid = audit_df[audit_df['total_visitors'] > 0]['Share_Pct'].median()

def get_quad(row):
    if row['total_visitors'] == 0: return 'MISSING/EMERGING'
    if row['Yield'] >= x_mid and row['Share_Pct'] >= y_mid: return 'STARS'
    if row['Yield'] < x_mid and row['Share_Pct'] >= y_mid: return 'MASS MARKET'
    if row['Yield'] >= x_mid and row['Share_Pct'] < y_mid: return 'PREMIUM NICHE'
    return 'EMERGING'

audit_df['Result_Quadrant'] = audit_df.apply(get_quad, axis=1)

# --- 3. SHOW RESULTS ---
print(f"--- Median Yield: {x_mid:,.2f} | Median Share: {y_mid:,.4f}% ---")
# เรียงตามรายได้จากมากไปน้อย
pd.set_option('display.max_rows', 60)
print(audit_df[['ProvinceEN', 'total_visitors', 'real_revenue', 'Yield', 'Share_Pct', 'Result_Quadrant']].sort_values('real_revenue', ascending=False))