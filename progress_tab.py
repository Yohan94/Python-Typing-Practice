"""
Progress tab: the current player's session history over time, with a
lightweight sparkline trend indicator (no charting library needed).
"""

import tkinter as tk
from tkinter import ttk

import db
import theme
from difficulty import DIFFICULTIES

SPARK_CHARS = "▁▂▃▄▅▆▇█"
SPARK_WINDOW = 20


def _sparkline(values):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        return SPARK_CHARS[-1] * len(values)
    span = hi - lo
    chars = []
    for v in values:
        idx = int((v - lo) / span * (len(SPARK_CHARS) - 1))
        chars.append(SPARK_CHARS[idx])
    return "".join(chars)


class ProgressTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app

        top_bar = tk.Frame(self, bg=theme.BG)
        top_bar.pack(fill="x", padx=10, pady=(10, 0))
        tk.Button(
            top_bar, text="☰ Menu", command=lambda: self.app.show_screen("menu"),
            font=("Helvetica", 10), bg=theme.SURFACE2, fg=theme.TEXT,
            activebackground=theme.SURFACE, borderwidth=0, padx=10, pady=4
        ).pack(side="left")

        self.player_label = tk.Label(
            top_bar, text="", font=("Helvetica", 10, "bold"),
            bg=theme.BG, fg=theme.TEAL
        )
        self.player_label.pack(side="right")

        tk.Label(
            self, text="📈  Your Progress", font=("Helvetica", 18, "bold"),
            bg=theme.BG, fg=theme.TITLE
        ).pack(pady=(20, 10))

        filter_frame = tk.Frame(self, bg=theme.BG)
        filter_frame.pack(pady=(0, 10))
        tk.Label(
            filter_frame, text="Difficulty:", font=("Helvetica", 12),
            bg=theme.BG, fg=theme.TEXT
        ).pack(side="left", padx=(0, 10))
        self.difficulty_var = tk.StringVar(value="All")
        for level in ["All"] + list(DIFFICULTIES):
            ttk.Radiobutton(
                filter_frame, text=level, value=level, variable=self.difficulty_var,
                command=self.refresh
            ).pack(side="left", padx=5)

        self.trend_label = tk.Label(
            self, text="", font=("Consolas", 14), bg=theme.BG, fg=theme.TEAL
        )
        self.trend_label.pack(pady=(0, 10))

        columns = ("date", "difficulty", "wpm", "accuracy", "time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        headings = {
            "date": "Date", "difficulty": "Difficulty", "wpm": "WPM",
            "accuracy": "Accuracy", "time": "Time",
        }
        widths = {"date": 160, "difficulty": 100, "wpm": 80, "accuracy": 90, "time": 90}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh()

    def refresh(self):
        self.player_label.config(text=f"Player: {self.app.player_name}")
        for row in self.tree.get_children():
            self.tree.delete(row)

        level = self.difficulty_var.get()
        difficulty = None if level == "All" else level
        rows = db.get_player_history(self.app.player_id, difficulty)

        for row in rows:
            self.tree.insert(
                "", "end",
                values=(
                    row["completed_at"], row["difficulty"], f"{row['wpm']:.0f}",
                    f"{row['accuracy']:.0f}%", f"{row['elapsed_seconds']:.1f}s",
                ),
            )

        recent = [row["wpm"] for row in rows[:SPARK_WINDOW]][::-1]
        if recent:
            spark = _sparkline(recent)
            avg_last5 = sum(recent[-5:]) / len(recent[-5:])
            if len(recent) > 5:
                prev = recent[:-5][-5:] or recent[:-5]
                avg_prev5 = sum(prev) / len(prev)
                delta = avg_last5 - avg_prev5
                sign = "+" if delta >= 0 else ""
                self.trend_label.config(
                    text=f"{spark}   Last 5 avg: {avg_last5:.0f} WPM ({sign}{delta:.1f} vs previous)"
                )
            else:
                self.trend_label.config(text=f"{spark}   Last 5 avg: {avg_last5:.0f} WPM")
        else:
            self.trend_label.config(text="No sessions yet — go play a round!")
