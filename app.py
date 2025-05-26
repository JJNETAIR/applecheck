
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json, os

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        code = request.form["code"].strip()
        data = load_data()
        if code in data:
            start_date = datetime.strptime(data[code]["start_date"], "%Y-%m-%d")
            days_valid = 15 if data[code]["type"] == "15" else 30
            end_date = start_date + timedelta(days=days_valid)
            remaining_days = (end_date - datetime.now()).days
            valid = remaining_days >= 0
            result = {
                "valid": valid,
                "end_date": end_date.strftime("%Y-%m-%d"),
                "remaining_days": max(0, remaining_days)
            }
        else:
            result = {"valid": False}
    return render_template("index.html", result=result)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    if request.method == "POST":
        code = request.form["code"].strip()
        start_date = request.form["start_date"]
        duration_type = request.form["type"]
        data = load_data()
        data[code] = {"start_date": start_date, "type": duration_type}
        save_data(data)
        message = "Voucher added successfully!"
    return render_template("admin.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
