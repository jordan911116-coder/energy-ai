from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# ===== 自動找欄位 =====
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
        price = request.form.get("price", 5)  # 預設電價5元

        if not file or file.filename == "":
            return render_template("index.html", result={"error": "請上傳檔案"})

        try:
            filename = file.filename.lower()

            # ===== 讀檔 =====
            if filename.endswith(".csv"):
                df = pd.read_csv(file)
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                return render_template("index.html", result={"error": "只支援CSV或Excel"})

            df.columns = df.columns.str.strip()

            # ===== 找欄位 =====
            power_col = find_column(df.columns, ["power", "kw", "用電", "electric"])
            time_col = find_column(df.columns, ["time", "hour", "時間"])

            if not power_col:
                return render_template("index.html", result={"error": "找不到用電欄位"})

            df[power_col] = pd.to_numeric(df[power_col], errors='coerce')

            # ===== 計算 =====
            total = df[power_col].sum()
            avg = df[power_col].mean()

            # ===== 電費 =====
            price = float(price)
            cost = total * price

            # ===== 異常偵測 =====
            std = df[power_col].std()
            threshold = avg + 1.5 * std
            df["anomaly"] = df[power_col] > threshold

            # ===== AI預測 =====
            X = np.arange(len(df)).reshape(-1, 1)
            y = df[power_col].values

            model = LinearRegression()
            model.fit(X, y)

            next_x = np.array([[len(df)]])
            predicted = model.predict(next_x)[0]

            # ===== 結果 =====
            result = {
                "total": round(total, 2),
                "avg": round(avg, 2),
                "cost": round(cost, 2),
                "predicted": round(predicted, 2)
            }

            # ===== 畫圖 =====
            plt.figure()

            x = df[time_col] if time_col else range(len(df))

            # 正常
            plt.plot(x, df[power_col], marker='o', label="正常")

            # 異常點
            anomalies = df[df["anomaly"]]
            if not anomalies.empty:
                plt.scatter(
                    anomalies[time_col] if time_col else anomalies.index,
                    anomalies[power_col],
                    color='red',
                    label="異常"
                )

            # 預測點
            future_x = len(df)
            plt.scatter(
                future_x,
                predicted,
                color='green',
                label="預測"
            )

            plt.title("Power Trend with AI")
            plt.xlabel("Time")
            plt.ylabel("Power (kW)")
            plt.legend()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart = base64.b64encode(img.getvalue()).decode()
            plt.close()

        except Exception as e:
            result = {"error": str(e)}

    return render_template("index.html", result=result, chart=chart)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
