"""
Progress screen: the current player's rounds over time, drawn as a line
chart on ruled paper (plain Tk canvas, no charting library), with a few
summary numbers and the most recent rounds.
"""

import math
import tkinter as tk

import db
import theme
from difficulty import DIFFICULTIES
from widgets import FlatButton, Page, RuledTable, Segmented, format_date

CHART_WINDOW = 30       # rounds shown on the chart
RECENT_ROWS = 4
CHART_HEIGHT = 190
PAD_LEFT, PAD_RIGHT, PAD_TOP, PAD_BOTTOM = 40, 40, 14, 26


def _nice_ticks(lo, hi, count=4):
    """Round tick values that cover lo..hi."""
    span = max(hi - lo, 1)
    raw = span / count
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1, 2, 5, 10) if m * magnitude >= raw)
    start = math.floor(lo / step) * step
    end = math.ceil(hi / step) * step
    ticks = []
    value = start
    while value <= end + 1e-9:
        ticks.append(value)
        value += step
    return ticks


class ProgressTab(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        fonts = self.fonts
        body = self.body
        self.add_back_link()
        self.points = []

        header = tk.Frame(body, bg=theme.PAPER)
        header.pack(fill="x", pady=(24, 0))
        tk.Label(header, text="Your progress", font=fonts["heading"], bg=theme.PAPER,
                 fg=theme.INK).pack(side="left")
        self.player_label = tk.Label(header, text="", font=fonts["body"],
                                     bg=theme.PAPER, fg=theme.INK)
        self.player_label.pack(side="right", anchor="s", pady=(0, 6))

        self.difficulty_var = tk.StringVar(value="All")
        Segmented(body, fonts, ["All"] + list(DIFFICULTIES), self.difficulty_var,
                  command=self.refresh).pack(anchor="w", pady=(12, 16))

        # Everything below is swapped for the empty state when there is no data.
        self.content = tk.Frame(body, bg=theme.PAPER)

        summary = tk.Frame(self.content, bg=theme.PAPER)
        summary.pack(fill="x")
        self.rounds_value = self._stat(summary, "rounds finished")
        self.best_value = self._stat(summary, "best wpm")
        self.recent_value = self._stat(summary, "average wpm, last 5 rounds")
        self.change_value = self._stat(summary, "change from the 5 before")

        tk.Label(self.content, text="Words per minute, oldest to newest",
                 font=fonts["label"], bg=theme.PAPER, fg=theme.PENCIL,
                 anchor="w").pack(anchor="w", pady=(16, 0))
        self.chart = tk.Canvas(self.content, bg=theme.PAPER, height=CHART_HEIGHT,
                               highlightthickness=0)
        self.chart.pack(fill="x")
        self.chart.bind("<Configure>", lambda e: self._draw_chart())
        self.chart.bind("<Motion>", self._on_hover)
        self.chart.bind("<Leave>", lambda e: self.chart.delete("hover"))

        self.table = RuledTable(self.content, fonts, [
            ("Date", 20, "w"), ("Difficulty", 10, "w"), ("WPM", 6, "e"),
            ("Accuracy", 9, "e"), ("Time", 8, "e"),
        ])
        self.table.pack(anchor="w", pady=(10, 0))

        self.empty = tk.Frame(body, bg=theme.PAPER)
        self.empty_label = tk.Label(self.empty, text="", font=fonts["body"],
                                    bg=theme.PAPER, fg=theme.INK, anchor="w",
                                    justify="left")
        self.empty_label.pack(anchor="w", pady=(8, 12))
        FlatButton(self.empty, fonts, "Choose a round",
                   lambda: self.app.show_screen("menu")).pack(anchor="w")

    def _stat(self, parent, caption):
        block = tk.Frame(parent, bg=theme.PAPER)
        block.pack(side="left", padx=(0, 44))
        value = tk.Label(block, text="", font=self.fonts["stat_small"], bg=theme.PAPER,
                         fg=theme.INK, anchor="w")
        value.pack(anchor="w")
        tk.Label(block, text=caption, font=self.fonts["label"], bg=theme.PAPER,
                 fg=theme.PENCIL, anchor="w").pack(anchor="w")
        return value

    def refresh(self):
        self.player_label.config(text=f"Playing as {self.app.player_name}")
        level = self.difficulty_var.get()
        difficulty = None if level == "All" else level
        rows = db.get_player_history(self.app.player_id, difficulty)

        if not rows:
            self.content.pack_forget()
            where = "" if difficulty is None else f" on {difficulty}"
            self.empty_label.config(
                text=f"No finished rounds{where} yet.\n"
                     "Your speed will be charted here after your first sentence."
            )
            self.empty.pack(anchor="w")
            return
        self.empty.pack_forget()
        self.content.pack(fill="both", expand=True)

        wpms = [row["wpm"] for row in rows]          # newest first
        self.rounds_value.config(text=str(len(rows)))
        self.best_value.config(text=f"{max(wpms):.0f}")
        last5 = wpms[:5]
        self.recent_value.config(text=f"{sum(last5) / len(last5):.0f}")
        prev5 = wpms[5:10]
        if prev5:
            delta = sum(last5) / len(last5) - sum(prev5) / len(prev5)
            self.change_value.config(text=f"{delta:+.1f}")
        else:
            self.change_value.config(text="-")

        self.table.set_rows([
            (format_date(row["completed_at"]), row["difficulty"], f"{row['wpm']:.0f}",
             f"{row['accuracy']:.0f}%", f"{row['elapsed_seconds']:.1f}s")
            for row in rows[:RECENT_ROWS]
        ])

        self.history = list(reversed(rows[:CHART_WINDOW]))   # oldest first
        self._draw_chart()

    # ------------------------------------------------------------------ chart

    def _draw_chart(self):
        c = self.chart
        c.delete("all")
        history = getattr(self, "history", [])
        if not history:
            return
        width = c.winfo_width()
        plot_w = width - PAD_LEFT - PAD_RIGHT
        plot_h = CHART_HEIGHT - PAD_TOP - PAD_BOTTOM
        values = [row["wpm"] for row in history]
        ticks = _nice_ticks(min(values), max(values))
        lo, hi = ticks[0], ticks[-1]
        if hi == lo:
            hi = lo + 1

        def y_of(v):
            return PAD_TOP + plot_h - (v - lo) / (hi - lo) * plot_h

        # Ruled gridlines double as the y axis.
        for t in ticks:
            y = y_of(t)
            c.create_line(PAD_LEFT, y, width - PAD_RIGHT, y, fill=theme.RULE)
            c.create_text(PAD_LEFT - 8, y, text=f"{t:g}", anchor="e",
                          font=self.fonts["label"], fill=theme.PENCIL)

        n = len(values)
        step = plot_w / (n - 1) if n > 1 else 0
        self.points = []
        for i, (row, v) in enumerate(zip(history, values)):
            x = PAD_LEFT + (i * step if n > 1 else plot_w / 2)
            self.points.append((x, y_of(v), row))

        if n > 1:
            coords = [coord for x, y, _ in self.points for coord in (x, y)]
            c.create_line(*coords, fill=theme.INK, width=2, joinstyle="round",
                          capstyle="round")
        for x, y, _ in self.points:
            c.create_oval(x - 4, y - 4, x + 4, y + 4, fill=theme.INK,
                          outline=theme.PAPER, width=2)

        # Direct label on the latest round only.
        x, y, row = self.points[-1]
        c.create_text(x + 10, y, text=f"{row['wpm']:.0f}", anchor="w",
                      font=self.fonts["label"], fill=theme.INK)
        c.create_text(PAD_LEFT, CHART_HEIGHT - 4, anchor="sw", text=f"{n} rounds ago"
                      if n > 1 else "", font=self.fonts["label"], fill=theme.PENCIL)
        c.create_text(width - PAD_RIGHT, CHART_HEIGHT - 4, anchor="se", text="latest",
                      font=self.fonts["label"], fill=theme.PENCIL)

    def _on_hover(self, event):
        c = self.chart
        c.delete("hover")
        if not self.points:
            return
        x, y, row = min(self.points, key=lambda p: abs(p[0] - event.x))
        c.create_line(x, PAD_TOP, x, CHART_HEIGHT - PAD_BOTTOM, fill=theme.PENCIL,
                      dash=(2, 3), tags="hover")
        c.create_oval(x - 6, y - 6, x + 6, y + 6, fill=theme.HIGHLIGHT,
                      outline=theme.INK, width=2, tags="hover")
        text = (f"{row['wpm']:.0f} wpm, {row['accuracy']:.0f}% accuracy\n"
                f"{row['difficulty']}, {format_date(row['completed_at'])}")
        label = c.create_text(0, 0, text=text, anchor="nw", font=self.fonts["label"],
                              fill=theme.INK, tags="hover")
        x0, y0, x1, y1 = c.bbox(label)
        w, h = x1 - x0 + 16, y1 - y0 + 10
        bx = x + 12 if x + 12 + w < c.winfo_width() else x - 12 - w
        by = min(max(y - h / 2, 0), CHART_HEIGHT - h)
        box = c.create_rectangle(bx, by, bx + w, by + h, fill=theme.PAPER,
                                 outline=theme.INK, tags="hover")
        c.coords(label, bx + 8, by + 5)
        c.tag_raise(label, box)
