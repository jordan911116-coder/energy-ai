from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64
import os

app = Flask(__name__)

# ===== 中文字體設定（Render穩定）=====
font_prop = None
try:
    font_path = os.path.join("fonts", "NotoSansTC-Regular.ttf")
    font_prop = fm.FontProperties(fname=font_path)
except Exception as e:
    print("字體載入失敗:", e)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart = None

    if request.method == "POST":
        file = request.files.get("file")

        if file:
            try:
                # ===== 修正CSV讀取問題 =====
                df = pd.read_csv(file, encoding='utf-8')
                df.columns = df.columns.str.strip()

                print("📊 CSV內容：")
                print(df.head())

                # ===== 檢查欄位 =====
                if "power_kw" not in df.columns:
                    return render_template("index.html",
                                           result={"error": "CSV缺少 power_kw 欄位"},
                                           chart=None)

                # ===== 分析 =====
                total = df["power_kw"].sum()
                avg = df["power_kw"].mean()

                result = {
                    "total": round(total, 2),
                    "avg": round(avg, 2)
                }

                # ===== 畫圖 =====
                plt.figure()

                # 如果有hour就用，沒有就用index
                if "hour" in df.columns:
                    x = df["hour"]
                else:
                    x = range(len(df))

                plt.plot(x, df["power_kw"], marker='o')

                if font_prop:
                    plt.title("用電趨勢", fontproperties=font_prop)
                    plt.xlabel("時間", fontproperties=font_prop)
                    plt.ylabel("用電(kW)", fontproperties=font_prop)
                else:
                    plt.title("Power Trend")
                    plt.xlabel("Time")
                    plt.ylabel("Power (kW)")

                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                chart = base64.b64encode(img.getvalue()).decode()
                plt.close()

            except Exception as e:
                print("❌ 錯誤：", e)
                result = {"error": str(e)}

    return render_template("index.html", result=result, chart=chart)


# ===== Render啟動 =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
