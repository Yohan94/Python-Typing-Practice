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
- **Optional countdown timer** — race against the clock, or turn it off to
  practice at your own pace.
- **Leaderboard** — top 10 scores per difficulty, across all players.
- **Progress tracking** — per-player session history with a lightweight
  sparkline trend of your last several rounds, no charting library required.
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

1. Enter a player name (existing names are remembered and suggested).
2. Pick a sentence category and difficulty.
3. Optionally enable the timer, or toggle punctuation / capital letters.
4. Click **Start Game** and start typing!

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
| `theme.py` | Shared colors and fonts for the UI. |

## Data storage

On first run, the app creates a local `typing_game.db` SQLite file to store
player names and session history (WPM, accuracy, score, timestamps). This
file is gitignored and stays on your machine — it isn't part of the
repository.

## License

Released under the [MIT License](LICENSE).
