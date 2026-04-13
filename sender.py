"""
sender.py - Automated File Sender with Retry Logic
IoT Video Pipeline Lab

This script watches the 'videos/' folder for new .mp4 files,
sends each one to the receiver laptop over the network,
waits for an OK confirmation, and deletes the local file only
after a confirmed successful transfer.

Features:
  - Prints file size before sending
  - Prints transfer time after sending
  - Retries failed transfers up to MAX_RETRIES times
  - Only deletes local file after confirmed transfer

Run this on Laptop A (Sender).
"""

import socket
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION – Change RECEIVER_IP to Laptop B's IP address
# ─────────────────────────────────────────────
RECEIVER_IP    = "192.168.1.200"  # Laptop B (Ernest VM) receiver IP
PORT           = 5001            # Must match receiver.py
VIDEO_FOLDER   = "videos"        # Folder to watch for new videos
CHECK_INTERVAL = 5               # How often to check for new files (seconds)
MAX_RETRIES    = 3               # Number of times to retry a failed transfer
RETRY_DELAY    = 5               # Seconds to wait between retries
# ─────────────────────────────────────────────

def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [SENDER]   {message}")

def format_size(bytes_size):
    """Convert bytes to a human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"

def send_file(filepath):
    """
    Attempt to send a single file to the receiver.
    Returns True if transfer was confirmed, False otherwise.
    """
    filename  = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    log(f"Sending: {filename}  |  Size: {format_size(file_size)}")

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(30)  # 30-second timeout for socket operations
        client.connect((RECEIVER_IP, PORT))

        # ── Step 1: Send filename ──────────────────────────────────────────
        client.sendall(filename.encode())
        response = client.recv(1024)

        if response != b"FILENAME_OK":
            log(f"FAILED: Receiver did not acknowledge filename for {filename}")
            client.close()
            return False

        # ── Step 2: Send file data ─────────────────────────────────────────
        transfer_start = time.time()

        with open(filepath, "rb") as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                client.sendall(data)

        client.sendall(b"EOF")  # Signal end of file

        # ── Step 3: Wait for confirmation ──────────────────────────────────
        response = client.recv(1024)
        client.close()

        transfer_time = time.time() - transfer_start

        if response == b"OK":
            log(f"Transfer confirmed: {filename}  |  Time: {transfer_time:.2f}s")

            # ── Step 4: Delete local file ONLY after confirmation ──────────
            os.remove(filepath)
            log(f"Deleted local file: {filename}\n")
            return True
        else:
            log(f"FAILED: Receiver sent unexpected response for {filename}: {response}")
            return False

    except socket.timeout:
        log(f"TIMEOUT: No response from receiver for {filename}")
        return False
    except ConnectionRefusedError:
        log(f"CONNECTION REFUSED: Is receiver.py running on {RECEIVER_IP}:{PORT}?")
        return False
    except Exception as e:
        log(f"ERROR sending {filename}: {e}")
        return False

def send_with_retry(filepath):
    """
    Try to send a file up to MAX_RETRIES times.
    Returns True if eventually successful, False if all retries exhausted.
    """
    filename = os.path.basename(filepath)

    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            log(f"Retry {attempt}/{MAX_RETRIES} for {filename} (waiting {RETRY_DELAY}s)...")
            time.sleep(RETRY_DELAY)

        success = send_file(filepath)
        if success:
            return True

        log(f"Attempt {attempt}/{MAX_RETRIES} failed for {filename}.")

    log(f"GIVING UP on {filename} after {MAX_RETRIES} failed attempts. Will retry next cycle.\n")
    return False

# ─────────────────────────────────────────────
# MAIN – Start the sender loop
# ─────────────────────────────────────────────
os.makedirs(VIDEO_FOLDER, exist_ok=True)

log(f"Sender started. Watching '{VIDEO_FOLDER}/' for new .mp4 files...")
log(f"Receiver: {RECEIVER_IP}:{PORT}")
log(f"Retry policy: up to {MAX_RETRIES} attempts per file")
log("Press Ctrl+C to stop.\n")

try:
    while True:
        # Find all .mp4 files in the videos folder, sorted by name (oldest first)
        files = sorted(
            f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")
        )

        if files:
            log(f"Found {len(files)} file(s) to send.")

        for filename in files:
            filepath = os.path.join(VIDEO_FOLDER, filename)

            # Skip if file no longer exists (already deleted by a previous iteration)
            if not os.path.exists(filepath):
                continue

            send_with_retry(filepath)

        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    log("Sender stopped by user (Ctrl+C).")
