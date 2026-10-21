"""
The typing screen: the sentence is drawn on ruled lines and the player types
straight onto it. Untyped letters are pencil grey, correct letters turn to
ink, mistakes are marked in red, and a highlighter shows the next letter.
"""

import time
import tkinter as tk

import db
import theme
from sentences import BEGINNER_LEVEL, format_sentence, get_time_limit, pick_sentence
from widgets import FlatButton, Page

LINE_GAP = 1.7          # ruled line spacing as a multiple of the font's line height
MIN_RULED_LINES = 2     # one spare ruled line is always drawn below the text
LOW_TIME_FRACTION = 0.25


class GameTab(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        fonts = self.fonts
        body = self.body
        self.add_back_link()

        self.start_time = None
        self.current_sentence = ""
        self.finished = False
        self.timed_out = False
        self.remaining = None
        self.time_limit = None
        self.timer_job = None
        self.clock_job = None
        self.keystrokes = 0
        self.errors = 0
        self._last_typed = ""
        self._char_items = []

        # Header: what is being practised, and who is playing.
        header = tk.Frame(body, bg=theme.PAPER)
        header.pack(fill="x", pady=(30, 0))
        self.info_label = tk.Label(
            header, text="", font=fonts["body"], bg=theme.PAPER, fg=theme.PENCIL,
            anchor="w",
        )
        self.info_label.pack(side="left")
        self.player_label = tk.Label(
            header, text="", font=fonts["body"], bg=theme.PAPER, fg=theme.INK,
            anchor="e",
        )
        self.player_label.pack(side="right")

        # Ruled writing area
        text_font = fonts["sentence"]
        self.ascent = text_font.metrics("ascent")
        self.line_height = int(text_font.metrics("linespace") * LINE_GAP)
        self.canvas = tk.Canvas(
            body, bg=theme.PAPER, highlightthickness=0, cursor="xterm",
            height=self.line_height * MIN_RULED_LINES + 12,
        )
        self.canvas.pack(fill="x", pady=(18, 0))
        self.canvas.bind("<Configure>", lambda e: self._layout())
        self.canvas.bind("<Button-1>", lambda e: self.entry.focus_set())

        # Teaching note for the current sentence (blank for plain sentences)
        self.note_label = tk.Label(
            body, text="", font=fonts["note"], bg=theme.PAPER, fg=theme.INK_HOVER,
            anchor="w", justify="left",
        )
        self.note_label.pack(fill="x", pady=(6, 0))
        body.bind("<Configure>", lambda e: self.note_label.config(wraplength=e.width))

        # The entry is off-screen: it only collects keystrokes and editing
        # (Backspace, Ctrl+Backspace) while the canvas shows the result.
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_var, takefocus=1)
        self.entry.place(x=-2000, y=0, width=10)
        self.entry_var.trace_add("write", lambda *a: self._on_input())
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Tab>", self._on_tab)
        self.entry.bind("<<Paste>>", lambda e: "break")
        self.entry.bind("<FocusIn>", lambda e: self._paint_focus(True))
        self.entry.bind("<FocusOut>", lambda e: self._paint_focus(False))
        # After time runs out the entry is disabled and focus moves to the page.
        self.bind("<Return>", lambda e: self.retry_sentence() if self.timed_out else None)
        self.bind("<Tab>", self._on_tab)

        # Live numbers
        stats = tk.Frame(body, bg=theme.PAPER)
        stats.pack(fill="x", pady=(26, 0))
        self.wpm_value = self._stat(stats, "words per minute")
        self.accuracy_value = self._stat(stats, "accuracy")
        self.time_value = self._stat(stats, "seconds")

        self.timer_bar = tk.Canvas(body, bg=theme.PAPER_DEEP, height=4, highlightthickness=0)
        self.timer_fill = self.timer_bar.create_rectangle(0, 0, 0, 4, fill=theme.INK, width=0)

        self.status_label = tk.Label(
            body, text="", font=fonts["body"], bg=theme.PAPER, fg=theme.PENCIL,
            anchor="w", justify="left",
        )
        self.status_label.pack(fill="x", pady=(18, 0))

        self.actions = tk.Frame(body, bg=theme.PAPER)
        self.actions.pack(anchor="w", pady=(12, 0))
        self.next_button = FlatButton(self.actions, fonts, "Next sentence", self.new_sentence)
        self.next_button.pack(side="left")
        self.retry_button = FlatButton(
            self.actions, fonts, "Try this one again", self.retry_sentence, kind="secondary"
        )

    def _stat(self, parent, caption):
        block = tk.Frame(parent, bg=theme.PAPER)
        block.pack(side="left", padx=(0, 56))
        value = tk.Label(block, text="0", font=self.fonts["stat"], bg=theme.PAPER,
                         fg=theme.INK, anchor="w")
        value.pack(anchor="w")
        tk.Label(block, text=caption, font=self.fonts["label"], bg=theme.PAPER,
                 fg=theme.PENCIL, anchor="w").pack(anchor="w")
        return value

    # ------------------------------------------------------------------ round

    def refresh(self):
        self.player_label.config(text=f"Playing as {self.app.player_name}")
        self.new_sentence()

    def _cancel_timers(self):
        for job in (self.timer_job, self.clock_job):
            if job is not None:
                self.after_cancel(job)
        self.timer_job = None
        self.clock_job = None

    def new_sentence(self):
        category = self.app.sentence_type
        level = self.app.difficulty
        sentence, note = pick_sentence(category, level)
        self.current_sentence = format_sentence(
            sentence,
            level,
            punctuation=self.app.punctuation_enabled,
            capitals=self.app.capitals_enabled,
        )
        self.time_limit = get_time_limit(category, level) if self.app.timer_enabled else None

        details = [f"{category}, {level}"]
        if self.time_limit is not None:
            details.append(f"{self.time_limit}-second timer")
        if level == BEGINNER_LEVEL or not self.app.punctuation_enabled:
            details.append("no punctuation")
        if not self.app.capitals_enabled:
            details.append("lowercase")
        self.info_label.config(text=", ".join(details))
        self.note_label.config(text=note)
        self._reset_round()

    def retry_sentence(self):
        self._reset_round()

    def _reset_round(self):
        self._cancel_timers()
        self.start_time = None
        self.finished = False
        self.timed_out = False
        self.remaining = self.time_limit
        self.keystrokes = 0
        self.errors = 0
        self._last_typed = ""
        self.entry.config(state="normal")
        self.entry_var.set("")
        self.entry.focus_set()

        self._layout()
        self._show_numbers(0, None, 0.0)
        self.time_value.config(fg=theme.INK)
        if self.time_limit is not None:
            self.timer_bar.pack(fill="x", pady=(14, 0), before=self.status_label)
            self.timer_bar.itemconfig(self.timer_fill, fill=theme.INK)
            self.time_value.config(text=str(self.time_limit))
            self.after_idle(lambda: self._paint_timer_bar(1.0))
        else:
            self.timer_bar.pack_forget()
        self.status_label.config(
            text="The clock starts with your first key. Tab skips to another sentence.",
            fg=theme.PENCIL,
        )
        self.retry_button.pack_forget()
        self.next_button.set_text("Skip sentence")

    # ---------------------------------------------------------------- drawing

    def _layout(self):
        """Wrap the sentence onto the ruled lines, one canvas item per char."""
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 200)
        font = self.fonts["sentence"]

        self.cursor_rect = canvas.create_rectangle(0, 0, 0, 0, fill=theme.HIGHLIGHT, width=0)

        # Greedy word wrap using measured character widths.
        positions = []
        x, line = 0, 0
        words = self.current_sentence.split(" ")
        for w_idx, word in enumerate(words):
            word_width = font.measure(word)
            if x > 0 and x + word_width > width:
                x, line = 0, line + 1
            for ch in word:
                positions.append((x, line, font.measure(ch)))
                x += font.measure(ch)
            if w_idx < len(words) - 1:
                space = font.measure(" ")
                positions.append((x, line, space))
                x += space

        lines = max(line + 2, MIN_RULED_LINES)
        canvas.config(height=self.line_height * lines + 12)
        for i in range(lines):
            y = (i + 1) * self.line_height
            canvas.create_line(0, y, width, y, fill=theme.RULE)
        canvas.tag_raise(self.cursor_rect)

        self._char_items = []
        for (cx, ln, cw), ch in zip(positions, self.current_sentence):
            baseline = (ln + 1) * self.line_height - 6
            top = baseline - self.ascent
            mark = canvas.create_rectangle(cx, top - 2, cx + cw, baseline + 8,
                                           fill="", width=0)
            text = canvas.create_text(cx, top, text=ch, anchor="nw", font=font,
                                      fill=theme.PENCIL)
            self._char_items.append((mark, text, cx, top, cw, baseline))
        self._paint_text()

    def _paint_text(self):
        typed = self.entry_var.get()
        canvas = self.canvas
        for i, (mark, text, cx, top, cw, baseline) in enumerate(self._char_items):
            if i < len(typed):
                if typed[i] == self.current_sentence[i]:
                    canvas.itemconfig(text, fill=theme.INK)
                    canvas.itemconfig(mark, fill="")
                else:
                    canvas.itemconfig(text, fill=theme.MARGIN)
                    canvas.itemconfig(mark, fill=theme.MARGIN_TINT)
            else:
                canvas.itemconfig(text, fill=theme.PENCIL)
                canvas.itemconfig(mark, fill="")

        pos = len(typed)
        if pos < len(self._char_items) and not (self.finished or self.timed_out):
            _, _, cx, top, cw, baseline = self._char_items[pos]
            canvas.coords(self.cursor_rect, cx, top - 2, cx + cw, baseline + 8)
        else:
            canvas.coords(self.cursor_rect, 0, 0, 0, 0)
        self._paint_focus(self.focus_get() is self.entry)

    def _paint_focus(self, focused):
        if not self._char_items:
            return
        self.canvas.itemconfig(
            self.cursor_rect, fill=theme.HIGHLIGHT if focused else theme.PAPER_DEEP
        )
        if not focused and not (self.finished or self.timed_out) and self.winfo_ismapped():
            self.status_label.config(text="Click the sentence to keep typing.",
                                     fg=theme.MARGIN)
        elif focused and self.status_label.cget("fg") == theme.MARGIN \
                and not (self.finished or self.timed_out):
            self.status_label.config(
                text="Backspace fixes a mistake. Tab skips to another sentence.",
                fg=theme.PENCIL,
            )

    def _show_numbers(self, wpm, accuracy, elapsed):
        self.wpm_value.config(text=f"{wpm:.0f}")
        self.accuracy_value.config(text="-" if accuracy is None else f"{accuracy:.0f}%")
        if self.time_limit is None:
            self.time_value.config(text=f"{elapsed:.1f}")

    def _paint_timer_bar(self, fraction):
        width = self.timer_bar.winfo_width()
        self.timer_bar.coords(self.timer_fill, 0, 0, width * max(fraction, 0), 4)
        low = fraction <= LOW_TIME_FRACTION
        self.timer_bar.itemconfig(self.timer_fill, fill=theme.MARGIN if low else theme.INK)
        self.time_value.config(fg=theme.MARGIN if low else theme.INK)

    # ----------------------------------------------------------------- timing

    def _tick(self):
        if self.finished or self.timed_out:
            return
        self.remaining -= 1
        self.time_value.config(text=str(max(self.remaining, 0)))
        self._paint_timer_bar(self.remaining / self.time_limit)
        if self.remaining <= 0:
            self.timed_out = True
            self._cancel_timers()
            self.entry.config(state="disabled")
            self._paint_text()
            self.status_label.config(
                text="Time is up. Press Enter to try this sentence again, or Tab for a new one.",
                fg=theme.MARGIN,
            )
            self.next_button.set_text("New sentence")
            self.retry_button.pack(side="left", padx=(12, 0))
            self.focus_set()
            return
        self.timer_job = self.after(1000, self._tick)

    def _clock(self):
        """Refresh live WPM and elapsed time between keystrokes."""
        if self.finished or self.timed_out or self.start_time is None:
            return
        self._update_stats()
        self.clock_job = self.after(200, self._clock)

    def _update_stats(self):
        typed = self.entry_var.get()
        elapsed = time.time() - self.start_time if self.start_time else 0
        correct = sum(1 for a, b in zip(typed, self.current_sentence) if a == b)
        wpm = (correct / 5) / (elapsed / 60) if elapsed > 1 else 0
        accuracy = ((self.keystrokes - self.errors) / self.keystrokes * 100
                    if self.keystrokes else None)
        self._show_numbers(wpm, accuracy, elapsed)

    # ------------------------------------------------------------------ input

    def _on_enter(self, event):
        if self.finished:
            self.new_sentence()
        return "break"

    def _on_tab(self, event):
        self.new_sentence()
        return "break"

    def _on_input(self):
        if self.finished or self.timed_out:
            return
        typed = self.entry_var.get()
        target = self.current_sentence

        if len(typed) > len(target):
            self.entry_var.set(typed[:len(target)])
            return

        # Count every newly typed character; a wrong one stays counted as an
        # error even after it is corrected, so accuracy reflects real slips.
        if len(typed) > len(self._last_typed):
            for i in range(len(self._last_typed), len(typed)):
                self.keystrokes += 1
                if typed[i] != target[i]:
                    self.errors += 1
        self._last_typed = typed

        if self.start_time is None and typed:
            self.start_time = time.time()
            self.next_button.set_text("Skip sentence")
            self.clock_job = self.after(200, self._clock)
            if self.time_limit is not None:
                self.timer_job = self.after(1000, self._tick)

        self._paint_text()
        self._update_stats()

        if typed == target:
            self._finish()

    def _finish(self):
        self.finished = True
        self._cancel_timers()
        target = self.current_sentence
        elapsed = time.time() - self.start_time
        wpm = (len(target) / 5) / (elapsed / 60)
        accuracy = (self.keystrokes - self.errors) / self.keystrokes * 100
        self._paint_text()
        self.wpm_value.config(text=f"{wpm:.0f}")
        self.accuracy_value.config(text=f"{accuracy:.0f}%")
        if self.time_limit is None:
            self.time_value.config(text=f"{elapsed:.1f}")

        previous_best = db.get_personal_best(self.app.player_id, self.app.difficulty)
        self.app.record_session(
            difficulty=self.app.difficulty,
            sentence=target,
            wpm=wpm,
            accuracy=accuracy,
            elapsed_seconds=elapsed,
            score=wpm * accuracy / 100,
        )

        if previous_best is None:
            verdict = "Your first saved round on this difficulty."
        elif wpm > previous_best:
            verdict = f"New personal best, up from {previous_best:.0f} wpm."
        else:
            verdict = f"Your best on {self.app.difficulty} is {previous_best:.0f} wpm."
        mistakes = "no mistakes" if self.errors == 0 else (
            "1 mistake" if self.errors == 1 else f"{self.errors} mistakes")
        self.status_label.config(
            text=f"Finished in {elapsed:.1f} seconds with {mistakes}. {verdict} "
                 "Press Enter for the next sentence.",
            fg=theme.INK,
        )
        self.next_button.set_text("Next sentence")
        self.retry_button.pack(side="left", padx=(12, 0))
