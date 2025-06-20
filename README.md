# 🧘‍♂️ Yoga Pose Detection & Correction System

Welcome to the Yoga Pose Detection and Correction System! This project uses computer vision and machine learning to help you practice yoga safely and effectively — even without a yoga instructor.

🌟 Project Overview - 
Many beginners struggle to perform yoga poses correctly without proper guidance, which can lead to injuries or ineffective practice. Our project, Yoga Pose Detection and Correction System, helps solve this by using MediaPipe Pose and OpenCV to detect poses through a webcam and give real-time feedback. It checks the user’s posture by analyzing body landmarks and angles, compares them with correct pose data, and shows on-screen corrections if needed. The system includes two rounds of practice to help users improve and safely master each pose—without needing any extra devices or sensors.

⚙️ Methodology -
The system follows a structured approach to ensure safe and effective yoga practice:
1. The webcam captures live video as the user performs yoga poses.
2. MediaPipe Pose detects 33 key body points like shoulders, elbows, hips, knees, and ankles.
3. The system calculates joint angles to check body alignment and pose structure.
4. It compares the pose with six predefined yoga poses using angle thresholds.
5. If the pose is incorrect, on-screen feedback helps the user fix it.
6. The user must hold the correct pose until the green progress bar is full to continue.
7. After completing all six poses once, a second round starts from the first pose to ensure proper practice.
This methodology enables continuous feedback and real-time correction, allowing users to practice yoga confidently and safely without an instructor.

💡 Features -
- Real-time detection & correction (good yoga posture or not)
- Instant feedback
- Supports multiple yoga poses (custom dataset)
- User-friendly interface
