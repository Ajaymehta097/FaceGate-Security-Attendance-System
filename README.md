# FaceGate — Classroom Face Recognition Security System

A Python-based security system that uses live face recognition via webcam.
Only registered people are granted access. Includes a full **Web UI** accessible from any browser.

---

## 📁 Project Structure

```
face_security/
├── main.py                  ← CLI version (terminal)
├── server.py                ← Web UI version (run this for browser)
├── requirements.txt
├── templates/
│   └── index.html           ← Web UI frontend
├── known_faces/             ← Auto-saved face images
├── data/
│   └── face_database.pkl    ← Encoded face data
├── logs/
│   └── access_log.json      ← All access events
└── utils/
    ├── __init__.py
    ├── database.py          ← Face data storage
    ├── logger.py            ← Access log handler
    └── display.py           ← CLI formatting
```

---

## ⚙️ Installation

### Step 1 — Install dependencies

**Windows:**
```bash
pip install cmake
pip install dlib
pip install face-recognition opencv-python numpy flask flask-cors
```

**Linux/macOS:**
```bash
sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev  # Linux only
pip install face-recognition opencv-python numpy flask flask-cors
```

**macOS (Homebrew):**
```bash
brew install cmake
pip install face-recognition opencv-python numpy flask flask-cors
```

---

## ▶️ Run

### Option 1 — Web UI (Recommended) 🌐
```bash
python server.py
```
Then open browser: **http://localhost:5000**

### Option 2 — Terminal / CLI
```bash
python main.py
```

---

## 🌐 Web UI Pages

| Page | Description |
|------|-------------|
| **Live Scanner** | Live camera feed — shows `YOU CAN ENTER` or `YOU CANNOT ENTER` on screen |
| **Register Person** | Fill name, ID, role + capture face from webcam |
| **Students DB** | All registered students with photos |
| **Access Logs** | Full history table — granted/denied, confidence %, timestamp |
| **Live Activity Feed** | Real-time sidebar showing every detection |

---

## 🎯 CLI Menu Options (main.py)

| Option | Description |
|--------|-------------|
| **[1] Register** | Opens webcam → Press SPACE to capture face → Saved to database |
| **[2] Scanner**  | Live webcam gate — shows GREEN for authorized, RED for unknown |
| **[3] View DB**  | Lists all registered people |
| **[4] View Logs**| Shows access history (granted/denied) with timestamps |
| **[5] Delete**   | Remove a person by their ID |

---

## 🔧 Configuration

Edit these variables in `server.py` (Web) or `main.py` (CLI):

| Variable | Default | Description |
|----------|---------|-------------|
| `TOLERANCE` | `0.5` | Match strictness — lower = stricter (try 0.4–0.6) |
| `CAMERA_INDEX` | `0` | 0 = default webcam, 1 = second/USB camera |
| `SCAN_INTERVAL` | `1.5` | Seconds between recognition attempts |
| `FRAME_SCALE` | `0.5` | Processing resolution (0.5 = half size, faster) |

---

## 📸 Scanner Display

- 🟢 **YOU CAN ENTER** → Authorized person, access granted
- 🔴 **YOU CANNOT ENTER** → Unknown face, access denied
- 🟡 **Yellow box** → Detecting, not yet matched

---

## 📋 Access Log Sample (`logs/access_log.json`)

```json
[
  {
    "timestamp": "2024-11-15 09:32:11",
    "name": "Amit Sharma",
    "id": "CS2024001",
    "role": "student",
    "status_label": "GRANTED",
    "confidence": 91.3
  },
  {
    "timestamp": "2024-11-15 09:33:05",
    "name": "UNKNOWN",
    "id": "—",
    "role": "—",
    "status_label": "DENIED",
    "confidence": 0
  }
]
```

---

## 💡 Tips

- **Good lighting** dramatically improves accuracy
- **Register multiple angles**: Register the same person 2–3 times (different angles/lighting) for better recognition
- **Adjust tolerance**: If false positives, lower `TOLERANCE` to `0.4`. If authorized people not recognized, raise to `0.6`
- **Multiple cameras**: Change `CAMERA_INDEX = 1` to use a USB webcam instead of built-in
- **Both versions share the same database** — register via Web UI, works in CLI too and vice versa

---

## 🔒 Security Note

This system is designed for educational/classroom use. For production security, consider pairing with hardware locks, door controllers (e.g., Raspberry Pi GPIO), and encrypted storage.