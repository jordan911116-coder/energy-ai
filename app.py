from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64
import os

app = Flask(__name__)

# ===== 字體修正（Render可用）=====
try:
    font_path = os.path.join("fonts", "NotoSansTC-Regular.ttf")
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'Noto Sans TC'
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("字體載入失敗")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart = None

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            df = pd.read_csv(file)

            total = df["power_kw"].sum()
            avg = df["power_kw"].mean()

            result = {
                "total": round(total, 2),
                "avg": round(avg, 2)
            }

            # 畫圖
            plt.figure()
            plt.plot(df["hour"], df["power_kw"], marker='o')
            plt.title("用電趨勢")
            plt.xlabel("時間")
            plt.ylabel("用電(kW)")

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart = base64.b64encode(img.getvalue()).decode()
            plt.close()

    return render_template("index.html", result=result, chart=chart)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
