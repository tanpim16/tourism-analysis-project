import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.dates as mdates

# -----------------------------
# 1. Load data
# -----------------------------
file_path = "data/processed/final_master_with_trends.csv"
df = pd.read_csv(file_path)

# -----------------------------
# 2. Define columns
# -----------------------------
region_col = "Region_EN"
visitor_col = "total_visitors"
year_col = "Year"
month_col = "Month"

# -----------------------------
# 3. Clean Year (Buddhist -> Gregorian)
# -----------------------------
df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
df[year_col] = df[year_col].apply(
    lambda y: y - 543 if pd.notna(y) and y > 2500 else y
)

# -----------------------------
# 4. Clean Month
# -----------------------------
month_lookup = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

def parse_month(value):
    if pd.isna(value):
        return pd.NA
    s = str(value).strip().lower()
    if s.isdigit():
        m = int(s)
        return m if 1 <= m <= 12 else pd.NA
    return month_lookup.get(s, pd.NA)

df["Month_num"] = df[month_col].apply(parse_month)

# -----------------------------
# 5. Create Date
# -----------------------------
df = df.dropna(subset=[year_col, "Month_num"])
df[year_col] = df[year_col].astype(int)
df["Month_num"] = df["Month_num"].astype(int)

df["Date"] = pd.to_datetime(
    dict(year=df[year_col], month=df["Month_num"], day=1),
    errors="coerce"
)

df = df.dropna(subset=["Date"])

# -----------------------------
# 6. Clean visitors
# -----------------------------
df[visitor_col] = pd.to_numeric(df[visitor_col], errors="coerce")
df = df.dropna(subset=[visitor_col, region_col])

# -----------------------------
# 7. Filter date range
# -----------------------------
df = df[
    (df["Date"] >= "2023-01-01") &
    (df["Date"] <= "2025-12-31")
].copy()

# -----------------------------
# 8. Aggregate to one row per region per month
# -----------------------------
df_plot = (
    df.groupby([region_col, "Date"], as_index=False)[visitor_col]
      .sum()
      .sort_values([region_col, "Date"])
)

regions = sorted(df_plot[region_col].unique())

if len(regions) == 0:
    raise ValueError("No regions found after filtering.")

# -----------------------------
# 9. Detect highest-volume region
# -----------------------------
region_max = (
    df_plot.groupby(region_col)[visitor_col]
    .max()
    .sort_values(ascending=False)
)

special_region = region_max.index[0]

print("Special region (Bangkok):", special_region)
print("Regions found:", regions)

# -----------------------------
# 10. Formatter
# -----------------------------
def millions_formatter(x, pos):
    return f"{x / 1_000_000:.0f}M"

date_formatter = mdates.DateFormatter("%b-%y")

# -----------------------------
# 11. Create subplots
# -----------------------------
fig, axes = plt.subplots(
    nrows=len(regions),
    ncols=1,
    figsize=(14, 5 * len(regions)),
    sharex=True
)

if len(regions) == 1:
    axes = [axes]

# -----------------------------
# 12. Plot
# -----------------------------
for ax, region in zip(axes, regions):
    region_df = df_plot[df_plot[region_col] == region].sort_values("Date")

    ax.plot(
        region_df["Date"],
        region_df[visitor_col],
        linestyle="-",
        linewidth=2,
        marker="o",
        markersize=4
    )

    ax.set_title(region, fontsize=12)
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    if region == special_region:
        ax.set_ylim(4_000_000, 8_000_000)
        ax.set_ylabel("Visitors (M)\n(4–8M scale)")
        ax.yaxis.set_major_locator(MultipleLocator(1_000_000))
    else:
        ax.set_ylim(1_000_000, 6_000_000)
        ax.set_ylabel("Visitors (M)\n(1–6M scale)")
        ax.yaxis.set_major_locator(MultipleLocator(1_000_000))

    ax.grid(axis="y", linestyle="--", linewidth=0.9, alpha=0.9)

    # show x-axis on every graph
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(date_formatter)
    ax.tick_params(axis="x", rotation=45, labelbottom=True)

# -----------------------------
# 13. Layout
# -----------------------------
fig.suptitle("Figure 5: Visitor Trends by Region (2023–2025)", fontsize=16)
fig.supxlabel("Date")

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.subplots_adjust(hspace=0.4)

# -----------------------------
# 14. Save
# -----------------------------
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "Figure_5_Visitor Trends by Region.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

# -----------------------------
# 15. Show
# -----------------------------
plt.show()