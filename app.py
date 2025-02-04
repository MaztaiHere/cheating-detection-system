import os
import sqlite3
import subprocess
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)

# SQLite Database Connection
def get_db_connection():
    conn = sqlite3.connect("cheating_detection.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if it does not exist
conn = get_db_connection()
cursor = conn.cursor()
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

# Flask Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_videos'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to process the video in a separate thread
def process_video(file_path):
    try:
        # Run the detect_cheating.py script once for processing the video
        result = subprocess.run(["python", "detect_cheating.py", file_path], check=True)
        
        # Rename and move the processed video to the processed_videos folder
        detected_video_path = os.path.join(app.config['PROCESSED_FOLDER'], os.path.basename(file_path).rsplit('.', 1)[0] + "_detected.mp4")
        os.rename(file_path, detected_video_path)
    except subprocess.CalledProcessError as e:
        print(f"Error: detect_cheating.py failed with exit code {e.returncode}")
        return

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for uploading the video
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    # Check if the file is allowed
    if not allowed_file(file.filename):
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the file to the uploads folder
    file.save(file_path)

    # Process the video in a separate thread to avoid blocking Flask
    threading.Thread(target=process_video, args=(file_path,)).start()

    return redirect(url_for('dashboard'))

# Route for the dashboard to display detection results
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cheating_detections")
    rows = cursor.fetchall()
    data = [{"id": row["id"], "timestamp": row["timestamp"], "cheating_type": row["cheating_type"], "confidence": row["confidence"], "video_name": row["video_name"]} for row in rows]
    conn.close()
    return render_template('dashboard.html', detections=data)

# API Route to get all detection data
@app.route('/get_detections')
def get_detections():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cheating_detections")
    rows = cursor.fetchall()
    data = [{"id": row["id"], "timestamp": row["timestamp"], "cheating_type": row["cheating_type"], "confidence": row["confidence"], "video_name": row["video_name"]} for row in rows]
    conn.close()
    return jsonify(data)

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)