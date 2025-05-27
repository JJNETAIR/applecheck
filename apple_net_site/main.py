from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import csv
import os

app = Flask(__name__)
app.secret_key = 'supersecret'

VOUCHER_CSV = 'vouchers.csv'

def read_vouchers():
    vouchers = []
    if os.path.exists(VOUCHER_CSV):
        with open(VOUCHER_CSV, newline='') as f:
            reader = csv.DictReader(f)
            vouchers = list(reader)
    return vouchers

def write_vouchers(vouchers):
    with open(VOUCHER_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'start_date', 'type'])
        writer.writeheader()
        writer.writerows(vouchers)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    code = request.form.get('code')
    vouchers = read_vouchers()
    for v in vouchers:
        if v['code'] == code:
            start_date = datetime.strptime(v['start_date'], '%Y-%m-%d') if v['start_date'] else None
            days = 15 if v['type'] == '15' else 30
            if start_date:
                valid_until = start_date + timedelta(days=days)
                valid = datetime.now() <= valid_until
                return render_template('result.html', valid=valid, code=code, valid_until=valid_until.date(), days=days)
            else:
                return render_template('result.html', valid=False, code=code, error="Start date missing.")
    return render_template('result.html', valid=False, code=code)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        code = request.form.get('code')
        start_date = request.form.get('start_date')
        vtype = request.form.get('type')
        vouchers = read_vouchers()
        updated = False
        for v in vouchers:
            if v['code'] == code:
                v['start_date'] = start_date
                v['type'] = vtype
                updated = True
        if not updated:
            vouchers.append({'code': code, 'start_date': start_date, 'type': vtype})
        write_vouchers(vouchers)
        flash('Voucher saved or updated successfully.')
        return redirect(url_for('admin'))
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
