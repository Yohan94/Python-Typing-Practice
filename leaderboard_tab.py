"""
Leaderboard tab: top 10 scores per difficulty, across all players.
"""

import tkinter as tk
from tkinter import ttk

import db
import theme
from difficulty import DIFFICULTIES


class LeaderboardTab(ttk.Frame):
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

        tk.Label(
            self, text="🏆  Leaderboard", font=("Helvetica", 18, "bold"),
            bg=theme.BG, fg=theme.TITLE
        ).pack(pady=(20, 10))

        filter_frame = tk.Frame(self, bg=theme.BG)
        filter_frame.pack(pady=(0, 10))
        tk.Label(
            filter_frame, text="Difficulty:", font=("Helvetica", 12),
            bg=theme.BG, fg=theme.TEXT
        ).pack(side="left", padx=(0, 10))
        self.difficulty_var = tk.StringVar(value="Medium")
        for level in DIFFICULTIES:
            ttk.Radiobutton(
                filter_frame, text=level, value=level, variable=self.difficulty_var,
                command=self.refresh
            ).pack(side="left", padx=5)

        columns = ("rank", "player", "wpm", "accuracy", "score", "date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        headings = {
            "rank": "Rank", "player": "Player", "wpm": "WPM",
            "accuracy": "Accuracy", "score": "Score", "date": "Date",
        }
        widths = {"rank": 50, "player": 150, "wpm": 80, "accuracy": 90, "score": 90, "date": 160}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = db.get_leaderboard(self.difficulty_var.get())
        for i, row in enumerate(rows, start=1):
            self.tree.insert(
                "", "end",
                values=(
                    i, row["name"], f"{row['wpm']:.0f}",
                    f"{row['accuracy']:.0f}%", f"{row['score']:.1f}",
                    row["completed_at"],
                ),
            )
