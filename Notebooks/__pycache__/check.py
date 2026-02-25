import pandas as pd

df = pd.read_csv('data/processed/master_tourism_analysis.csv')
print(df[['Month']].drop_duplicates().sort_values('Month'))
print("\nColumns ทั้งหมด:", df.columns.tolist())
print("\nตัวอย่างข้อมูล 3 แถว:")
print(df.head(3))