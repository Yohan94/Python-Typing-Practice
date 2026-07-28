"""
Main menu screen: enter/pick a player name, then navigate to
Start Game, Leaderboard, or Progress — all within the same window.
"""

import tkinter as tk
from tkinter import ttk

import db
import theme
from difficulty import DIFFICULTIES
from sentences import SENTENCE_SETS


class MainMenu(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app

        tk.Label(
            self, text="⌨  Typing Practice", font=("Helvetica", 26, "bold"),
            bg=theme.BG, fg=theme.TITLE
        ).pack(pady=(25, 12))

        tk.Label(
            self, text="Enter your name to continue", font=("Helvetica", 13),
            bg=theme.BG, fg=theme.TEXT
        ).pack(pady=(0, 8))

        self.name_var = tk.StringVar()
        self.combo = ttk.Combobox(
            self, textvariable=self.name_var, font=("Helvetica", 13), width=28
        )
        self.combo.pack(pady=5)
        self.combo.bind("<Return>", lambda event: self._start_game())

        self.error_label = tk.Label(
            self, text="", font=("Helvetica", 10), bg=theme.BG, fg=theme.RED
        )
        self.error_label.pack(pady=(3, 6))

        # Sentence type selector: which pool of sentences to practise with
        type_frame = tk.Frame(self, bg=theme.BG)
        type_frame.pack(pady=(5, 5))
        tk.Label(
            type_frame, text="Sentence Type:", font=("Helvetica", 12),
            bg=theme.BG, fg=theme.TEXT
        ).pack(side="left", padx=(0, 10))
        self.type_var = tk.StringVar(value=app.sentence_type)
        for category in SENTENCE_SETS:
            ttk.Radiobutton(
                type_frame, text=category, value=category, variable=self.type_var
            ).pack(side="left", padx=5)

        # Difficulty selector
        diff_frame = tk.Frame(self, bg=theme.BG)
        diff_frame.pack(pady=(5, 5))
        tk.Label(
            diff_frame, text="Difficulty:", font=("Helvetica", 12),
            bg=theme.BG, fg=theme.TEXT
        ).pack(side="left", padx=(0, 10))
        self.difficulty_var = tk.StringVar(value=app.difficulty)
        for level in DIFFICULTIES:
            ttk.Radiobutton(
                diff_frame, text=level, value=level, variable=self.difficulty_var
            ).pack(side="left", padx=5)

        # Optional timer toggle (applies to whichever difficulty is selected)
        self.timer_var = tk.BooleanVar(value=app.timer_enabled)
        ttk.Checkbutton(
            self, text="Enable Timer", variable=self.timer_var
        ).pack(pady=(5, 15))

        btn_frame = tk.Frame(self, bg=theme.BG)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="Start Game", command=self._start_game,
            font=("Helvetica", 12), bg=theme.BLUE, fg=theme.BG,
            activebackground=theme.BLUE_HOVER, borderwidth=0, padx=18, pady=10, width=14
        ).pack(pady=6)

        tk.Button(
            btn_frame, text="Leaderboard", command=self._show_leaderboard,
            font=("Helvetica", 12), bg=theme.SURFACE2, fg=theme.TEXT,
            activebackground=theme.SURFACE, borderwidth=0, padx=18, pady=10, width=14
        ).pack(pady=6)

        tk.Button(
            btn_frame, text="Progress", command=self._show_progress,
            font=("Helvetica", 12), bg=theme.SURFACE2, fg=theme.TEXT,
            activebackground=theme.SURFACE, borderwidth=0, padx=18, pady=10, width=14
        ).pack(pady=6)

        tk.Button(
            btn_frame, text="Quit", command=self.app.root.destroy,
            font=("Helvetica", 12), bg=theme.RED, fg=theme.BG,
            activebackground=theme.RED_HOVER, borderwidth=0, padx=18, pady=10, width=14
        ).pack(pady=6)

    def refresh(self):
        self.combo.config(values=db.list_players())
        self.error_label.config(text="")

    def _require_name(self):
        name = self.name_var.get().strip()
        if not name:
            self.error_label.config(text="Please enter a name.")
            return None
        self.error_label.config(text="")
        self.app.set_player(name)
        return name

    def _start_game(self):
        if self._require_name():
            self.app.difficulty = self.difficulty_var.get()
            self.app.sentence_type = self.type_var.get()
            self.app.timer_enabled = self.timer_var.get()
            self.app.show_screen("game")

    def _show_progress(self):
        if self._require_name():
            self.app.show_screen("progress")

    def _show_leaderboard(self):
        self.app.show_screen("leaderboard")
