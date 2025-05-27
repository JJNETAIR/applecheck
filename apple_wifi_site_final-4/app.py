from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CSV_FILE = 'vouchers.csv'
ADMIN_PASSWORD = 'admin123'

def read_vouchers():
    vouchers = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                vouchers.append(row)
    return vouchers

def write_vouchers(vouchers):
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['code', 'start_date', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for v in vouchers:
            writer.writerow(v)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    result = {}
    if request.method == 'POST':
        code = request.form['code'].strip()
        vouchers = read_vouchers()
        for v in vouchers:
            if v['code'] == code:
                if v['start_date']:
                    start_date = datetime.strptime(v['start_date'], '%Y-%m-%d')
                    days = int(v['type'].replace(' days', ''))
                    end_date = start_date + timedelta(days=days)
                    today = datetime.today()
                    valid = today <= end_date
                    remaining = (end_date - today).days
                    result = {
                        'valid': valid,
                        'start_date': v['start_date'],
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'remaining': remaining
                    }
                else:
                    result = {'valid': False, 'error': 'Voucher not activated yet.'}
                break
        else:
            result = {'valid': False, 'error': 'Invalid voucher code.'}
    return render_template('index.html', result=result)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            vouchers = read_vouchers()
            return render_template('admin.html', vouchers=vouchers, logged_in=True)
        else:
            return render_template('admin.html', error='Invalid password')
    return render_template('admin.html', logged_in=False)

@app.route('/update_voucher', methods=['POST'])
def update_voucher():
    code = request.form.get('code').strip()
    start_date = request.form.get('start_date')
    v_type = request.form.get('type')

    vouchers = read_vouchers()
    found = False
    for v in vouchers:
        if v['code'] == code:
            v['start_date'] = start_date
            v['type'] = v_type
            found = True
            break

    if not found:
        vouchers.append({'code': code, 'start_date': start_date, 'type': v_type})

    write_vouchers(vouchers)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)