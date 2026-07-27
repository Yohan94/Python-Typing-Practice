"""
The typing gameplay tab: sentence display, entry box, live stats,
difficulty selector, and optional countdown timer.
"""

import random
import time
import tkinter as tk
from tkinter import ttk

import theme
from difficulty import DIFFICULTIES


class GameTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="TFrame")
        self.app = app

        self.start_time = None
        self.current_sentence = ""
        self.finished = False
        self.timed_out = False
        self.remaining = None
        self.timer_job = None

        fonts = theme.build_fonts()
        self.text_font = fonts["text"]
        self.stats_font = fonts["stats"]

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
            self, text="⌨  Typing Practice", font=fonts["title"],
            bg=theme.BG, fg=theme.TITLE
        ).pack(pady=(20, 10))

        # Difficulty/timer are chosen on the main menu; just show what's active.
        self.info_label = tk.Label(
            self, text="", font=self.stats_font, bg=theme.BG, fg=theme.SUBTEXT
        )
        self.info_label.pack(pady=(0, 10))

        # Sentence display (Text widget so we can color individual characters)
        self.display = tk.Text(
            self, height=3, width=60, font=self.text_font,
            bg=theme.SURFACE, fg=theme.TEXT, wrap="word",
            borderwidth=0, highlightthickness=0, padx=20, pady=15
        )
        self.display.pack(pady=10)
        self.display.config(state="disabled")

        self.display.tag_configure("correct", foreground=theme.GREEN)
        self.display.tag_configure("incorrect", foreground=theme.RED, underline=True)
        self.display.tag_configure("pending", foreground=theme.SUBTEXT)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            self, textvariable=self.entry_var, font=self.text_font,
            width=50, bg=theme.SURFACE2, fg=theme.TITLE, insertbackground=theme.TITLE,
            borderwidth=0, highlightthickness=2, highlightcolor=theme.BLUE
        )
        self.entry.pack(pady=10, ipady=8)
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<Return>", self.on_enter)

        self.stats_label = tk.Label(
            self, text="WPM: 0   Accuracy: 0%   Time: 0.0s",
            font=self.stats_font, bg=theme.BG, fg=theme.TEAL
        )
        self.stats_label.pack(pady=5)

        self.timer_label = tk.Label(
            self, text="", font=self.stats_font, bg=theme.BG, fg=theme.RED
        )
        self.timer_label.pack(pady=(0, 5))

        btn_frame = tk.Frame(self, bg=theme.BG)
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame, text="New Sentence", command=self.new_sentence,
            font=self.stats_font, bg=theme.BLUE, fg=theme.BG,
            activebackground=theme.BLUE_HOVER, borderwidth=0, padx=15, pady=8
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame, text="Quit", command=self.app.root.destroy,
            font=self.stats_font, bg=theme.RED, fg=theme.BG,
            activebackground=theme.RED_HOVER, borderwidth=0, padx=15, pady=8
        ).pack(side="left", padx=10)

        self.new_sentence()

    def refresh(self):
        self.player_label.config(text=f"Player: {self.app.player_name}")
        self.new_sentence()

    def _cancel_timer(self):
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    def new_sentence(self):
        self._cancel_timer()
        level = self.app.difficulty
        config = DIFFICULTIES[level]
        self.current_sentence = random.choice(config["sentences"])
        self.time_limit = config["time_limit"] if self.app.timer_enabled else None
        self.remaining = self.time_limit
        timer_text = f"{self.time_limit}s" if self.time_limit is not None else "Off"
        self.info_label.config(text=f"Difficulty: {level}   Timer: {timer_text}")
        self.start_time = None
        self.finished = False
        self.timed_out = False
        self.entry_var.set("")
        self.entry.config(state="normal")
        self.entry.focus_set()

        self.display.config(state="normal")
        self.display.delete("1.0", "end")
        self.display.insert("1.0", self.current_sentence)
        self.display.tag_add("pending", "1.0", "end")
        self.display.config(state="disabled")

        self.stats_label.config(text="WPM: 0   Accuracy: 0%   Time: 0.0s")
        if self.time_limit is not None:
            self.timer_label.config(text=f"Time Left: {self.remaining}s")
        else:
            self.timer_label.config(text="")

    def _tick(self):
        if self.finished or self.timed_out:
            return
        self.remaining -= 1
        self.timer_label.config(text=f"Time Left: {self.remaining}s")
        if self.remaining <= 0:
            self.timed_out = True
            self.entry.config(state="disabled")
            self.timer_label.config(text="Time's up! Click 'New Sentence' to retry.")
            return
        self.timer_job = self.after(1000, self._tick)

    def on_enter(self, event):
        if self.finished:
            self.new_sentence()

    def on_key_release(self, event):
        if self.finished or self.timed_out:
            return

        typed = self.entry_var.get()

        if self.start_time is None and len(typed) > 0:
            self.start_time = time.time()
            if self.time_limit is not None:
                self.timer_job = self.after(1000, self._tick)

        target = self.current_sentence

        self.display.config(state="normal")
        self.display.tag_remove("correct", "1.0", "end")
        self.display.tag_remove("incorrect", "1.0", "end")
        self.display.tag_remove("pending", "1.0", "end")

        correct_count = 0
        for i, ch in enumerate(target):
            start_idx = f"1.0+{i}c"
            end_idx = f"1.0+{i+1}c"
            if i < len(typed):
                if typed[i] == ch:
                    self.display.tag_add("correct", start_idx, end_idx)
                    correct_count += 1
                else:
                    self.display.tag_add("incorrect", start_idx, end_idx)
            else:
                self.display.tag_add("pending", start_idx, end_idx)
        self.display.config(state="disabled")

        elapsed = (time.time() - self.start_time) if self.start_time else 0
        accuracy = (correct_count / len(typed) * 100) if typed else 0
        wpm = (len(typed) / 5) / (elapsed / 60) if elapsed > 0 else 0

        self.stats_label.config(
            text=f"WPM: {wpm:.0f}   Accuracy: {accuracy:.0f}%   Time: {elapsed:.1f}s"
        )

        if typed == target:
            self.finished = True
            self._cancel_timer()
            final_elapsed = time.time() - self.start_time
            final_wpm = (len(target) / 5) / (final_elapsed / 60)
            self.stats_label.config(
                text=f"✅ Done! WPM: {final_wpm:.0f}   Accuracy: 100%   "
                     f"Time: {final_elapsed:.1f}s  — click 'New Sentence' to continue"
            )
            score = final_wpm * (100.0 / 100.0)
            self.app.record_session(
                difficulty=self.app.difficulty,
                sentence=target,
                wpm=final_wpm,
                accuracy=100.0,
                elapsed_seconds=final_elapsed,
                score=score,
            )
