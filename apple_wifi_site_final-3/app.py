from flask import Flask, render_template, request, redirect, url_for, flash, session
import csv
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'apple_wifi_secret'

VOUCHERS_FILE = 'vouchers.csv'

def load_vouchers():
    vouchers = []
    if os.path.exists(VOUCHERS_FILE):
        with open(VOUCHERS_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                vouchers.append(row)
    return vouchers

def save_vouchers(vouchers):
    with open(VOUCHERS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['code', 'start_date', 'type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for v in vouchers:
            writer.writerow(v)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        code = request.form['code']
        vouchers = load_vouchers()
        for v in vouchers:
            if v['code'] == code:
                if v['start_date']:
                    days = 15 if v['type'] == '15' else 30
                    start = datetime.strptime(v['start_date'], '%Y-%m-%d')
                    expiry = start + timedelta(days=days)
                    remaining = (expiry - datetime.today()).days
                    valid = remaining >= 0
                    result = {
                        'valid': valid,
                        'expiry': expiry.strftime('%Y-%m-%d'),
                        'remaining': max(remaining, 0)
                    }
                else:
                    result = {'valid': False, 'message': 'Start date not set'}
                break
        else:
            result = {'valid': False, 'message': 'Code not found'}
    return render_template('index.html', result=result)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    vouchers = load_vouchers()
    return render_template('admin.html', vouchers=vouchers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    code = request.form['code']
    start_date = request.form['start_date']
    vtype = request.form['type']
    vouchers = load_vouchers()
    vouchers.append({'code': code, 'start_date': start_date, 'type': vtype})
    save_vouchers(vouchers)
    return redirect(url_for('admin'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    if file:
        file.save(VOUCHERS_FILE)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)