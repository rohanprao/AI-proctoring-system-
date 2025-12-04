🧠 AI Proctoring System


A smart, AI-powered remote examination monitoring system designed to detect cheating behavior such as multiple-person presence, mobile phone detection, gaze tracking, absence from frame, and voice activity during an online exam.

🚀 Features
Feature	Description
🔍 Face Recognition	Detects and verifies the primary user.
🧑‍🤝‍🧑 Multi-Person Detection	Flags if more than one person appears.
👀 Eye Gaze Tracking	Tracks user eye movement to detect suspicious behavior.
📱 Object Detection (YOLO)	Detects mobile phones and forbidden items.
🎤 Voice Activity Detection	Detects talking or external conversation noise.
📝 Report Logging	Generates a timestamped log report of all violations.
📷 Live Camera Feed	Works with system webcam or video input.
🛠️ Tech Stack
Component	Technology
Language	Python
Computer Vision	OpenCV, Mediapipe, Dlib
Object Detection	YOLOv8 / MobileNet SSD
Audio Processing	PyAudio, SpeechRecognition, Whisper (optional)
UI (optional)	Streamlit / Flask
Storage	Local logs, CSV


⚙️ Installation
1️⃣ Clone the Repo
git clone https://github.com/rohanprao/AI-proctoring-system.git
cd AI-proctoring-system

2️⃣ Install Required Dependencies
pip install -r requirements.txt

3️⃣ (Optional) Download YOLO Model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

4️⃣ Run the App
python app.py

🧪 Output Example
Timestamp	Detection Event	Confidence
12:03:41	Mobile Phone Detected	92%
12:05:09	Face Not Detected	85%
12:06:43	Extra Person Detected	98%

Output is stored in:

/logs/session_logs.csv

📸 Screenshots

👉 (Add your own — placeholders below)

Live Feed	Detection Alerts	Report Output

	
	
🧭 Future Enhancements

 Browser-based proctor dashboard

 Real-time cloud sync

 Cheating risk score based on violations

 Auto suspension on repeated violations

🤝 Contributing

Pull requests are welcome!
To contribute:

Fork the repository

Create a new feature branch

Submit a PR

📜 License

This project is licensed under the MIT License.

⭐ If you like this project, don’t forget to star ⭐ the repo!
