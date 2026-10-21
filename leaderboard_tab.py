"""
Leaderboard screen: top 10 scores per difficulty, across all players.
Score is words per minute weighted by accuracy.
"""

import tkinter as tk

import db
import theme
from difficulty import DIFFICULTIES
from widgets import FlatButton, Page, RuledTable, Segmented, format_date


class LeaderboardTab(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        fonts = self.fonts
        body = self.body
        self.add_back_link()

        tk.Label(
            body, text="Leaderboard", font=fonts["heading"], bg=theme.PAPER,
            fg=theme.INK, anchor="w",
        ).pack(anchor="w", pady=(24, 0))
        tk.Label(
            body, text="The ten best rounds by everyone on this computer. "
                       "Score is words per minute multiplied by accuracy.\n"
                       "Your own rounds are highlighted.",
            font=fonts["body"], bg=theme.PAPER, fg=theme.PENCIL, anchor="w", justify="left",
        ).pack(anchor="w", pady=(2, 16))

        self.difficulty_var = tk.StringVar(value=app.difficulty)
        Segmented(body, fonts, DIFFICULTIES, self.difficulty_var,
                  command=self.refresh).pack(anchor="w", pady=(0, 18))

        self.table = RuledTable(body, fonts, [
            ("Rank", 5, "w"), ("Player", 16, "w"), ("Score", 7, "e"),
            ("WPM", 6, "e"), ("Accuracy", 9, "e"), ("Date", 18, "w"),
        ])
        self.table.pack(anchor="w")

        self.empty = tk.Frame(body, bg=theme.PAPER)
        self.empty_label = tk.Label(
            self.empty, text="", font=fonts["body"], bg=theme.PAPER, fg=theme.INK,
            anchor="w",
        )
        self.empty_label.pack(anchor="w", pady=(16, 12))
        FlatButton(self.empty, fonts, "Choose a round",
                   lambda: self.app.show_screen("menu")).pack(anchor="w")

    def refresh(self):
        level = self.difficulty_var.get()
        rows = db.get_leaderboard(level)
        values, mine = [], set()
        for i, row in enumerate(rows):
            values.append((
                str(i + 1), row["name"], f"{row['score']:.1f}", f"{row['wpm']:.0f}",
                f"{row['accuracy']:.0f}%", format_date(row["completed_at"]),
            ))
            if self.app.player_name and row["name"].lower() == self.app.player_name.lower():
                mine.add(i)
        self.table.set_rows(values, highlight=mine, highlight_column=1)

        if rows:
            self.empty.pack_forget()
        else:
            self.empty_label.config(
                text=f"No one has finished a {level} round yet. Finish one to take first place."
            )
            self.empty.pack(anchor="w")
