"""
Display — CLI formatting helpers.
"""

import os


class Display:
    WIDTH = 54

    def banner(self):
        os.system("cls" if os.name == "nt" else "clear")
        print()
        print("  ╔" + "═" * (self.WIDTH - 2) + "╗")
        print("  ║" + "  FACEGATE — CLASSROOM SECURITY SYSTEM  ".center(self.WIDTH - 2) + "║")
        print("  ║" + "  Face Recognition Access Control       ".center(self.WIDTH - 2) + "║")
        print("  ╚" + "═" * (self.WIDTH - 2) + "╝")
        print()

    def section(self, title: str):
        os.system("cls" if os.name == "nt" else "clear")
        print()
        print(f"  ── {title} " + "─" * max(0, self.WIDTH - len(title) - 5))
        print()