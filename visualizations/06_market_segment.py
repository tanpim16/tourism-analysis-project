import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. LOAD DATA
file_path = 'data/processed/final_master_with_trends.csv'
if not os.path.exists(file_path):
    print(f"❌ Error: ไม่พบไฟล์ที่ {file_path}")
    exit()

df = pd.read_csv(file_path)

# --- ฟังก์ชันช่วยหาชื่อคอลัมน์ ---
def find_col(keywords, columns):
    for col in columns:
        if all(k.lower() in col.lower() for k in keywords):
            return col
    return None

col_thai_rev = find_col(['thai', 'revenue'], df.columns)
col_fore_rev = find_col(['foreign', 'revenue'], df.columns)
col_prov     = find_col(['prov', 'en'], df.columns) or find_col(['province'], df.columns)
col_city_type = find_col(['city', 'type'], df.columns)

print(f"📌 กำลังประมวลผลข้อมูลจากคอลัมน์: {col_prov} และ {col_city_type}")

# 2. AGGREGATION (รวมรายได้รายจังหวัด เพื่อให้ชื่อไม่ซ้ำ)
agg_df = df.groupby([col_prov, col_city_type])[[col_thai_rev, col_fore_rev]].sum().reset_index()

# 3. FILTERING (เฉพาะเมืองรอง)
secondary_df = agg_df[agg_df[col_city_type].str.contains('Secondary|รอง', case=False, na=False)].copy()

if secondary_df.empty:
    print("❌ Error: ไม่พบข้อมูลเมืองรอง!")
    exit()

# คำนวณยอดรวมเพื่อใช้เรียงลำดับและทำ Label
secondary_df['total_rev'] = secondary_df[col_thai_rev] + secondary_df[col_fore_rev]
secondary_df = secondary_df.sort_values('total_rev', ascending=False)

# 4. VISUALIZATION (Figure 9)
# --- Styling for a cleaner, more modern aesthetic
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Liberation Sans'],
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.labelcolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': '#cccccc',
})

# ปรับความสูงเป็น 20 นิ้วเพื่อให้แสดง 55 จังหวัดได้สวยงาม
fig, ax = plt.subplots(figsize=(14, 20), facecolor='white')
ax.set_facecolor('#f7f7f7')

bars = secondary_df.set_index(col_prov)[[col_thai_rev, col_fore_rev]].plot(
    kind='barh', 
    stacked=True, 
    color=["#a8ddb5", "#2a8f48"],  # Two complementary shades of green
    ax=ax, 
    width=0.8
)

# --- เพิ่ม Data Labels (ยอดรวม) ที่ปลายแท่ง ---
# เว้นระยะห่างจากปลายแท่งเล็กน้อย (1% ของยอดสูงสุด)
offset = secondary_df['total_rev'].max() * 0.01

for i, total in enumerate(secondary_df['total_rev']):
    ax.text(total + offset, i, 
            f'{total:,.0f}', # ใส่ comma ขั้นหลักพัน
            va='center', 
            fontsize=10, 
            color='#2e2e2e', 
            fontweight='semibold')

# ให้แถวที่ใหญ่ที่สุดอยู่ด้านบน (เรียงจากมากไปน้อย)
ax.invert_yaxis()

# 5. ตกแต่งกราฟให้ดูพรีเมียม
plt.title('Figure 9: Real Revenue Composition (Thai vs Foreigner)\nTotal Economic Contribution of 55 Secondary Cities', 
          fontsize=20, fontweight='bold', pad=40, color='#333333')
plt.xlabel('Total Real Revenue (Million THB)', fontsize=13, fontweight='bold')
plt.ylabel('Province', fontsize=13, fontweight='bold')
plt.legend(['Domestic Revenue (Thai)', 'International Revenue (Foreign)'], 
           loc='lower right', fontsize=12, frameon=True)

# เพิ่มพื้นที่ด้านบนเพื่อให้หัวกราฟ (title) ไม่ชิดขอบ
fig.subplots_adjust(top=0.92)

# ปรับเส้น Grid ให้ดูโมเดิร์น และไม่ดึงสายตามากนัก
ax.grid(axis='x', linestyle='--', alpha=0.35)
ax.grid(axis='y', linestyle=':', alpha=0.15)

# ลบกรอบด้านบนและด้านขวาเพื่อให้กราฟดูโมเดิร์น (Clean look)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#bbbbbb')
ax.spines['bottom'].set_color('#bbbbbb')

# ปรับรูปแบบแกน x ให้แสดง comma ในหลักพัน
import matplotlib.ticker as mtick
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))

# เพิ่มคำบรรยายจำนวนจังหวัดที่ตรวจพบ
plt.text(0.5, 1.02, f'Total: {len(secondary_df)} Secondary Provinces Aggregated', 
         transform=ax.transAxes, fontsize=12, style='italic', ha='center')

# เพิ่มพื้นที่ด้านบนและขวาเพื่อไม่ให้หัวกราฟหรือ legend ถูกตัด
plt.tight_layout(rect=[0, 0, 1, 0.94])

# 6. SAVE & SHOW
os.makedirs('visualizations', exist_ok=True)
output_path = 'visualizations/Figure_9_Revenue_Split.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"✅ สำเร็จ! กราฟ Figure 9 ถูกสร้างแล้วที่: {output_path}")
print(f"📊 พลอตข้อมูลทั้งหมด {len(secondary_df)} จังหวัด")