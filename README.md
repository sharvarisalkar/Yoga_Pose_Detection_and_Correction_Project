# 🧘‍♂️ Yoga_Pose_Detection_and_Correction_Project

Welcome to the Yoga Pose Detection and Correction System! This project uses computer vision and machine learning to help you practice yoga safely and effectively — even without a yoga instructor.

🌟 Project Overview -
Many yoga practitioners, especially beginners, face challenges in performing poses correctly without guidance from trained instructors. This can lead to ineffective practice or even injuries, particularly in home or virtual environments where in-person classes are unavailable. To address this, our project—Yoga Pose Detection and Correction System—uses computer vision and machine learning to provide real-time feedback and ensure safe, effective yoga practice at home. Leveraging MediaPipe Pose and OpenCV, the system detects specific yoga poses through a webcam, analyzes key body landmarks and joint angles, and compares them to a dataset of correct poses. If the user’s posture is not aligned properly, the system delivers immediate corrective feedback on-screen. The approach includes two rounds of practice, ensuring mastery of each pose while fostering safe yoga habits without the need for additional sensors or advanced devices.

⚙️ Methodology -
The system follows a structured approach to ensure safe and effective yoga practice:
1. The webcam captures a live video stream using laptop as the user performs yoga poses.
2. MediaPipe Pose extracts 33 key body landmarks from each frame, including shoulders, elbows, hips, knees, and ankles.
3. The system calculates the angles between these key joints to assess body alignment and posture structure.
4. The detected pose is compared with a dataset of six yoga poses (Downward Dog, Goddess, Lotus, Butterfly, Easy Pose, etc.), using angle thresholds to determine correctness.
5. If the pose does not meet the defined angle thresholds, it is labeled as incorrect, and the system displays on-screen corrective feedback to help the user adjust their posture.
6. The user must hold the correct posture until the system’s pose progress indicator (a green load bar) is fully completed. Only then does the system move on to the next pose.
7. After the user successfully completes all six poses in the first round, the system automatically begins a second round, starting again with the first pose. This ensures thorough practice and mastery of each pose.
This methodology enables continuous feedback and real-time correction, allowing users to practice yoga confidently and safely without an instructor.

💡 Features -
1. Real-time detection
2. Instant feedback
3. Supports multiple yoga poses
4. User-friendly interface


