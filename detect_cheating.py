import sqlite3
import cv2
import sys
from ultralytics import YOLO
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import threading


# SQLite Database Connection
def get_db_connection():
    conn = sqlite3.connect("cheating_detection.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
cursor = conn.cursor()

# Create table if it does not exist
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

# Ensure video path is provided
if len(sys.argv) < 2:
    print("Usage: python detect_cheating.py <video_path>")
    sys.exit(1)

video_path = sys.argv[1]
video_name = video_path.split("/")[-1]  # Extract filename

# Load YOLO model
model = YOLO('yolov8n.pt')
allowed_classes = ["cell phone", "head phone", "cable" , "wire"]  # Cheating-related objects

cap = cv2.VideoCapture(video_path)
fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frames per second of the video
frame_interval = max(1, int(fps))  # Sample 1 frame per second

# Video Output Setup
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
output_path = "cheating_detected.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

print("\nCheating Detections:")
print("-------------------------")

# Dictionary to store frames with detections
detected_frames = {}

while cap.isOpened():
    frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    timestamp = frame_number / fps
    time_str = f"{int(timestamp // 60)}m {int(timestamp % 60)}s"

    ret, frame = cap.read()
    if not ret:
        break

    if frame_number % frame_interval == 0:
        results = model(frame, conf=0.10)

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                class_name = model.names.get(class_id, "Unknown")

                if class_name in allowed_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])

                    # Print detection
                    print(f"⏱ Time: {time_str} | 🚨 Cheating Type: {class_name} ({confidence:.2f})")

                    # Insert detection into SQLite Database
                    cursor.execute('''
                        INSERT INTO cheating_detections (timestamp, cheating_type, confidence, video_name)
                        VALUES (?, ?, ?, ?)
                    ''', (time_str, class_name, confidence, video_name))

                    conn.commit()

                    for i in range(frame_number, frame_number + fps):
                        detected_frames[i] = (class_name, confidence, (x1, y1, x2, y2))

    if frame_number in detected_frames:
        class_name, confidence, (x1, y1, x2, y2) = detected_frames[frame_number]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{class_name} ({confidence:.2f})", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    out.write(frame)

# Release resources
cap.release()
out.release()
cursor.close()
conn.close()

print("\n✅ Processed video saved as 'cheating_detected.mp4'")
print("✅ Cheating data stored in SQLite Database.")

