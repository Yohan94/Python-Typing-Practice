"""
SQLite persistence for players and completed typing sessions.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "typing_game.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id        INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    difficulty       TEXT NOT NULL CHECK(difficulty IN ('Easy','Medium','Hard')),
    sentence         TEXT NOT NULL,
    wpm              REAL NOT NULL,
    accuracy         REAL NOT NULL,
    elapsed_seconds  REAL NOT NULL,
    score            REAL NOT NULL,
    completed_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_sessions_player_id        ON sessions(player_id);
CREATE INDEX IF NOT EXISTS idx_sessions_difficulty_score ON sessions(difficulty, score DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_player_completed ON sessions(player_id, completed_at);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def get_or_create_player(name):
    name = name.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name FROM players WHERE name = ? COLLATE NOCASE", (name,)
        ).fetchone()
        if row is not None:
            return row["id"], row["name"]
        cur = conn.execute("INSERT INTO players (name) VALUES (?)", (name,))
        return cur.lastrowid, name


def list_players():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM players ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [row["name"] for row in rows]


def insert_session(player_id, difficulty, sentence, wpm, accuracy, elapsed_seconds, score):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO sessions
               (player_id, difficulty, sentence, wpm, accuracy, elapsed_seconds, score)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (player_id, difficulty, sentence, wpm, accuracy, elapsed_seconds, score),
        )


def get_leaderboard(difficulty, limit=10):
    with get_connection() as conn:
        return conn.execute(
            """SELECT p.name AS name, s.wpm AS wpm, s.accuracy AS accuracy,
                      s.score AS score, s.completed_at AS completed_at
               FROM sessions s
               JOIN players p ON p.id = s.player_id
               WHERE s.difficulty = ?
               ORDER BY s.score DESC
               LIMIT ?""",
            (difficulty, limit),
        ).fetchall()


def get_player_history(player_id, difficulty=None, limit=200):
    with get_connection() as conn:
        if difficulty:
            return conn.execute(
                """SELECT difficulty, wpm, accuracy, elapsed_seconds, score, completed_at
                   FROM sessions
                   WHERE player_id = ? AND difficulty = ?
                   ORDER BY completed_at DESC
                   LIMIT ?""",
                (player_id, difficulty, limit),
            ).fetchall()
        return conn.execute(
            """SELECT difficulty, wpm, accuracy, elapsed_seconds, score, completed_at
               FROM sessions
               WHERE player_id = ?
               ORDER BY completed_at DESC
               LIMIT ?""",
            (player_id, limit),
        ).fetchall()
