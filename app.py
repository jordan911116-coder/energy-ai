from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

# ===== 自動辨識欄位 =====
def find_column(columns, keywords):
    for col in columns:
        for key in keywords:
            if key in col.lower():
                return col
    return None


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart = None

    if request.method == "POST":
        file = request.files.get("file")

        # ===== 沒選檔案 =====
        if not file or file.filename == "":
            result = {"error": "請先選擇檔案"}
            return render_template("index.html", result=result, chart=None)

        try:
            # ===== 自動讀取 CSV / Excel =====
            filename = file.filename.lower()

            if filename.endswith(".csv"):
                df = pd.read_csv(file)
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                result = {"error": "只支援 CSV 或 Excel (.xlsx)"}
                return render_template("index.html", result=result, chart=None)

            # 清除欄位空白
            df.columns = df.columns.str.strip()

            print("📊 欄位:", df.columns)
            print(df.head())

            # ===== 自動找用電欄位 =====
            power_col = find_column(df.columns, ["power", "kw", "用電", "electric"])

            if not power_col:
                result = {"error": "找不到用電欄位（power_kw / 用電）"}
                return render_template("index.html", result=result, chart=None)

            # ===== 自動找時間欄位 =====
            time_col = find_column(df.columns, ["time", "hour", "時間"])

            # ===== 轉數字 =====
            df[power_col] = pd.to_numeric(df[power_col], errors='coerce')

            # ===== 計算 =====
            total = df[power_col].sum()
            avg = df[power_col].mean()

            result = {
                "total": round(total, 2),
                "avg": round(avg, 2)
            }

            # ===== 畫圖 =====
            plt.figure()

            if time_col:
                x = df[time_col]
            else:
                x = range(len(df))

            plt.plot(x, df[power_col], marker='o')
            plt.title("Power Trend")
            plt.xlabel("Time")
            plt.ylabel("Power (kW)")

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart = base64.b64encode(img.getvalue()).decode()
            plt.close()

        except Exception as e:
            print("❌ 錯誤:", e)
            result = {"error": str(e)}

    return render_template("index.html", result=result, chart=chart)


# ===== Render 啟動 =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
