"""
Main menu screen: enter/pick a player name, choose what to practise, then
start a round or open the Leaderboard or Progress screens.
"""

import tkinter as tk
from tkinter import ttk

import db
import theme
from difficulty import DIFFICULTIES
from sentences import BEGINNER_LEVEL, SENTENCE_SETS, get_time_limit
from widgets import FlatButton, Page, Segmented, field_label

CATEGORY_HINTS = {
    "General": "Everyday sentences, from simple to number-heavy.",
    "Grammar": "Each sentence comes with a short grammar tip.",
    "Conversation": "Phrases you would say out loud, with notes on usage.",
    "Idioms": "Common idioms and what they really mean.",
    "Business": "Workplace English: emails, meetings and reports.",
}

LEVEL_HINTS = {
    "Easy": "Short sentences with no punctuation.",
    "Medium": "Longer sentences with everyday punctuation.",
    "Hard": "Numbers, symbols and quotation marks.",
}


class MainMenu(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        fonts = self.fonts
        body = self.body

        tk.Label(
            body, text="Typing Practice", font=fonts["display"],
            bg=theme.PAPER, fg=theme.INK, anchor="w",
        ).pack(anchor="w", pady=(28, 0))
        tk.Label(
            body, text="Type each sentence exactly as shown. Mistakes are marked in red as you go.",
            font=fonts["body"], bg=theme.PAPER, fg=theme.PENCIL, anchor="w",
        ).pack(anchor="w", pady=(2, 22))

        # Name
        field_label(body, fonts, "Your name").pack(anchor="w")
        self.name_var = tk.StringVar()
        self.combo = ttk.Combobox(
            body, textvariable=self.name_var, font=fonts["body"], width=30
        )
        self.combo.pack(anchor="w", pady=(4, 0))
        self.combo.bind("<Return>", lambda event: self._start_game())
        self.combo.bind("<KeyRelease>", lambda event: self._clear_error())

        self.error_label = tk.Label(
            body, text="", font=fonts["label"], bg=theme.PAPER, fg=theme.MARGIN,
            anchor="w",
        )
        self.error_label.pack(anchor="w", pady=(2, 10))

        # Sentence category
        field_label(body, fonts, "Subject").pack(anchor="w")
        self.type_var = tk.StringVar(value=app.sentence_type)
        Segmented(
            body, fonts, SENTENCE_SETS, self.type_var,
            command=self._on_choice_change, hints=CATEGORY_HINTS,
        ).pack(anchor="w", pady=(4, 16))

        # Difficulty (its hint mentions the timer length, so create that first)
        self.timer_var = tk.BooleanVar(value=app.timer_enabled)
        field_label(body, fonts, "Difficulty").pack(anchor="w")
        self.difficulty_var = tk.StringVar(value=app.difficulty)
        level_hints = {
            level: (lambda lv=level: self._level_hint(lv)) for level in DIFFICULTIES
        }
        self.level_control = Segmented(
            body, fonts, DIFFICULTIES, self.difficulty_var,
            command=self._on_choice_change, hints=level_hints,
        )
        self.level_control.pack(anchor="w", pady=(4, 16))

        # Toggles that apply to whichever type and difficulty are selected.
        # Unchecking Punctuation or Capital Letters simplifies the sentences.
        field_label(body, fonts, "Options").pack(anchor="w")
        options_frame = tk.Frame(body, bg=theme.PAPER)
        options_frame.pack(anchor="w", pady=(2, 26))
        ttk.Checkbutton(
            options_frame, text="Countdown timer", variable=self.timer_var,
            command=self._on_choice_change,
        ).pack(side="left", padx=(0, 22))
        self.punctuation_var = tk.BooleanVar(value=app.punctuation_enabled)
        self.punctuation_check = ttk.Checkbutton(
            options_frame, text="Punctuation", variable=self.punctuation_var
        )
        self.punctuation_check.pack(side="left", padx=(0, 22))
        self.capitals_var = tk.BooleanVar(value=app.capitals_enabled)
        ttk.Checkbutton(
            options_frame, text="Capital letters", variable=self.capitals_var
        ).pack(side="left")

        actions = tk.Frame(body, bg=theme.PAPER)
        actions.pack(anchor="w")
        FlatButton(actions, fonts, "Start typing", self._start_game).pack(side="left")
        FlatButton(
            actions, fonts, "Leaderboard", self._show_leaderboard, kind="secondary"
        ).pack(side="left", padx=(12, 0))
        FlatButton(
            actions, fonts, "Your progress", self._show_progress, kind="secondary"
        ).pack(side="left", padx=(12, 0))

        tk.Label(
            body, text="Press Enter in the name box to start. Esc returns here from any screen.",
            font=fonts["label"], bg=theme.PAPER, fg=theme.PENCIL, anchor="w",
        ).pack(anchor="w", pady=(10, 0))

        self._on_choice_change()

    def refresh(self):
        players = db.list_players()
        self.combo.config(values=players)
        if not self.name_var.get().strip():
            self.name_var.set(self.app.player_name or db.last_player_name())
        self._clear_error()
        self.combo.focus_set()
        self.combo.icursor("end")

    def _level_hint(self, level):
        text = LEVEL_HINTS.get(level, "")
        if self.timer_var.get():
            seconds = get_time_limit(self.type_var.get(), level)
            text += f" You get {seconds} seconds per sentence."
        return text

    def _on_choice_change(self):
        # Easy always strips punctuation, so the toggle would do nothing there.
        if self.difficulty_var.get() == BEGINNER_LEVEL:
            self.punctuation_check.state(["disabled"])
        else:
            self.punctuation_check.state(["!disabled"])
        self.level_control.refresh_hint()

    def _clear_error(self):
        self.error_label.config(text="")

    def _require_name(self):
        name = self.name_var.get().strip()
        if not name:
            self.error_label.config(text="Enter a name so your scores can be saved.")
            self.combo.focus_set()
            return None
        self._clear_error()
        self.app.set_player(name)
        return name

    def _start_game(self):
        if self._require_name():
            self.app.difficulty = self.difficulty_var.get()
            self.app.sentence_type = self.type_var.get()
            self.app.timer_enabled = self.timer_var.get()
            self.app.punctuation_enabled = self.punctuation_var.get()
            self.app.capitals_enabled = self.capitals_var.get()
            self.app.show_screen("game")

    def _show_progress(self):
        if self._require_name():
            self.app.show_screen("progress")

    def _show_leaderboard(self):
        self.app.show_screen("leaderboard")
