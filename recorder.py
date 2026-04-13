"""
recorder.py - Automated Video Recorder
IoT Video Pipeline Lab

This script continuously records short video clips from the webcam
every 2 minutes and saves them to the local 'videos/' folder.
The sender.py script will pick them up and transfer them automatically.

Run this on Laptop A (Sender).
"""

import cv2
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION – Change these if needed
# ─────────────────────────────────────────────
SAVE_FOLDER     = "videos"        # Local folder to save recorded videos
RECORD_SECONDS  = 10              # How long each video clip should be (seconds)
INTERVAL_SECONDS = 120            # How long to wait between recordings (120 = 2 minutes)
FPS             = 20.0            # Frames per second
FRAME_WIDTH     = 640             # Video width in pixels
FRAME_HEIGHT    = 480             # Video height in pixels
# ─────────────────────────────────────────────

def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [RECORDER] {message}")

def record_clip():
    """Record a single video clip and save it to the videos folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"video_{timestamp}.mp4"
    filepath  = os.path.join(SAVE_FOLDER, filename)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out    = cv2.VideoWriter(filepath, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    log(f"Recording started → {filename}")
    start_time = time.time()

    frames_written = 0
    while time.time() - start_time < RECORD_SECONDS:
        ret, frame = cap.read()
        if not ret:
            log("WARNING: Could not read frame from webcam. Skipping.")
            break
        out.write(frame)
        frames_written += 1

    out.release()

    # Calculate and display file size
    if os.path.exists(filepath):
        file_size_kb = os.path.getsize(filepath) / 1024
        log(f"Saved: {filename}  |  Size: {file_size_kb:.1f} KB  |  Frames: {frames_written}")
    else:
        log(f"ERROR: File was not saved: {filepath}")

# ─────────────────────────────────────────────
# MAIN – Start the recorder loop
# ─────────────────────────────────────────────
os.makedirs(SAVE_FOLDER, exist_ok=True)

log("Initialising webcam...")
cap = cv2.VideoCapture(0)  # 0 = default webcam

if not cap.isOpened():
    log("ERROR: Could not open webcam. Make sure a webcam is connected.")
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

log("Webcam ready.")
log(f"Recording every {INTERVAL_SECONDS} seconds ({INTERVAL_SECONDS // 60} min).")
log("Press Ctrl+C to stop.\n")

try:
    while True:
        record_clip()
        log(f"Waiting {INTERVAL_SECONDS} seconds until next recording...\n")
        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    log("Recorder stopped by user (Ctrl+C).")

finally:
    cap.release()
    log("Webcam released. Goodbye.")
