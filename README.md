# Typing Practice Game

A desktop typing practice game built with Python's Tkinter, featuring adjustable
difficulty, multiple sentence categories, a multi-player leaderboard, and
per-player progress tracking over time — all persisted to a local SQLite
database.

## Features

- **Difficulty levels** — Easy, Medium, and Hard, each with its own sentence
  pool and default countdown time.
- **Sentence categories** — General, Grammar, Conversation, Idioms, and
  Business, so you can practice typing alongside short teaching notes (e.g.
  grammar tips) shown under each sentence.
- **Punctuation & capitalization toggles** — simplify sentences for beginners
  by stripping punctuation and/or lowercasing text.
- **Type straight onto the sentence** — letters turn from pencil grey to ink
  as you type them correctly, mistakes (including wrong spaces) are marked in
  red, and a highlighter shows the next letter.
- **Honest accuracy** — every wrong key counts, even after you fix it with
  Backspace, and the score is words per minute multiplied by accuracy.
- **Optional countdown timer** — race against the clock with a draining time
  bar, or turn it off to practice at your own pace.
- **Keyboard first** — Enter starts and moves to the next sentence, Tab skips
  a sentence, Esc returns to the menu from any screen.
- **Leaderboard** — top 10 scores per difficulty, across all players, with
  your own rounds highlighted.
- **Progress tracking** — a words-per-minute chart of your last 30 rounds
  (hover a point for details), your best and recent averages, and a personal
  best check after every round, drawn on a plain Tk canvas.
- **Local persistence** — players and completed sessions are stored in a
  SQLite database (`typing_game.db`), created automatically on first run.

## Requirements

- Python 3.8+
- No external dependencies — only the standard library (`tkinter`, `sqlite3`)
  is used.

## Getting started

```bash
python main.py
```

1. Enter a player name (the last player is filled in, and existing names are
   suggested).
2. Pick a subject (sentence category) and difficulty.
3. Optionally enable the countdown timer, or turn off punctuation / capital
   letters.
4. Click **Start typing** (or press Enter) and type the sentence.

## Project structure

| File | Purpose |
|---|---|
| `main.py` | App entry point and screen navigation. |
| `main_menu.py` | Player selection, category/difficulty/options menu. |
| `game_tab.py` | Core gameplay: sentence display, input, live stats, timer. |
| `leaderboard_tab.py` | Top scores per difficulty across all players. |
| `progress_tab.py` | Per-player history and WPM trend sparkline. |
| `difficulty.py` | Difficulty levels and their default sentence pools. |
| `sentences.py` | Sentence categories, punctuation stripping, sentence selection. |
| `db.py` | SQLite schema and persistence helpers. |
| `theme.py` | Exercise-book colors, fonts and ttk styling. |
| `widgets.py` | Shared widgets: page with margin, buttons, segmented chooser, ruled table. |

## Data storage

On first run, the app creates a local `typing_game.db` SQLite file to store
player names and session history (WPM, accuracy, score, timestamps). This
file is gitignored and stays on your machine — it isn't part of the
repository.

## License

Released under the [MIT License](LICENSE).
