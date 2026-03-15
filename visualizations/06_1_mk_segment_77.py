import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
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

col_thai_rev  = find_col(['thai', 'revenue'], df.columns)
col_fore_rev  = find_col(['foreign', 'revenue'], df.columns)
col_prov      = find_col(['prov', 'en'], df.columns) or find_col(['province'], df.columns)
col_city_type = find_col(['city', 'type'], df.columns)

print(f"📌 คอลัมน์ที่ใช้: {col_prov}, {col_city_type}, {col_thai_rev}, {col_fore_rev}")

# 2. AGGREGATION (รวมรายได้รายจังหวัด)
agg_df = (
    df.groupby([col_prov, col_city_type])[[col_thai_rev, col_fore_rev]]
    .sum()
    .reset_index()
)
agg_df['total_rev'] = agg_df[col_thai_rev] + agg_df[col_fore_rev]

# 3. SPLIT: Primary vs Secondary
primary_df = agg_df[
    agg_df[col_city_type].str.contains('Primary|หลัก', case=False, na=False)
].copy().sort_values('total_rev', ascending=False)

secondary_df = agg_df[
    agg_df[col_city_type].str.contains('Secondary|รอง', case=False, na=False)
].copy().sort_values('total_rev', ascending=False)

if primary_df.empty:
    print("❌ Error: ไม่พบข้อมูลเมืองหลัก (Primary)!")
    exit()
if secondary_df.empty:
    print("❌ Error: ไม่พบข้อมูลเมืองรอง (Secondary)!")
    exit()

print(f"📊 Primary cities: {len(primary_df)}, Secondary cities: {len(secondary_df)}")

# 4. STYLING
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

# คำนวณความสูงของแต่ละ panel ตามจำนวนแถว
# ให้ความสูงต่อแถวเท่ากัน → figure จะสูงพอสำหรับ panel ที่มีแถวมากกว่า
row_height = 0.38   # นิ้วต่อแถว
n_primary   = len(primary_df)
n_secondary = len(secondary_df)
fig_height  = max(n_primary, n_secondary) * row_height + 4  # +4 สำหรับ title/legend

fig, (ax_left, ax_right) = plt.subplots(
    1, 2,
    figsize=(22, fig_height),
    facecolor='white'
)

bg_color = '#f7f7f7'

# ─────────────────────────────────────────────
# 5A. LEFT PANEL — Major Cities (Primary)
# ─────────────────────────────────────────────
ax_left.set_facecolor(bg_color)

primary_df.set_index(col_prov)[[col_thai_rev, col_fore_rev]].plot(
    kind='barh',
    stacked=True,
    color=['#89c4e1', '#1a6fa8'],   # สีฟ้าอ่อน / เข้ม
    ax=ax_left,
    width=0.8,
    legend=False
)

# Data labels ฝั่งซ้าย
offset_l = primary_df['total_rev'].max() * 0.01
for i, total in enumerate(primary_df['total_rev']):
    ax_left.text(
        total + offset_l, i,
        f'{total:,.0f}',
        va='center', fontsize=8.5,
        color='#2e2e2e', fontweight='semibold'
    )

ax_left.invert_yaxis()
ax_left.set_title('Major Cities: Revenue Powerhouses',
                   fontsize=14, fontweight='bold', pad=12, color='#333333')
ax_left.set_xlabel('Total Real Revenue (Million THB)', fontsize=11, fontweight='bold')
ax_left.set_ylabel('Province', fontsize=11, fontweight='bold')
ax_left.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
ax_left.grid(axis='x', linestyle='--', alpha=0.35)
ax_left.grid(axis='y', linestyle=':', alpha=0.15)
ax_left.spines['top'].set_visible(False)
ax_left.spines['right'].set_visible(False)
ax_left.spines['left'].set_color('#bbbbbb')
ax_left.spines['bottom'].set_color('#bbbbbb')

# Legend ฝั่งซ้าย
from matplotlib.patches import Patch
legend_left = [
    Patch(facecolor='#89c4e1', label='Domestic (Thai)'),
    Patch(facecolor='#1a6fa8', label='International (Foreign)'),
]
ax_left.legend(handles=legend_left, loc='lower right', fontsize=10)

# ─────────────────────────────────────────────
# 5B. RIGHT PANEL — Secondary Cities
# ─────────────────────────────────────────────
ax_right.set_facecolor(bg_color)

secondary_df.set_index(col_prov)[[col_thai_rev, col_fore_rev]].plot(
    kind='barh',
    stacked=True,
    color=['#a8ddb5', '#2a8f48'],   # สีเขียวอ่อน / เข้ม
    ax=ax_right,
    width=0.8,
    legend=False
)

# Data labels ฝั่งขวา
offset_r = secondary_df['total_rev'].max() * 0.01
for i, total in enumerate(secondary_df['total_rev']):
    ax_right.text(
        total + offset_r, i,
        f'{total:,.0f}',
        va='center', fontsize=8.5,
        color='#2e2e2e', fontweight='semibold'
    )

ax_right.invert_yaxis()
ax_right.set_title('Secondary Cities: Emerging Potential',
                    fontsize=14, fontweight='bold', pad=12, color='#333333')
ax_right.set_xlabel('Total Real Revenue (Million THB)', fontsize=11, fontweight='bold')
ax_right.set_ylabel('')
ax_right.xaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f}'))
ax_right.grid(axis='x', linestyle='--', alpha=0.35)
ax_right.grid(axis='y', linestyle=':', alpha=0.15)
ax_right.spines['top'].set_visible(False)
ax_right.spines['right'].set_visible(False)
ax_right.spines['left'].set_color('#bbbbbb')
ax_right.spines['bottom'].set_color('#bbbbbb')

# Legend ฝั่งขวา
legend_right = [
    Patch(facecolor='#a8ddb5', label='Domestic (Thai)'),
    Patch(facecolor='#2a8f48', label='International (Foreign)'),
]
ax_right.legend(handles=legend_right, loc='lower right', fontsize=10)

# 6. SUPER TITLE
fig.suptitle(
    'Figure 9: Comparison of Revenue Structure between Primary and Secondary Tiers',
    fontsize=18, fontweight='bold', y=1.005, color='#222222'
)

plt.tight_layout(rect=[0, 0, 1, 1])

# 7. SAVE
os.makedirs('visualizations', exist_ok=True)
output_path = 'visualizations/Figure_12_Revenue_Comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print(f"✅ สำเร็จ! บันทึกที่: {output_path}")
print(f"📊 Primary: {n_primary} จังหวัด | Secondary: {n_secondary} จังหวัด")