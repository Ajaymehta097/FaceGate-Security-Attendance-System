"""
FaceGate - Classroom Face Recognition Security System
======================================================
Author: FaceGate Security
Usage:  python main.py

Modes:
  1. Register Mode  - Add new students/authorized persons
  2. Scanner Mode   - Live recognition gate (camera)
  3. View Database  - Show all registered people
  4. View Logs      - Show access history
"""

import cv2
import face_recognition
import numpy as np
import os
import json
import time
import datetime
import pickle
from utils.database import Database
from utils.logger import AccessLogger
from utils.display import Display

# ─── Config ───────────────────────────────────────────────────────────────────
KNOWN_FACES_DIR = "known_faces"
DB_FILE         = "data/face_database.pkl"
LOG_FILE        = "logs/access_log.json"
TOLERANCE       = 0.5        # Lower = stricter match (0.4–0.6 recommended)
FRAME_SCALE     = 0.5        # Downscale for speed
CAMERA_INDEX    = 0
SCAN_INTERVAL   = 1.5        # Seconds between recognition attempts
MIN_FACE_SIZE   = 80         # Pixels — ignore tiny faces

# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    db     = Database(DB_FILE)
    logger = AccessLogger(LOG_FILE)
    disp   = Display()

    while True:
        disp.banner()
        print("  [1]  Register New Person")
        print("  [2]  Start Security Scanner")
        print("  [3]  View Registered Database")
        print("  [4]  View Access Logs")
        print("  [5]  Delete a Person")
        print("  [0]  Exit\n")
        choice = input("  → Select option: ").strip()

        if choice == "1":
            register_person(db, disp)
        elif choice == "2":
            run_scanner(db, logger, disp)
        elif choice == "3":
            db.print_all()
        elif choice == "4":
            logger.print_logs()
        elif choice == "5":
            delete_person(db, disp)
        elif choice == "0":
            print("\n  [SYSTEM] Shutting down FaceGate. Goodbye.\n")
            break
        else:
            print("\n  [!] Invalid option.\n")


# ─── Register New Person ───────────────────────────────────────────────────────
def register_person(db: "Database", disp: "Display"):
    disp.section("REGISTER NEW PERSON")

    name     = input("  Full Name     : ").strip()
    roll_id  = input("  ID / Roll No  : ").strip()
    role     = input("  Role (student/staff/admin) [student]: ").strip() or "student"

    if not name or not roll_id:
        print("  [!] Name and ID are required.\n")
        return

    print(f"\n  [*] Opening camera to capture face for '{name}'...")
    print("  [*] Press SPACE to capture | ESC to cancel\n")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("  [!] Cannot open camera.\n")
        return

    encoding = None
    face_img = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locs  = face_recognition.face_locations(rgb)
        encs  = face_recognition.face_encodings(rgb, locs)

        # Draw detection boxes
        for (top, right, bottom, left) in locs:
            t, r, b, l = top*2, right*2, bottom*2, left*2
            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 120), 2)
            cv2.putText(frame, "FACE DETECTED — Press SPACE", (l, t-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 120), 1)

        if not locs:
            cv2.putText(frame, "No face detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)

        cv2.imshow(f"Register: {name} — SPACE=Capture  ESC=Cancel", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:   # ESC
            break
        if key == 32 and encs:  # SPACE + face found
            encoding = encs[0]
            face_img = frame.copy()
            print(f"  [✓] Face captured successfully!")
            break

    cap.release()
    cv2.destroyAllWindows()

    if encoding is None:
        print("  [!] No face captured. Registration cancelled.\n")
        return

    # Save face image
    img_path = os.path.join(KNOWN_FACES_DIR, f"{roll_id}_{name.replace(' ','_')}.jpg")
    cv2.imwrite(img_path, face_img)

    db.add_person(name=name, roll_id=roll_id, role=role,
                  encoding=encoding, img_path=img_path)

    print(f"\n  [✓] '{name}' registered successfully!\n")


# ─── Draw Big Overlay on Camera Frame ────────────────────────────────────────
def draw_overlay(frame, result):
    h, w = frame.shape[:2]

    if result["granted"]:
        # Semi-transparent green overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 180, 250), -1)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

        # Green border
        cv2.rectangle(frame, (0, 0), (w, h), (0, 255, 70), 6)

        # Big text — center of screen
        cv2.putText(frame, "YOU CAN ENTER",
                    (w//2 - 200, h//2 - 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 70), 4)
        cv2.putText(frame, f"Welcome,  {result['name']}!",
                    (w//2 - 180, h//2 + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
        cv2.putText(frame, f"Match: {result['confidence']}%   |   {result['role'].upper()}",
                    (w//2 - 130, h//2 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 255, 180), 2)

    else:
        # Semi-transparent red overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 200), -1)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

        # Red border
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 6)

        # Big text — center of screen
        cv2.putText(frame, "YOU CANNOT ENTER",
                    (w//2 - 230, h//2 - 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.7, (0, 0, 255), 4)
        cv2.putText(frame, "NOT REGISTERED IN SYSTEM",
                    (w//2 - 230, h//2 + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2)
        cv2.putText(frame, "Contact your administrator.",
                    (w//2 - 170, h//2 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 180, 180), 2)

    return frame


# ─── Live Security Scanner ────────────────────────────────────────────────────
def run_scanner(db: "Database", logger: "AccessLogger", disp: "Display"):
    if db.count() == 0:
        print("\n  [!] No persons in database. Please register first.\n")
        return

    disp.section("SECURITY SCANNER — LIVE")
    print(f"  [*] {db.count()} person(s) in database.")
    print("  [*] Press Q to quit scanner.\n")
    time.sleep(1)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("  [!] Cannot open camera.\n")
        return

    known_encodings, known_names, known_ids, known_roles = db.get_all_encodings()

    last_scan_time       = 0
    last_result          = None
    result_display_until = 0
    cooldown_until       = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        now   = time.time()

        small = cv2.resize(frame, (0, 0), fx=FRAME_SCALE, fy=FRAME_SCALE)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locs = face_recognition.face_locations(rgb)
        face_encs = face_recognition.face_encodings(rgb, face_locs)

        # Run recognition at interval
        if now - last_scan_time > SCAN_INTERVAL and face_encs and now > cooldown_until:
            last_scan_time = now

            for enc in face_encs:
                distances = face_recognition.face_distance(known_encodings, enc)
                best_idx  = np.argmin(distances) if len(distances) > 0 else -1

                if best_idx >= 0 and distances[best_idx] < TOLERANCE:
                    last_result = {
                        "granted"   : True,
                        "name"      : known_names[best_idx],
                        "id"        : known_ids[best_idx],
                        "role"      : known_roles[best_idx],
                        "confidence": round((1 - distances[best_idx]) * 100, 1),
                    }
                    logger.log(last_result["name"], last_result["id"],
                               last_result["role"], granted=True,
                               confidence=last_result["confidence"])
                else:
                    last_result = {"granted": False, "name": "UNKNOWN",
                                   "role": "", "confidence": 0}
                    logger.log("UNKNOWN", "—", "—", granted=False)

                result_display_until = now + 3
                cooldown_until       = now + 4
                break

        # ── Draw face box ──
        scale = int(1 / FRAME_SCALE)
        for (top, right, bottom, left) in face_locs:
            t, r, b, l = top*scale, right*scale, bottom*scale, left*scale
            color = (180, 180, 0)   # yellow = scanning
            cv2.rectangle(frame, (l, t), (r, b), color, 2)

        # ── Show big overlay on camera if result active ──
        if last_result and now < result_display_until:
            frame = draw_overlay(frame, last_result)

        # ── HUD (top bar) ──
        ts = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        cv2.putText(frame, f"FACEGATE  |  {ts}  |  DB: {db.count()} registered",
                    (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        cv2.imshow("FaceGate Security Scanner  [ Q = Quit ]", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n  [*] Scanner stopped.\n")


# ─── Delete Person ─────────────────────────────────────────────────────────────
def delete_person(db: "Database", disp: "Display"):
    disp.section("DELETE PERSON")
    db.print_all()
    if db.count() == 0:
        return
    roll_id = input("\n  Enter ID to delete (or ENTER to cancel): ").strip()
    if roll_id:
        db.delete_person(roll_id)


if __name__ == "__main__":
    main()