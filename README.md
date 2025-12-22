# 🧘‍♂️ Yoga Pose Detection & Correction System

The Yoga Pose Detection and Correction System is a full-stack web application that enables users to practice yoga safely and effectively through real-time pose detection and feedback. The system is designed as a website where users interact through a browser-based interface, while the backend processes live video input to detect, analyze, and validate yoga poses using machine learning and computer vision techniques.

**📖 Project Overview -**
Many beginners struggle to maintain correct posture while practicing yoga without professional guidance. To address this challenge, we developed a web-based yoga pose correction system that works directly with a webcam. The frontend of the website provides an intuitive interface for starting sessions, viewing live pose detection, and receiving feedback. The backend, built using Python, handles pose estimation, joint angle calculation, and pose validation logic. By comparing detected body landmarks with predefined correct poses, the system delivers real-time visual feedback to help users improve posture and avoid injuries. The application includes two practice rounds to ensure users consistently perform each pose correctly, without requiring any external sensors or devices.

**⚙️ System Architecture & Methodology -**
A. Frontend (Web Interface):
- Built using HTML, CSS, and JavaScript
- Displays live webcam feed, pose status, and feedback messages
- Shows progress bar to indicate correct pose holding duration

B. Backend (Pose Processing Engine):
- Developed using Python and Flask
- Captures video frames from the webcam
- Uses MediaPipe Pose to detect 33 body landmarks
- Calculates joint angles and compares them with predefined thresholds
- Sends real-time pose validation results to the frontend

C. Practice Flow:
1. Users must hold the correct pose until the progress bar completes
2. Supports six predefined yoga poses
3. A second practice round reinforces correct posture and consistency

**🛠️ Technologies Used -**
1. Frontend: HTML, CSS, JavaScript
2. Backend: Python, Flask
3. Computer Vision & ML: MediaPipe Pose, OpenCV
4. Hardware: Webcam

**💡 Features -**
- Full-stack web-based yoga pose detection system
- Real-time pose correction and instant feedback
- Multiple yoga pose support with custom pose validation logic
- User-friendly and interactive web interface
- No external sensors or wearables required
