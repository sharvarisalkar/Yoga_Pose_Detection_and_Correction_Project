import cv2
import mediapipe as mp
import numpy as np
import time

class YogaPoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Pose list - transitions flagged, real poses flagged
        self.poses = [
            {"name": "Stand Up", "image": None, "completed": False, "is_transition": True},
            {"name": "Tree Pose", "image": "tree_pose.jpg", "completed": False, "is_real_pose": True},
            {"name": "Downward Dog Pose", "image": "downward_dog.jpg", "completed": False, "is_real_pose": True},
            {"name": "Goddess Pose", "image": "goddess_pose.jpg", "completed": False, "is_real_pose": True},
            {"name": "Sit Down", "image": None, "completed": False, "is_transition": True},
            {"name": "Lotus Pose", "image": "lotus_pose.jpg", "completed": False, "is_real_pose": True},
            {"name": "Butterfly Pose", "image": "butterfly_pose.jpg", "completed": False, "is_real_pose": True},
            {"name": "Easy Pose", "image": "easy_pose.jpg", "completed": False, "is_meditation": True, "is_real_pose": True}
        ]

        self.current_pose_index = 0
        self.round_number = 1
        self.pose_hold_start = 0
        self.pose_hold_duration = 3.0

        # Meditation variables
        self.meditation_start = 0
        self.meditation_duration = 30  # one-time 30s meditation per round
        self.breath_cycle = "Breathe In"
        self.meditation_done_for_round = False  # ensure single meditation per round

        # for counting only when a real pose completes
        self.last_pose_completed_count = 0

    def calculate_angle(self, a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        ba = a - b
        bc = c - b
        denom = (np.linalg.norm(ba) * np.linalg.norm(bc))
        if denom == 0:
            return 0.0
        cosine_angle = np.dot(ba, bc) / denom
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine_angle))
        return angle

    def check_pose(self, landmarks, target_pose):
        feedback = []
        all_correct = True

        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        left_elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

        # Tree Pose
        if target_pose == "Tree Pose":
            foot_on_thigh = ((left_ankle.y < left_knee.y and abs(left_ankle.x - right_hip.x) < 0.15)) or \
                            (right_ankle.y < right_knee.y and abs(right_ankle.x - left_hip.x) < 0.15)
            if not foot_on_thigh:
                feedback.append("Place foot on opposite thigh")
                all_correct = False

            hands_together = (abs(left_wrist.x - right_wrist.x) < 0.1 and
                              abs(left_wrist.y - right_wrist.y) < 0.1 and
                              left_wrist.y < nose.y)
            if not hands_together:
                feedback.append("Bring hands together above head")
                all_correct = False

        # Downward Dog Pose
        elif target_pose == "Downward Dog Pose":
            hips_raised = (left_hip.y < left_shoulder.y) and (right_hip.y < right_shoulder.y)
            if not hips_raised:
                feedback.append("Raise your hips higher")
                all_correct = False

            legs_straight = (left_knee_angle > 160) and (right_knee_angle > 160)
            if not legs_straight:
                feedback.append("Straighten your legs")
                all_correct = False

        # Goddess Pose
        elif target_pose == "Goddess Pose":
            knees_bent = (left_knee_angle < 120) and (right_knee_angle < 120)
            knees_wide = abs(left_knee.x - right_knee.x) > abs(left_hip.x - right_hip.x)
            if not knees_bent:
                feedback.append("Bend your knees more")
                all_correct = False
            if not knees_wide:
                feedback.append("Widen your stance")
                all_correct = False

            arms_bent = (left_elbow_angle < 90) and (right_elbow_angle < 90)
            arms_height = abs(left_wrist.y - left_shoulder.y) < 0.15
            if not arms_bent:
                feedback.append("Bend your elbows")
                all_correct = False
            if not arms_height:
                feedback.append("Raise arms to shoulder height")
                all_correct = False

        # Lotus Pose
        elif target_pose == "Lotus Pose":
            left_foot_on_right_thigh = (left_ankle.y < right_knee.y and abs(left_ankle.x - right_hip.x) < 0.15)
            right_foot_on_left_thigh = (right_ankle.y < left_knee.y and abs(right_ankle.x - left_hip.x) < 0.15)

            if not (left_foot_on_right_thigh or right_foot_on_left_thigh):
                feedback.append("Place at least one foot on opposite thigh")
                all_correct = False

            spine_straight = (abs(left_shoulder.x - left_hip.x) < 0.1) and (abs(right_shoulder.x - right_hip.x) < 0.1)
            if not spine_straight:
                feedback.append("Keep spine straight")
                all_correct = False

            hands_on_knees = ((abs(left_wrist.x - left_knee.x) < 0.15 and abs(left_wrist.y - left_knee.y) < 0.15) and
                              (abs(right_wrist.x - right_knee.x) < 0.15 and abs(right_wrist.y - right_knee.y) < 0.15))

            hands_prayer = (abs(left_wrist.x - right_wrist.x) < 0.1 and abs(left_wrist.y - right_wrist.y) < 0.1)

            if not (hands_on_knees or hands_prayer):
                feedback.append("Place hands on knees or in prayer position")
                all_correct = False

        # Butterfly Pose
        elif target_pose == "Butterfly Pose":
            knees_bent = (left_knee_angle < 90) and (right_knee_angle < 90)
            feet_together = abs(left_ankle.x - right_ankle.x) < 0.1

            if not knees_bent:
                feedback.append("Bend your knees more")
                all_correct = False
            if not feet_together:
                feedback.append("Bring feet together")
                all_correct = False

            hands_on_feet = ((abs(left_wrist.x - left_ankle.x) < 0.15 and abs(left_wrist.y - left_ankle.y) < 0.15)) and \
                            ((abs(right_wrist.x - right_ankle.x) < 0.15 and abs(right_wrist.y - right_ankle.y) < 0.15))

            if not hands_on_feet:
                feedback.append("Hold your feet with hands")
                all_correct = False

        # Easy Pose (meditation)
        elif target_pose == "Easy Pose":
            legs_crossed = (left_knee.x > right_ankle.x) and (right_knee.x < left_ankle.x)
            if not legs_crossed:
                feedback.append("Cross your legs comfortably")
                all_correct = False

            spine_straight = (abs(left_shoulder.x - left_hip.x) < 0.1) and (abs(right_shoulder.x - right_hip.x) < 0.1)
            if not spine_straight:
                feedback.append("Keep spine straight")
                all_correct = False

        return all_correct, feedback

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        current = self.poses[self.current_pose_index]
        pose_valid = False
        feedback = []
        skeleton_color = (0, 0, 255)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            pose_valid, feedback = self.check_pose(landmarks, current['name'])

            skeleton_color = (0, 255, 0) if pose_valid else (0, 0, 255) #green, red
            if pose_valid and self.pose_hold_start == 0:
                self.pose_hold_start = time.time()
            elif not pose_valid:
                self.pose_hold_start = 0

            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
            )

        hold_time = time.time() - self.pose_hold_start if self.pose_hold_start > 0 else 0

        status = {
            "pose_name": current['name'],
            "pose_valid": pose_valid,
            "feedback": feedback,
            "hold_time": hold_time,
            "hold_duration": self.pose_hold_duration,
            "current_pose_index": self.current_pose_index,
            "total_poses": len(self.poses),
            "round_number": self.round_number,
            "is_transition": current.get("is_transition", False),
            "is_meditation": current.get("is_meditation", False),
            "pose_image": current.get("image"),
            "completed": False
        }

        # Meditation (one time per round)
        if current.get("is_meditation") and pose_valid and not self.meditation_done_for_round:
            if self.meditation_start == 0:
                self.meditation_start = time.time()
                # ensure 30-second meditation per round
                self.meditation_duration = 30

            elapsed = time.time() - self.meditation_start
            remaining = max(0, self.meditation_duration - elapsed)

            if elapsed < 10:
                self.breath_cycle = "Breathe In"
            elif elapsed < 20:
                self.breath_cycle = "Breathe Out"
            else:
                self.breath_cycle = "Relax"

            progress = elapsed / self.meditation_duration
            status["meditation_progress"] = progress
            status["meditation_remaining"] = int(remaining)
            status["breath_cycle"] = self.breath_cycle

            if elapsed >= self.meditation_duration:
                status["completed"] = True
                self.meditation_start = 0
                self.meditation_done_for_round = True

        elif pose_valid and hold_time >= self.pose_hold_duration:
            status["completed"] = True

        return frame, status

    def next_pose(self):
        """
        Advance to next pose. Returns (round_completed: bool, pose_completed_count: int)
        pose_completed_count is 1 only if the pose just completed is a 'real' pose (is_real_pose True).
        """
        current_pose = self.poses[self.current_pose_index]
        self.last_pose_completed_count = 0

        # Count only real poses
        if not current_pose.get("completed", False) and current_pose.get("is_real_pose", False):
            self.last_pose_completed_count = 1

        # mark done
        current_pose["completed"] = True

        # advance
        self.current_pose_index += 1
        self.pose_hold_start = 0
        self.meditation_start = 0

        # if finished round
        if self.current_pose_index >= len(self.poses):
            # reset index and pose completed flags for next round
            self.current_pose_index = 0
            for p in self.poses:
                p["completed"] = False
            # reset meditation flag (so next round will have meditation again)
            self.meditation_done_for_round = False
            # increment round_number on the server side only when user confirms — we return round_complete here
            return True, self.last_pose_completed_count

        return False, self.last_pose_completed_count

    def get_progress(self):
        completed = sum(1 for p in self.poses if p.get("completed", False))
        return {
            "completed": completed,
            "total": len(self.poses),
            "round": self.round_number,
            "current_pose": self.poses[self.current_pose_index]["name"]
        }

    def reset_session(self):
        self.current_pose_index = 0
        self.round_number = 1
        self.pose_hold_start = 0
        self.meditation_start = 0
        self.meditation_done_for_round = False
        for p in self.poses:
            p["completed"] = False
