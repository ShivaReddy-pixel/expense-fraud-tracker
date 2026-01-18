from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load transactions
df = pd.read_csv("../data/transactions.csv")
df.columns = df.columns.str.strip().str.lower()

def fraud_score(row):
    score = 0

    amount = float(row["amount"])
    category = str(row["category"])
    time_str = str(row["time"])

    # Rule 1: High amount
    if amount > 1000:
        score += 50

    # Rule 2: Expensive electronics
    if category == "Electronics" and amount > 800:
        score += 30

    # Rule 3: Late night transaction
    try:
        tx_time = datetime.strptime(time_str, "%H:%M").time()
        if 0 <= tx_time.hour <= 5:
            score += 20
    except:
        pass

    return score

def risk_level(score):
    if score >= 70:
        return "High"
    elif score >= 30:
        return "Medium"
    else:
        return "Low"

@app.route("/transactions")
def get_transactions():
    df["fraud_score"] = df.apply(fraud_score, axis=1)
    df["risk_level"] = df["fraud_score"].apply(risk_level)
    return jsonify(df.to_dict(orient="records"))

@app.route("/high-risk")
def high_risk():
    df["fraud_score"] = df.apply(fraud_score, axis=1)
    df["risk_level"] = df["fraud_score"].apply(risk_level)
    high_risk_df = df[df["risk_level"] == "High"]
    return jsonify(high_risk_df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)

