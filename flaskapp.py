from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'users.db')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# SQLite setup
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    firstname TEXT,
    lastname TEXT,
    email TEXT,
    address TEXT)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    address = request.form['address']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
              (username, password, firstname, lastname, email, address))
    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    word_count = None
    filename = os.path.join(UPLOAD_FOLDER, f"{username}_Limerick.txt")

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            word_count = len(f.read().split())

    return render_template('profile.html', user=user, word_count=word_count)

@app.route('/relogin')
def relogin():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid credentials"

@app.route('/upload/<username>', methods=['POST'])
def upload(username):
    if 'limerick' not in request.files:
        return "No file part"

    file = request.files['limerick']

    if file.filename == '':
        return "No selected file"

    filename = os.path.join(UPLOAD_FOLDER, f"{username}_Limerick.txt")
    file.save(filename)

    return redirect(url_for('profile', username=username))

@app.route('/download/<username>')
def download(username):
    filename = os.path.join(UPLOAD_FOLDER, f"{username}_Limerick.txt")

    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return "File not found"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
