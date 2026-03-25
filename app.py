from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

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
        price = request.form.get("price", 5)

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

            # ===== 基本計算 =====
            total = df[power_col].sum()
            avg = df[power_col].mean()

            price = float(price)
            cost = total * price

            # ===== 異常偵測（Z-score）=====
            mean = df[power_col].mean()
            std = df[power_col].std()
            df["zscore"] = (df[power_col] - mean) / std
            df["anomaly"] = abs(df["zscore"]) > 1.5

            # ===== AI預測（Polynomial）=====
            X = np.arange(len(df)).reshape(-1, 1)
            y = df[power_col].values

            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(X)

            model = LinearRegression()
            model.fit(X_poly, y)

            next_x = poly.transform([[len(df)]])
            predicted = model.predict(next_x)[0]

            result = {
                "total": round(total, 2),
                "avg": round(avg, 2),
                "cost": round(cost, 2),
                "predicted": round(predicted, 2)
            }

            # ===== 畫圖 =====
            plt.figure(figsize=(8,5))

            x = df[time_col] if time_col else range(len(df))

            plt.plot(x, df[power_col], marker='o', label="Usage")

            anomalies = df[df["anomaly"]]
            if not anomalies.empty:
                plt.scatter(
                    anomalies[time_col] if time_col else anomalies.index,
                    anomalies[power_col],
                    color='red',
                    label="Anomaly"
                )

            plt.scatter(len(df), predicted, color='green', label="Prediction")

            plt.title("Energy Usage Trend")
            plt.xlabel("Time")
            plt.ylabel("kW")
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
