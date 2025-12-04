from flask import Flask, render_template, Response, jsonify
from inference import get_model
import supervision as sv
import cv2
import numpy as np
import time
from datetime import datetime
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for, flash, g

# -------------------------------
# CONFIG
# -------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'users.db'
VIDEO_SOURCE = "input2.mp4"

# -------------------------------
# DATABASE MANAGEMENT
# -------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()

# Initialize DB on startup
# Note: In a production app, this might be done differently
if not os.path.exists(DATABASE):
    init_db()
else:
    # Ensure table exists even if file exists
    init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------
# AUTH ROUTES
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
            
        db = get_db()
        try:
            hashed_password = generate_password_hash(password)
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
            return redirect(url_for('register'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Global list to store cheating logs
cheating_logs = []

# Load your Roboflow model
# Note: Ideally, api_key should be an environment variable.
model = get_model(
    model_id="cheating-detection-ygrsh/1",
    api_key="Dr4Em209Ivd1tzLWamdY"
)

# Supervision annotators
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Global control flag
monitoring_active = False

def generate_frames():
    global monitoring_active
    
    # Open video file
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {VIDEO_SOURCE}")
        return

    # Get video FPS for smooth playback
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # Default to 30 FPS if unable to get
    
    frame_delay = 1.0 / fps
    last_frame_time = time.time()

    while True:
        if not monitoring_active:
            # Yield a blank or placeholder frame when not monitoring
            # Or just sleep to save resources
            time.sleep(0.1)
            # Create a black frame with text "Monitoring Paused"
            blank_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Monitoring Paused", (400, 360), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue

        success, frame = cap.read()
        if not success:
            # Loop video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Run inference
        results = model.infer(frame)[0]

        # Convert to Supervision detections
        detections = sv.Detections.from_inference(results)

        # Log detections
        if len(detections) > 0:
            current_time = datetime.now().strftime("%H:%M:%S")
            # Get unique labels detected
            labels = set()
            for class_id in detections.class_id:
                 if hasattr(model, "class_names"):
                     labels.add(model.class_names[class_id])
                 else:
                     labels.add(f"Class {class_id}")
            
            # Filter for cheating detection
            cheating_detected = False
            for label in labels:
                if "cheating" in label.lower():
                    cheating_detected = True
                    break
            
            if cheating_detected:
                log_entry = {
                    "timestamp": current_time,
                    "message": f"⚠️ CHEATING DETECTED at {current_time}"
                }
                
                # Avoid duplicate logs in the same second to reduce noise
                if not cheating_logs or cheating_logs[-1]["timestamp"] != current_time:
                    cheating_logs.append(log_entry)
                    # Keep only last 50 logs
                    if len(cheating_logs) > 50:
                        cheating_logs.pop(0)
            # Optional: Log non-cheating if needed, but user specifically asked for cheating timestamp
            # else:
            #    pass

        # Annotate
        annotated = box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated = label_annotator.annotate(scene=annotated, detections=detections)

        # Encode frame to JPEG with higher quality
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        ret, buffer = cv2.imencode('.jpg', annotated, encode_param)
        frame_bytes = buffer.tobytes()

        # Maintain frame rate
        current_time_calc = time.time()
        elapsed = current_time_calc - last_frame_time
        if elapsed < frame_delay:
            time.sleep(frame_delay - elapsed)
        last_frame_time = time.time()

        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
@login_required
def get_logs():
    return jsonify(cheating_logs)

@app.route('/start_monitoring', methods=['POST'])
@login_required
def start_monitoring():
    global monitoring_active
    monitoring_active = True
    return jsonify({"status": "started"})

@app.route('/stop_monitoring', methods=['POST'])
@login_required
def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
