import pandas as pd
import matplotlib.pyplot as plt

# ===== 中文字體設定 =====
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# ===== 讀取CSV資料 =====
df = pd.read_csv("data.csv")
df["hour"] = df["hour"].astype(str)

# ===== 計算平均 =====
average = df["power_kw"].mean()
print("平均用電:", average)

# ===== 異常偵測 =====
for power in df["power_kw"]:
    if power > average * 1.5:
        print("⚠️ 偵測到異常用電:", power)

# ===== 節能分析 =====
price_per_kwh = 3
wasted_energy = 0

for power in df["power_kw"]:
    if power > average:
        wasted_energy += (power - average)

cost = wasted_energy * price_per_kwh

print(f"⚡ 預估浪費電量: {round(wasted_energy,2)} kW")
print(f"💰 預估浪費金額: {round(cost,2)} 元")

# ===== AI預測（簡單版）=====
next_power = df["power_kw"].iloc[-1] * 1.1
print(f"🔮 預測下一小時用電: {round(next_power,2)} kW")

# ===== 畫圖 =====
plt.figure(figsize=(8,5))
plt.plot(df["hour"], df["power_kw"], marker='o')

plt.xlabel("時間")
plt.ylabel("用電 (kW)")
plt.title("工廠用電監測圖")

plt.grid(True)
plt.show()
