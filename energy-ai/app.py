from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# ===== 中文字體設定 =====
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        # ===== 基本分析 =====
        average = df["power_kw"].mean()
        wasted_energy = sum([p - average for p in df["power_kw"] if p > average])
        cost = wasted_energy * 3

        # ===== AI預測（簡單版）=====
        next_power = df["power_kw"].iloc[-1] * 1.1

        # ===== 產生圖表 =====
        plt.figure()
        plt.plot(df["hour"], df["power_kw"], marker='o')
        plt.xlabel("時間")
        plt.ylabel("用電 (kW)")
        plt.title("用電趨勢圖")

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # ===== 傳給前端 =====
        result = {
            "average": round(average, 2),
            "wasted": round(wasted_energy, 2),
            "cost": round(cost, 2),
            "predict": round(next_power, 2),
            "plot": plot_url
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()