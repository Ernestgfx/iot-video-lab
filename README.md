# IoT Large-Data Video Pipeline

A Python-based automated IoT pipeline that records short video clips on one laptop, transfers them over a local network to a second laptop, and deletes the local copy only after the transfer is confirmed.

---

## System Overview

This project simulates a real-world edge device monitoring system, such as a surveillance camera that continuously sends footage to a central storage server.

**Pipeline:**

```
Record → Save Locally → Send over Network → Receive Confirmation → Delete Local File
```

| Role     | Device   | Scripts Used                  |
|----------|----------|-------------------------------|
| Sender   | Laptop A | `recorder.py` + `sender.py`   |
| Receiver | Laptop B | `receiver.py`                 |

---

## Folder Structure

```
iot_video_lab/
├── recorder.py          ← Records videos from webcam (run on Laptop A)
├── sender.py            ← Sends videos to receiver (run on Laptop A)
├── receiver.py          ← Receives and saves videos (run on Laptop B)
├── videos/              ← Temporary storage on Laptop A (auto-created)
├── received_videos/     ← Permanent storage on Laptop B (auto-created)
└── README.md
```

---

## Requirements

- Python 3.8 or higher
- OpenCV (sender/recorder only)
- Both laptops connected to the **same WiFi network**

---

## Setup Instructions

### Step 1 – Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3 and run the installer
3. **Important:** Check the box that says *"Add Python to PATH"* during installation
4. Verify the installation by opening Command Prompt and running:

```
python --version
```

You should see something like `Python 3.11.4`.

---

### Step 2 – Install OpenCV (Sender laptop only)

On **Laptop A**, open Command Prompt and run:

```
pip install opencv-python
```

Laptop B does not need OpenCV.

---

### Step 3 – Create the Folder Structure

**On Laptop A (Sender):**

Open Command Prompt and run:

```
mkdir iot_video_lab
cd iot_video_lab
mkdir videos
```

Place `recorder.py` and `sender.py` inside `iot_video_lab/`.

**On Laptop B (Receiver):**

```
mkdir iot_video_lab
cd iot_video_lab
mkdir received_videos
```

Place `receiver.py` inside `iot_video_lab/`.

---

### Step 4 – Find the Receiver IP Address

On **Laptop B**, open Command Prompt and run:

```
ipconfig
```

Look for the **IPv4 Address** under your WiFi adapter. It will look something like:

```
IPv4 Address. . . . . . . . . . . : 192.168.1.25
```

Write this down — you will need it in the next step.

---

### Step 5 – Set the Receiver IP in sender.py

Open `sender.py` on **Laptop A** and find this line near the top:

```python
RECEIVER_IP = "RECEIVER_IP"
```

Replace `RECEIVER_IP` with the actual IP address of Laptop B:

```python
RECEIVER_IP = "192.168.1.25"   # ← use your actual IP
```

Save the file.

---

## How to Run the System

### Step 1 – Start the Receiver (Laptop B)

Open Command Prompt, navigate to the project folder, and run:

```
python receiver.py
```

Leave this window open. It will wait for incoming files.

---

### Step 2 – Start the Recorder (Laptop A)

Open a **new** Command Prompt window, navigate to the project folder, and run:

```
python recorder.py
```

This will start recording a 10-second video clip every 2 minutes.

---

### Step 3 – Start the Sender (Laptop A)

Open a **second** Command Prompt window, navigate to the project folder, and run:

```
python sender.py
```

This will watch the `videos/` folder and automatically send new clips to Laptop B.

---

## Example Output Logs

### Laptop A – Recorder

```
[2025-11-12 10:00:00] [RECORDER] Initialising webcam...
[2025-11-12 10:00:01] [RECORDER] Webcam ready.
[2025-11-12 10:00:01] [RECORDER] Recording every 120 seconds (2 min).
[2025-11-12 10:00:01] [RECORDER] Press Ctrl+C to stop.

[2025-11-12 10:00:01] [RECORDER] Recording started → video_20251112_100001.mp4
[2025-11-12 10:00:11] [RECORDER] Saved: video_20251112_100001.mp4  |  Size: 842.3 KB  |  Frames: 200
[2025-11-12 10:00:11] [RECORDER] Waiting 120 seconds until next recording...
```

### Laptop A – Sender

```
[2025-11-12 10:00:05] [SENDER]   Sender started. Watching 'videos/' for new .mp4 files...
[2025-11-12 10:00:05] [SENDER]   Receiver: 192.168.1.200:5001
[2025-11-12 10:00:05] [SENDER]   Retry policy: up to 3 attempts per file

[2025-11-12 10:00:11] [SENDER]   Found 1 file(s) to send.
[2025-11-12 10:00:11] [SENDER]   Sending: video_20251112_100001.mp4  |  Size: 842.3 KB
[2025-11-12 10:00:12] [SENDER]   Transfer confirmed: video_20251112_100001.mp4  |  Time: 1.23s
[2025-11-12 10:00:12] [SENDER]   Deleted local file: video_20251112_100001.mp4
```

### Laptop B – Receiver

```
[2025-11-12 10:00:01] [RECEIVER] Receiver server started on port 5001.
[2025-11-12 10:00:01] [RECEIVER] Saving files to: C:\iot_video_lab\received_videos
[2025-11-12 10:00:01] [RECEIVER] Waiting for incoming files... (Press Ctrl+C to stop)

[2025-11-12 10:00:11] [RECEIVER] New connection from 192.168.1.14:50231
[2025-11-12 10:00:11] [RECEIVER] Incoming file: video_20251112_100001.mp4
[2025-11-12 10:00:12] [RECEIVER] Saved: video_20251112_100001.mp4  |  Size: 842.3 KB  |  Time: 1.21s
[2025-11-12 10:00:12] [RECEIVER] Sent confirmation to sender.
```

---

## Lab Report

### Roles

| Role     | Name       |
|----------|------------|
| Sender   | Ernest     |
| Receiver | Ernest VM  |

### Receiver IP Address

```
192.168.1.200
```

### Did the automated system work?

Yes. The full pipeline worked as designed:

1. `recorder.py` automatically started a new recording every 2 minutes
2. `sender.py` detected each new `.mp4` file and transferred it to the receiver
3. `receiver.py` saved each file to the `received_videos/` folder and replied with `OK`
4. The sender deleted the local copy only after receiving the `OK` confirmation

### Were files deleted only after transfer confirmation?

Yes. The sender only calls `os.remove(filepath)` inside the block that checks for the `b"OK"` response from the receiver. If the transfer fails or times out, the file is kept locally and the retry mechanism attempts to send it again.

### Problems and Fixes

**Problem 1: Connection refused error on sender**

The sender printed `CONNECTION REFUSED` when first started.

*Fix:* `receiver.py` was not running yet on Laptop B. We started the receiver first, then the sender. The issue was simply the order of operations.

---

**Problem 2: Windows Firewall blocked the connection**

After starting both scripts in the correct order, the sender kept timing out with no connection.

*Fix:* On Laptop B, we opened Windows Defender Firewall → Advanced Settings → Inbound Rules → New Rule → Port → TCP → Port 5001 → Allow the connection. After adding this rule, the transfer worked immediately.

---

**Problem 3: Wrong IP address entered in sender.py**

The sender was connecting to an old IP from a previous session. Laptop B had been reassigned a new IP by the router.

*Fix:* We ran `ipconfig` on Laptop B again and updated `RECEIVER_IP` in `sender.py` with the correct current address.

---

## Firewall Troubleshooting

If the sender cannot connect to the receiver, the Windows Firewall may be blocking port 5001.

**To open port 5001 on Laptop B (Receiver):**

1. Press `Win + S` and search for **Windows Defender Firewall**
2. Click **Advanced settings** on the left
3. Click **Inbound Rules** → then **New Rule** on the right
4. Select **Port** → click Next
5. Select **TCP**, enter `5001` → click Next
6. Select **Allow the connection** → click Next
7. Check all three boxes (Domain, Private, Public) → click Next
8. Give the rule a name, e.g. `IoT Lab Port 5001` → click Finish

---

## Learning Outcome

This lab demonstrates a complete edge IoT pipeline:

- **Edge recording** – a device captures data continuously
- **Local buffering** – files are stored temporarily until they can be sent
- **Network transfer** – data is transmitted to a central server over TCP
- **Server confirmation** – the receiver acknowledges successful storage
- **Local cleanup** – the edge device frees up storage only after confirmation

This pattern is used in real-world systems including smart surveillance cameras, industrial sensor networks, autonomous vehicle data pipelines, and remote environmental monitoring systems.
