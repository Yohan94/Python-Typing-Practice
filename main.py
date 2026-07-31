"""
Typing Practice Game
---------------------
A GUI game to help you practice keyboard typing speed and accuracy, with
difficulty levels, a multi-player leaderboard, and per-player progress
tracking over time — all persisted to a local SQLite database.

How to run:
    python main.py

Requires only the Python standard library (tkinter, sqlite3), no extra installs.
"""

import tkinter as tk

import db
import sentences
import theme
from main_menu import MainMenu
from game_tab import GameTab
from leaderboard_tab import LeaderboardTab
from progress_tab import ProgressTab


class TypingGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Practice Game")
        self.root.geometry("900x600")
        self.root.configure(bg=theme.BG)
        self.root.resizable(False, False)

        theme.build_style(self.root)
        db.init_db()

        self.player_id = None
        self.player_name = None
        self.difficulty = "Medium"
        self.sentence_type = sentences.DEFAULT_CATEGORY
        self.timer_enabled = False
        self.punctuation_enabled = True
        self.capitals_enabled = True

        self.container = tk.Frame(self.root, bg=theme.BG)
        self.container.pack(fill="both", expand=True)

        self.screens = {
            "menu": MainMenu(self.container, self),
            "game": GameTab(self.container, self),
            "leaderboard": LeaderboardTab(self.container, self),
            "progress": ProgressTab(self.container, self),
        }
        for screen in self.screens.values():
            screen.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_screen("menu")

    def show_screen(self, name):
        screen = self.screens[name]
        screen.tkraise()
        if hasattr(screen, "refresh"):
            screen.refresh()

    def set_player(self, name):
        self.player_id, self.player_name = db.get_or_create_player(name)

    def record_session(self, difficulty, sentence, wpm, accuracy, elapsed_seconds, score):
        db.insert_session(
            self.player_id, difficulty, sentence, wpm, accuracy, elapsed_seconds, score
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingGameApp(root)
    root.mainloop()
