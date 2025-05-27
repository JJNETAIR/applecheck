from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import csv

app = Flask(__name__)
app.secret_key = 'applewifi123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vouchers.db'
db = SQLAlchemy(app)

class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    duration_days = db.Column(db.Integer, nullable=True)

    @property
    def is_valid(self):
        if self.start_date and self.duration_days:
            return datetime.today().date() <= self.start_date + timedelta(days=self.duration_days)
        return False

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    code = request.form['code'].strip()
    voucher = Voucher.query.filter_by(code=code).first()
    if not voucher:
        return render_template('result.html', status='invalid')
    expiry = voucher.start_date + timedelta(days=voucher.duration_days) if voucher.start_date else None
    return render_template('result.html', status='valid' if voucher.is_valid else 'expired',
                           expiry=expiry, days=voucher.duration_days)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != 'admin123':
            flash("Invalid password", "danger")
            return redirect(url_for('admin'))
        return render_template('dashboard.html', vouchers=Voucher.query.all())
    return render_template('admin.html')

@app.route('/add', methods=['POST'])
def add_voucher():
    code = request.form['code'].strip()
    duration = int(request.form['duration'])
    start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
    voucher = Voucher.query.filter_by(code=code).first()
    if voucher:
        voucher.start_date = start_date
        voucher.duration_days = duration
    else:
        voucher = Voucher(code=code, start_date=start_date, duration_days=duration)
        db.session.add(voucher)
    db.session.commit()
    flash('Voucher updated or added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['csv_file']
    if not file:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('admin'))

    stream = file.stream.read().decode("UTF8").splitlines()
    csv_input = csv.reader(stream)
    for row in csv_input:
        if len(row) >= 2:
            code = row[0].strip()
            try:
                duration = int(row[1])
            except ValueError:
                continue
            voucher = Voucher.query.filter_by(code=code).first()
            if not voucher:
                db.session.add(Voucher(code=code, duration_days=duration))
    db.session.commit()
    flash('CSV uploaded successfully!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
