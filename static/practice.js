let sessionActive = false;
let statusCheckInterval = null;
let currentPoseData = null;

// small lock to avoid double-calling nextPose when a pose completes rapidly
let completionLock = false;

const welcomeScreen = document.getElementById('welcomeScreen');
const practiceScreen = document.getElementById('practiceScreen');
const completionScreen = document.getElementById('completionScreen');
const startBtn = document.getElementById('startBtn');
const endBtn = document.getElementById('endBtn');

startBtn.addEventListener('click', startSession);
endBtn.addEventListener('click', endSession);

async function startSession() {
    try {
        const response = await fetch('/api/start_session', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            welcomeScreen.style.display = 'none';
            practiceScreen.style.display = 'block';
            sessionActive = true;

            // Ensure UI round label starts at 1 and pose progress at 0
            document.getElementById('roundNumber').textContent = 1;
            document.getElementById('poseProgress').textContent = 0;

            startStatusCheck();
        }
    } catch (error) {
        console.error('Error starting session:', error);
    }
}

async function endSession() {
    if (!confirm('Are you sure you want to end this session?')) {
        return;
    }
    try {
        const response = await fetch('/api/end_session', { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            sessionActive = false;
            stopStatusCheck();
            showCompletionScreen(data.session_info);
        }
    } catch (error) {
        console.error('Error ending session:', error);
    }
}

function startStatusCheck() {
    // Slightly more restful polling but still responsive
    statusCheckInterval = setInterval(updatePoseStatus, 250);
}

function stopStatusCheck() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

async function updatePoseStatus() {
    if (!sessionActive) return;
    try {
        const response = await fetch('/api/pose_status');
        const data = await response.json();
        if (data.status === 'success') {
            currentPoseData = data.pose_status;
            updateUI(currentPoseData);

            // If completed, advance — but guard with a completion lock to avoid duplicates
            if (currentPoseData.completed && !completionLock) {
                completionLock = true;
                // small delay to avoid race conditions with backend state
                setTimeout(async () => {
                    await nextPose();
                    // release lock shortly after
                    setTimeout(() => { completionLock = false; }, 300);
                }, 80);
            }
        }
    } catch (error) {
        console.error('Error fetching pose status:', error);
    }
}

function updateUI(poseData) {
    const poseNameDisplay = document.getElementById('poseNameDisplay');
    const statusIndicator = document.getElementById('statusIndicator');
    const feedbackContent = document.getElementById('feedbackContent');
    const holdProgress = document.getElementById('holdProgress');
    const holdBarFill = document.getElementById('holdBarFill');
    const holdText = document.getElementById('holdText');
    const referenceImage = document.getElementById('referenceImage');
    const transitionMessage = document.getElementById('transitionMessage');
    const meditationOverlay = document.getElementById('meditationOverlay');
    const breathCycle = document.getElementById('breathCycle');
    const meditationBarFill = document.getElementById('meditationBarFill');
    const meditationText = document.getElementById('meditationText');
    const roundNumber = document.getElementById('roundNumber');
    const poseProgress = document.getElementById('poseProgress');

    poseNameDisplay.textContent = poseData.pose_name;

    // show the current active round number (backend tracks completed rounds separately)
    roundNumber.textContent = poseData.round_number;

    // Only set the *current pose index number* here — the HTML contains the static "/ 8 poses".
    poseProgress.textContent = poseData.current_pose_index + 1;

    if (poseData.is_transition) {
        referenceImage.style.display = 'none';
        transitionMessage.style.display = 'block';
        transitionMessage.textContent = poseData.pose_name;
        holdProgress.style.display = 'none';
        meditationOverlay.style.display = 'none';

        statusIndicator.textContent = 'TRANSITION';
        statusIndicator.className = 'status-indicator';

        feedbackContent.className = 'feedback-content';
        feedbackContent.textContent = 'Get ready for the next pose...';
    } else if (poseData.is_meditation) {
        if (poseData.pose_image) {
            referenceImage.src = `/static/images/${poseData.pose_image}`;
            referenceImage.style.display = 'block';
        }
        transitionMessage.style.display = 'none';
        holdProgress.style.display = 'none';

        if (poseData.meditation_progress !== undefined) {
            meditationOverlay.style.display = 'block';
            breathCycle.textContent = poseData.breath_cycle;

            // Scale the meditation bar down so it doesn't cover the feed
            // (use a smaller max width visually so it appears compact)
            const scaled = Math.min(poseData.meditation_progress * 60, 60); // 0..60%
            meditationBarFill.style.width = `${scaled}%`;

            meditationText.textContent = `${poseData.meditation_remaining}s remaining`;

            statusIndicator.textContent = 'MEDITATION';
            statusIndicator.className = 'status-indicator status-valid';

            feedbackContent.className = 'feedback-content valid';
            feedbackContent.textContent = `Follow the breathing guide. ${poseData.meditation_remaining} seconds remaining.`;
        } else {
            meditationOverlay.style.display = 'none';
        }
    } else {
        if (poseData.pose_image) {
            referenceImage.src = `/static/images/${poseData.pose_image}`;
            referenceImage.style.display = 'block';
        } else {
            referenceImage.style.display = 'none';
        }
        transitionMessage.style.display = 'none';
        meditationOverlay.style.display = 'none';

        if (poseData.pose_valid) {
            statusIndicator.textContent = 'HOLDING';
            statusIndicator.className = 'status-indicator status-holding';

            holdProgress.style.display = 'block';
            const progress = (poseData.hold_time / poseData.hold_duration) * 100;
            holdBarFill.style.width = `${Math.min(progress, 100)}%`;
            holdText.textContent = `Hold: ${poseData.hold_time.toFixed(1)}s / ${poseData.hold_duration.toFixed(1)}s`;

            feedbackContent.className = 'feedback-content valid';
            feedbackContent.textContent = '✓ Great! Hold this pose...';
        } else {
            statusIndicator.textContent = 'ADJUST POSE';
            statusIndicator.className = 'status-indicator status-invalid';

            holdProgress.style.display = 'none';

            feedbackContent.className = 'feedback-content';
            if (poseData.feedback && poseData.feedback.length > 0) {
                feedbackContent.innerHTML = '<strong>Adjustments needed:</strong><ul>' +
                    poseData.feedback.map(f => `<li>${f}</li>`).join('') +
                    '</ul>';
            } else {
                feedbackContent.textContent = 'Position yourself to match the reference pose';
            }
        }
    }
}

async function nextPose() {
    try {
        const response = await fetch('/api/next_pose', { method: 'POST' });
        const data = await response.json();

        if (data.status === 'round_complete') {
            // Show modal with the completed round number from backend.
            // Backend returns the "upcoming round number" (i.e., completed round number),
            // so we display that and allow user to confirm continuing.
            showRoundCompleteModal(data.round);
            return;
        }

        // otherwise just continue (UI will update next poll)
    } catch (error) {
        console.error('Error advancing to next pose:', error);
    }
}

function showRoundCompleteModal(completedRoundNumber) {
    const modal = document.getElementById('roundCompleteModal');
    const title = document.getElementById('roundCompleteTitle');
    const continueBtn = document.getElementById('continueRoundBtn');
    const endBtn = document.getElementById('endRoundBtn');

    // The backend sent `data.round` (upcoming round index / completed round number).
    title.textContent = `🎉 Round ${completedRoundNumber} Complete!`;

    modal.style.display = 'flex';

    continueBtn.onclick = async () => {
        modal.style.display = 'none';

        // Tell backend to increment the stored completed-rounds count.
        await fetch('/api/continue_round', { method: 'POST' });

        // Active round should now be completedRoundNumber + 1
        document.getElementById('roundNumber').textContent = completedRoundNumber + 1;

        // Reset pose progress UI for new round start (first pose)
        document.getElementById('poseProgress').textContent = 1;
    };

    endBtn.onclick = async () => {
        modal.style.display = 'none';

        // Ensure backend counts the completed round before ending session
        await fetch('/api/continue_round', { method: 'POST' });

        // Then end the session, which will return the updated rounds_completed value
        await endSession();
    };
}

function showCompletionScreen(sessionInfo) {
    practiceScreen.style.display = 'none';
    completionScreen.style.display = 'flex';

    document.getElementById('totalRounds').textContent = sessionInfo.rounds_completed;
    document.getElementById('totalPoses').textContent = sessionInfo.poses_completed;
    document.getElementById('sessionDuration').textContent = sessionInfo.duration_minutes;
}

window.addEventListener('beforeunload', (e) => {
    if (sessionActive) {
        e.preventDefault();
        e.returnValue = '';
    }
});
