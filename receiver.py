"""
receiver.py - File Receiver Server
IoT Video Pipeline Lab

This script runs as a server on Laptop B (Receiver).
It listens for incoming video files from the sender laptop,
saves each file to 'received_videos/', and sends back an OK
confirmation so the sender knows it is safe to delete its local copy.

Features:
  - Saves received files with original filenames
  - Prints file size and receive time after each transfer
  - Keeps running indefinitely to handle multiple files

Run this on Laptop B (Receiver).
Start this BEFORE running recorder.py or sender.py on Laptop A.
"""

import socket
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
HOST        = "0.0.0.0"           # Listen on all network interfaces
PORT        = 5001                # Must match sender.py
SAVE_FOLDER = "received_videos"   # Folder to save received files
# ─────────────────────────────────────────────

def log(message):
    """Print a timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [RECEIVER] {message}")

def format_size(bytes_size):
    """Convert bytes to a human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"

def handle_connection(conn, addr):
    """Handle a single incoming file transfer from the sender."""
    log(f"New connection from {addr[0]}:{addr[1]}")

    # ── Step 1: Receive filename ───────────────────────────────────────────
    filename = conn.recv(1024).decode().strip()

    if not filename:
        log("ERROR: Received empty filename. Closing connection.")
        conn.close()
        return

    log(f"Incoming file: {filename}")
    conn.sendall(b"FILENAME_OK")

    # ── Step 2: Receive file data until EOF marker ─────────────────────────
    save_path    = os.path.join(SAVE_FOLDER, filename)
    receive_start = time.time()
    bytes_received = 0

    with open(save_path, "wb") as f:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            if data.endswith(b"EOF"):
                # Write everything before the EOF marker
                f.write(data[:-3])
                bytes_received += len(data) - 3
                break
            f.write(data)
            bytes_received += len(data)

    receive_time = time.time() - receive_start
    file_size    = os.path.getsize(save_path)

    log(f"Saved: {filename}  |  Size: {format_size(file_size)}  |  Time: {receive_time:.2f}s")

    # ── Step 3: Send OK confirmation ──────────────────────────────────────
    conn.sendall(b"OK")
    log(f"Sent confirmation to sender.\n")
    conn.close()

# ─────────────────────────────────────────────
# MAIN – Start the receiver server
# ─────────────────────────────────────────────
os.makedirs(SAVE_FOLDER, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow quick restart
server.bind((HOST, PORT))
server.listen(5)

log(f"Receiver server started on port {PORT}.")
log(f"Saving files to: {os.path.abspath(SAVE_FOLDER)}")
log("Waiting for incoming files... (Press Ctrl+C to stop)\n")

try:
    while True:
        conn, addr = server.accept()
        handle_connection(conn, addr)

except KeyboardInterrupt:
    log("Receiver stopped by user (Ctrl+C).")

finally:
    server.close()
    log("Server socket closed. Goodbye.")
