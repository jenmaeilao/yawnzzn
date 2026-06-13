# A simple web application.
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
import os

app = Flask(__name__, static_folder='templates/assets', static_url_path='/assets')
app.secret_key = os.urandom(24)  # For session management

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        dob TEXT NOT NULL,
                        password TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

init_db()  # Initialize database on startup

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/signin", methods=["POST"])
def signin():
    email = request.form.get("email")
    password = request.form.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, hashed_password)).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        return redirect(url_for('home'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('index'))

@app.route("/signup", methods=["POST"])
def signup():
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    dob = request.form.get("dob")
    password = request.form.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (full_name, email, dob, password) VALUES (?, ?, ?, ?)',
                     (full_name, email, dob, hashed_password))
        conn.commit()
        flash('Account created successfully! Please sign in.')
    except sqlite3.IntegrityError:
        flash('Email already exists.')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

@app.route("/home")
def home():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template("index.html")

@app.route("/hello/<name>")
def greet(name="Stranger"):
    return render_template("greeting.html", name=name)

@app.route("/order", methods=("GET", "POST"))
def order():
    if request.method == "POST":
        drink = request.form["drink"]
        print("Drink: ", drink)
        return render_template("print.html", drink=drink)

    return render_template("forms.html")

@app.route('/<path:filename>')
def serve_file(filename):
    if filename.endswith('.html'):
        return render_template(filename)
    else:
        return app.send_static_file(filename)
    
@app.route("/debug-users")
def show_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, full_name, email, dob FROM users').fetchall()
    conn.close()
    
    # I-display lang natin as simple list para makita mo
    output = "<h1>List of Accounts</h1>"
    for user in users:
        output += f"<p>ID: {user['id']} | Name: {user['full_name']} | Email: {user['email']}</p>"
    return output

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)