from flask import Flask, render_template, Response, jsonify, request
import cv2
import json
import os
from datetime import datetime
from pose_detector import YogaPoseDetector

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'yoga-pose-detector-secret-key')

detector = None
camera = None
session_data = {
    'start_time': None,
    'poses_completed': 0,
    'rounds_completed': 0,
    'session_active': False
}

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None

def load_session_history():
    history_file = 'data/session_history.json'
    try:
        with open(history_file, 'r') as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except FileNotFoundError:
        return []

def save_session_history(session_info):
    history_file = 'data/session_history.json'
    history = load_session_history()
    history.append(session_info)
    if len(history) > 50:
        history = history[-50:]
    os.makedirs('data', exist_ok=True)
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/practice')
def practice():
    return render_template('practice.html')

@app.route('/history')
def history():
    session_history = load_session_history()
    return render_template('history.html', sessions=session_history)

@app.route('/api/start_session', methods=['POST'])
def start_session():
    global detector, session_data
    detector = YogaPoseDetector()
    session_data = {
        'start_time': datetime.now().isoformat(),
        'poses_completed': 0,
        'rounds_completed': 0,
        'session_active': True
    }
    return jsonify({'status': 'success', 'message': 'Session started'})

@app.route('/api/end_session', methods=['POST'])
def end_session():
    global detector, session_data
    if session_data['session_active']:
        end_time = datetime.now().isoformat()
        start_time = datetime.fromisoformat(session_data['start_time'])
        duration = (datetime.now() - start_time).total_seconds()
        session_info = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_minutes': round(duration / 60, 1),
            'poses_completed': session_data['poses_completed'],
            'rounds_completed': session_data['rounds_completed']
        }
        save_session_history(session_info)
        session_data['session_active'] = False
        detector = None
        release_camera()
        return jsonify({'status': 'success', 'session_info': session_info})
    return jsonify({'status': 'error', 'message': 'No active session'})

@app.route('/api/next_pose', methods=['POST'])
def next_pose():
    global detector, session_data
    if detector:
        round_completed, pose_completed_count = detector.next_pose()
        # Only count 'real' poses (detector provides pose_completed_count)
        session_data['poses_completed'] += pose_completed_count

        if round_completed:
            # don't increment rounds here — wait for explicit user confirmation
            upcoming_round_number = session_data['rounds_completed'] + 1
            return jsonify({
                'status': 'round_complete',
                'round': upcoming_round_number
            })

        return jsonify({
            'status': 'success',
            'pose_completed': pose_completed_count == 1
        })

    return jsonify({'status': 'error', 'message': 'No active detector'})

@app.route('/api/continue_round', methods=['POST'])
def continue_round():
    """
    Called when the user chooses to continue to the next round (or
    when user chooses 'End Session' from the round modal — we still
    count the completed round first).
    """
    global session_data
    session_data['rounds_completed'] += 1
    return jsonify({'status': 'success', 'rounds_completed': session_data['rounds_completed']})

@app.route('/api/status')
def get_status():
    global detector
    if detector:
        progress = detector.get_progress()
        return jsonify({
            'status': 'active',
            'progress': progress,
            'session_data': session_data
        })
    return jsonify({'status': 'inactive'})

def generate_frames():
    global detector
    camera = get_camera()
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)
        if detector:
            frame, status = detector.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/pose_status')
def pose_status():
    global detector
    if detector and session_data['session_active']:
        camera = get_camera()
        success, frame = camera.read()
        if success:
            frame = cv2.flip(frame, 1)
            _, status = detector.process_frame(frame)
            return jsonify({
                'status': 'success',
                'pose_status': status
            })
    return jsonify({'status': 'inactive'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
