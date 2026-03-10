"""
Database — stores face encodings, names, IDs, roles
using pickle for persistence.
"""

import os
import pickle
import numpy as np


class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.records = []   # list of dicts
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────
    def _load(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "rb") as f:
                self.records = pickle.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, "wb") as f:
            pickle.dump(self.records, f)

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def add_person(self, name: str, roll_id: str, role: str,
                   encoding: np.ndarray, img_path: str):
        # Remove existing entry with same ID
        self.records = [r for r in self.records if r["id"] != roll_id]
        self.records.append({
            "name"    : name,
            "id"      : roll_id,
            "role"    : role,
            "encoding": encoding,
            "img_path": img_path,
        })
        self._save()

    def delete_person(self, roll_id: str):
        before = len(self.records)
        self.records = [r for r in self.records if r["id"] != roll_id]
        if len(self.records) < before:
            self._save()
            print(f"\n  [✓] Person with ID '{roll_id}' deleted.\n")
        else:
            print(f"\n  [!] ID '{roll_id}' not found.\n")

    def count(self) -> int:
        return len(self.records)

    # ── Bulk retrieval for recognition ────────────────────────────────────────
    def get_all_encodings(self):
        encodings = [r["encoding"] for r in self.records]
        names     = [r["name"]     for r in self.records]
        ids       = [r["id"]       for r in self.records]
        roles     = [r["role"]     for r in self.records]
        return encodings, names, ids, roles

    # ── Display ───────────────────────────────────────────────────────────────
    def print_all(self):
        print("\n" + "─"*54)
        print(f"  {'ID':<12} {'NAME':<22} {'ROLE':<10}")
        print("─"*54)
        if not self.records:
            print("  (No records found)")
        for r in self.records:
            print(f"  {r['id']:<12} {r['name']:<22} {r['role']:<10}")
        print("─"*54)
        print(f"  Total: {self.count()} registered\n")