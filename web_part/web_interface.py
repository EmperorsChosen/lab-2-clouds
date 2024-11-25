from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

USERS_SERVICE_URL = "http://127.0.0.1:5001"
PARCELS_SERVICE_URL = "http://127.0.0.1:5002"

# Головна сторінка
@app.route('/')
def home():
    return render_template('home.html')

# Сторінка реєстрації
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "password": request.form['password']
        }
        response = requests.post(f"{USERS_SERVICE_URL}/register", json=data)
        if response.status_code == 201:
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed: ' + response.json().get("error", "Unknown error"), 'danger')
    return render_template('register.html')

# Сторінка входу
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {
            "email": request.form['email'],
            "password": request.form['password']
        }
        response = requests.post(f"{USERS_SERVICE_URL}/login", json=data)
        if response.status_code == 200:
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            error_message = response.json().get("error", "Invalid credentials")
            flash(f'Login failed: {error_message}', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


# Сторінка з функціоналом роботи з посилками
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
