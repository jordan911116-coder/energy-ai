from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import io
import base64
import os

app = Flask(__name__)

# ===== 字體（安全版，不會爆）=====
font_prop = None
try:
    font_path = os.path.join("fonts", "NotoSansTC-Regular.ttf")
    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
except Exception as e:
    print("字體載入失敗:", e)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart = None

    if request.method == "POST":
        file = request.files.get("file")

        # ===== 沒選檔案 =====
        if not file or file.filename == "":
            result = {"error": "請先選擇CSV檔案"}
            return render_template("index.html", result=result, chart=None)

        try:
            # ===== 讀取CSV（穩定版）=====
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()

            print("📊 CSV內容：")
            print(df.head())

            # ===== 檢查欄位 =====
            if "power_kw" not in df.columns:
                result = {"error": "CSV缺少 power_kw 欄位"}
                return render_template("index.html", result=result, chart=None)

            # ===== 強制轉數字 =====
            df["power_kw"] = pd.to_numeric(df["power_kw"], errors='coerce')

            # ===== 計算 =====
            total = df["power_kw"].sum()
            avg = df["power_kw"].mean()

            result = {
                "total": round(total, 2),
                "avg": round(avg, 2)
            }

            # ===== 畫圖 =====
            plt.figure()

            if "hour" in df.columns:
                x = df["hour"]
            else:
                x = range(len(df))

            plt.plot(x, df["power_kw"], marker='o')

            # ===== 字體（不會炸）=====
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


# ===== Render 啟動 =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
