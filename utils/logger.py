"""
AccessLogger — records every access attempt to a JSON log file.
"""

import os
import json
import datetime


class AccessLogger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    def log(self, name: str, roll_id: str, role: str,
            granted: bool, confidence: float = 0.0):
        entry = {
            "timestamp" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name"      : name,
            "id"        : roll_id,
            "role"      : role,
            "status"    : "GRANTED" if granted else "DENIED",
            "confidence": confidence,
        }
        # Load existing
        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(entry)

        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)

        # Console print
        icon   = "✅" if granted else "❌"
        status = "GRANTED" if granted else "DENIED"
        conf_str = f"  [{confidence}%]" if granted else ""
        print(f"  {icon} [{entry['timestamp']}]  {status}  —  {name}{conf_str}")

    def print_logs(self, last_n: int = 30):
        if not os.path.exists(self.log_file):
            print("\n  (No logs found)\n")
            return

        with open(self.log_file, "r") as f:
            logs = json.load(f)

        logs = logs[-last_n:]
        print(f"\n{'─'*66}")
        print(f"  {'TIMESTAMP':<22} {'STATUS':<9} {'NAME':<22} {'CONF'}")
        print(f"{'─'*66}")
        for e in reversed(logs):
            icon = "✅" if e["status"] == "GRANTED" else "❌"
            conf = f"{e['confidence']}%" if e["confidence"] else "—"
            print(f"  {e['timestamp']:<22} {icon} {e['status']:<7} {e['name']:<22} {conf}")
        print(f"{'─'*66}")
        print(f"  Showing last {len(logs)} entries\n")