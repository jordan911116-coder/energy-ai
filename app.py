from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64
import os

# ===== 中文字體設定 =====
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "fonts", "NotoSansTC-Regular.ttf")

    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False

except Exception as e:
    print("字體載入失敗:", e)
    font_prop = None

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart = None

    if request.method == "POST":
        try:
            data = pd.read_csv("data.csv")

            # 🔥 修正欄位名稱（你的CSV是 power_kw）
            total_usage = data["power_kw"].sum()
            avg_usage = data["power_kw"].mean()

            result = {
                "total": round(total_usage, 2),
                "avg": round(avg_usage, 2)
            }

            # 📈 畫圖
            plt.figure()
            plt.plot(data["power_kw"])
            plt.title("用電趨勢")
            plt.xlabel("時間索引")
            plt.ylabel("用電量 (kW)")

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            chart = base64.b64encode(img.getvalue()).decode()

            plt.close()

        except Exception as e:
            result = {"error": str(e)}

    return render_template("index.html", result=result, chart=chart)


# 🔥 Render 必備（超關鍵）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
