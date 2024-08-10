from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('blood_bank.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Donor management route
@app.route('/donors', methods=['GET', 'POST'])
def donors():
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        blood_type = request.form['blood_type']
        age = int(request.form['age'])
        last_donation_date = request.form['last_donation_date']

        # Insert donor
        conn.execute('''
        INSERT INTO donors (name, blood_type, age, last_donation_date)
        VALUES (?, ?, ?, ?)
        ''', (name, blood_type, age, last_donation_date))
        conn.commit()

        return redirect(url_for('donors'))

    donors = conn.execute('SELECT * FROM donors').fetchall()
    conn.close()
    return render_template('donors.html', donors=donors)

# Check donor eligibility
@app.route('/check_eligibility/<int:donor_id>')
def check_eligibility(donor_id):
    conn = get_db_connection()
    donor = conn.execute('SELECT age, last_donation_date FROM donors WHERE id = ?', (donor_id,)).fetchone()
    
    if donor:
        age, last_donation_date = donor['age'], donor['last_donation_date']
        last_donation_date = datetime.strptime(last_donation_date, '%Y-%m-%d')
        
        if age < 18 or age > 60:
            status = "Donor is not eligible due to age restrictions."
        elif datetime.now() - last_donation_date < timedelta(days=90):
            status = "Donor is not eligible as the last donation was less than 3 months ago."
        else:
            status = "Donor is eligible to donate."
    else:
        status = "Donor not found."
    
    conn.close()
    return render_template('eligibility.html', status=status)

# Appointment scheduling route
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    conn = get_db_connection()

    if request.method == 'POST':
        donor_id = int(request.form['donor_id'])
        appointment_date = request.form['appointment_date']

        # Schedule appointment
        conn.execute('''
        INSERT INTO appointments (donor_id, appointment_date)
        VALUES (?, ?)
        ''', (donor_id, appointment_date))
        conn.commit()

        return redirect(url_for('appointments'))

    appointments = conn.execute('''
    SELECT donors.name, donors.blood_type, appointments.appointment_date
    FROM appointments
    JOIN donors ON appointments.donor_id = donors.id
    WHERE appointment_date >= ?
    ORDER BY appointment_date
    ''', (datetime.now().strftime('%Y-%m-%d'),)).fetchall()

    donors = conn.execute('SELECT * FROM donors').fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments, donors=donors)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)


