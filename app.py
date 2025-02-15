import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import subprocess
import threading

app = Flask(__name__)


app.secret_key = os.urandom(24)  


def get_db_connection():
    conn = sqlite3.connect("cheating_detection.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')
conn.commit()


cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS cheating_detections ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        timestamp TEXT, 
        cheating_type TEXT, 
        confidence REAL, 
        video_name TEXT 
    ) 
''')
conn.commit()


UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_videos'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_video(file_path):
    try:
        
        result = subprocess.run(["python", "detect_cheating.py", file_path], check=True)
        
        
        detected_video_path = os.path.join(app.config['PROCESSED_FOLDER'], os.path.basename(file_path).rsplit('.', 1)[0] + "_detected.mp4")
        os.rename(file_path, detected_video_path)
        
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cheating_detections (timestamp, cheating_type, confidence, video_name) VALUES (?, ?, ?, ?)",
                ('2025-02-04', 'Phone Usage', 0.95, os.path.basename(detected_video_path)))  
        conn.commit()
        conn.close()
    except subprocess.CalledProcessError as e:
        print(f"Error: detect_cheating.py failed with exit code {e.returncode}")
        return


@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('index'))  
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please choose another one.", "error")
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and user['password'] == password:  
        session['username'] = user['username']  
        return redirect(url_for('index'))  
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)  
    return redirect(url_for('login'))  


@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))  
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files or 'username' not in session:
        return redirect(url_for('login'))  

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(file_path)

    
    threading.Thread(target=process_video, args=(file_path,)).start()

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cheating_detections")
    rows = cursor.fetchall()
    data = [{"id": row["id"], "timestamp": row["timestamp"], "cheating_type": row["cheating_type"], "confidence": row["confidence"], "video_name": row["video_name"]} for row in rows]
    conn.close()
    return render_template('dashboard.html', detections=data)


@app.route('/get_detections')
def get_detections():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cheating_detections")
    rows = cursor.fetchall()
    data = [{"id": row["id"], "timestamp": row["timestamp"], "cheating_type": row["cheating_type"], "confidence": row["confidence"], "video_name": row["video_name"]} for row in rows]
    conn.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
