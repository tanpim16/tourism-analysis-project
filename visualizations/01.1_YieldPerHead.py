import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. โหลดข้อมูล
file_path = 'data/processed/final_master_with_trends.csv'
if not os.path.exists(file_path):
    print(f"❌ Error: ไม่พบไฟล์ข้อมูลที่ '{file_path}'")
    exit()

df = pd.read_csv(file_path)

# --- ส่วนตรวจสอบชื่อคอลัมน์ (Analytical Depth: Data Integrity) ---
revenue_candidates = [c for c in df.columns if 'revenue' in c.lower() and 'real' in c.lower()]
if not revenue_candidates:
    revenue_candidates = [c for c in df.columns if 'revenue' in c.lower()]

if not revenue_candidates:
    print("❌ Error: ไม่พบคอลัมน์รายได้ กรุณาเช็คชื่อคอลัมน์ในไฟล์ของคุณ:", df.columns.tolist())
    exit()

target_revenue_col = revenue_candidates[0]
print(f"✅ ใช้คอลัมน์ '{target_revenue_col}' ในการคำนวณ")

# 2. คำนวณ Yield per Head (Baht per Person)
df['yield_per_head'] = (df[target_revenue_col] * 1000000) / df['total_visitors']

# 3. จัดกลุ่มข้อมูล
yield_stats = df.groupby('City_type_EN')['yield_per_head'].mean().sort_values(ascending=False).reset_index()

# 4. ปรับแต่งกราฟให้สวยระดับพรีเมียม (Aesthetic Upgrade)
sns.set_theme(style="white") # พื้นหลังขาวสะอาด
plt.figure(figsize=(11, 7))

# กำหนดสี: เมืองหลัก = สีฟ้า (#339af0), เมืองรอง = สีเขียว (#51cf66)
# ตรวจสอบลำดับใน yield_stats เพื่อใส่สีให้ตรง
palette = []
for city in yield_stats['City_type_EN']:
    if 'Major' in city:
        palette.append('#339af0') # Blue
    else:
        palette.append('#51cf66') # Green

ax = sns.barplot(data=yield_stats, x='City_type_EN', y='yield_per_head', palette=palette, edgecolor=".2", linewidth=1.5)

# --- เพิ่มรายละเอียดความเป๊ะ (Clarity & Unit Integrity) ---
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f'{height:,.0f} THB', 
                (p.get_x() + p.get_width() / 2., height), 
                ha = 'center', va = 'center', 
                xytext = (0, 15), 
                textcoords = 'offset points',
                fontsize=13, fontweight='bold', color='#2c3e50')

# ปรับ Font และ Labels
plt.title('Figure 2B : Average Yield per Head (Real Revenue per Visitor)', fontsize=16, fontweight='bold', pad=30, color='#1a1a1a')
plt.xlabel('City Classification', fontsize=13, labelpad=15, fontweight='bold')
plt.ylabel('Average Real Revenue (THB per Person)', fontsize=13, labelpad=15, fontweight='bold')

# ปรับ Gridline เฉพาะแนวนอนให้ดูเบาบาง
ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#bdc3c7')
ax.xaxis.grid(False)
sns.despine(left=True) # เอาเส้นขอบด้านซ้ายและบนออกให้ดู Modern

# เพิ่มคำอธิบายสั้นๆ ในกราฟ (Optional - เพิ่มความว้าว)
plt.text(0.5, -0.15, "* Yield calculated as (Real Revenue * 1M) / Total Visitors", 
         ha='center', va='center', transform=ax.transAxes, fontsize=10, style='italic', color='#7f8c8d')

# 5. เซฟรูป (พื้นหลังขาว ไม่โปร่งใส ป้องกัน Dark Mode Issue บน GitHub)
if not os.path.exists('visualizations'): os.makedirs('visualizations')
output_file = 'visualizations/Figure_Yield_Efficiency_Final.png'
plt.savefig(output_file, facecolor='white', transparent=False, bbox_inches='tight', dpi=300)

print(f"📊 DONE")
plt.show()