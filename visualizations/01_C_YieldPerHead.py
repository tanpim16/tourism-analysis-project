import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ─── Style Configuration ──────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  'white',
    'axes.facecolor':    '#F8F9FA',
    'axes.grid':         True,
    'grid.color':        '#FFFFFF',
    'grid.linewidth':    1.2,
    'font.family':       'sans-serif',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom':False,
})

# ─── Load Data ────────────────────────────────────────────────────────────────
file_path = 'data/processed/final_master_with_trends.csv'

if not os.path.exists(file_path):
    print(f"❌ Error: ไม่พบไฟล์ '{file_path}'")
    exit()

df = pd.read_csv(file_path)

# ─── Column Detection ─────────────────────────────────────────────────────────
revenue_candidates = [c for c in df.columns if 'revenue' in c.lower() and 'real' in c.lower()]
if not revenue_candidates:
    revenue_candidates = [c for c in df.columns if 'revenue' in c.lower()]

if not revenue_candidates:
    print("❌ ไม่พบคอลัมน์รายได้:", df.columns.tolist())
    exit()

target_revenue_col = revenue_candidates[0]

# ─── Compute Yield ────────────────────────────────────────────────────────────
# คำนวณรายได้ต่อหัว: (รายได้จริงหน่วยล้าน * 1,000,000) / จำนวนนักท่องเที่ยว
df['yield_per_head'] = (df[target_revenue_col] * 1_000_000) / df['total_visitors']

# ─── Aggregate ────────────────────────────────────────────────────────────────
yield_stats = (
    df.groupby('City_type_EN')['yield_per_head']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

# ─── Plotting ─────────────────────────────────────────────────────────────────
sns.set_theme(style="white")
fig, ax = plt.subplots(figsize=(10, 7)) # ปรับสัดส่วนให้เตี้ยลงเล็กน้อยเพื่อความสมดุล

# กำหนดสีแยกตามประเภทเมือง
palette = ["#1B4F8A" if 'Major' in city else "#16A085" for city in yield_stats['City_type_EN']]

sns.barplot(
    data=yield_stats,
    x='City_type_EN',
    y='yield_per_head',
    palette=palette,
    edgecolor=".2",
    linewidth=1.2,
    ax=ax
)

# ─── Value Labels (ปรับขนาดให้พอดี) ──────────────────────────────────────────────
for p in ax.patches:
    ax.annotate(
        f'{p.get_height():,.0f}',
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='bottom',
        xytext=(0, 8),
        textcoords='offset points',
        fontsize=14,
        fontweight='bold',
        color='#2c3e50'
    )

# ─── Title & Labels (จุดที่แก้ไข) ───────────────────────────────────────────────
# ใช้ ax.set_title แทน suptitle เพื่อให้ระยะห่างคงที่และไม่ดู "ลอย" เกินไป
ax.set_title(
    'Average Yield per Head (Real Revenue per Visitor)',
    fontsize=14,
    fontweight='bold',
    pad=25,
    color='#2c3e50'
)

ax.set_xlabel('')
ax.set_ylabel('Average Real Revenue (THB per Person)', fontsize=14, labelpad=10)

# ─── Axis Limits & Ticks ──────────────────────────────────────────────────────
ax.set_ylim(0, 8500) # เพิ่มพื้นที่ด้านบนนิดหน่อยเพื่อให้ Label ไม่ชนขอบ
ax.set_yticks(range(0, 8001, 1000))
ax.tick_params(axis='both', labelsize=14)

# ─── Grid & Despine ───────────────────────────────────────────────────────────
ax.yaxis.grid(True, linestyle='--', alpha=0.6, color='#bdc3c7')
ax.xaxis.grid(False)
sns.despine(left=True, bottom=False)

# ─── Footnote ─────────────────────────────────────────────────────────────────
ax.text(
    0.5, -0.15,
    "* Yield = (Real Revenue × 1,000,000) / Total Visitors",
    ha='center', va='center', transform=ax.transAxes,
    fontsize=12, style='italic', color='#7f8c8d'
)

# ─── Layout Adjustment ────────────────────────────────────────────────────────
plt.tight_layout()

# ─── Save & Show ──────────────────────────────────────────────────────────────
output_dir = 'visualizations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = f'{output_dir}/Figure_1C_Yield_efficiency.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')

print(f"✅ Visualization saved to: {output_file}")
plt.show()