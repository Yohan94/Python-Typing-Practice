"""
Small reusable widgets drawn in the exercise-book style: a page with a red
margin, flat keyboard-focusable buttons, and a segmented chooser.
"""

import tkinter as tk

import theme


class Page(tk.Frame):
    """A full screen of paper with the red margin line down the left.

    Children go into self.body, which starts to the right of the margin.
    self.margin_slot is the column left of the line, used for the back link.
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.PAPER)
        self.app = app
        self.fonts = app.fonts

        self.margin_slot = tk.Frame(self, bg=theme.PAPER)
        self.margin_slot.place(x=0, y=0, width=theme.MARGIN_X, relheight=1)

        tk.Frame(self, bg=theme.MARGIN, width=2).place(
            x=theme.MARGIN_X, y=0, relheight=1
        )

        self.body = tk.Frame(self, bg=theme.PAPER)
        self.body.place(
            x=theme.CONTENT_X, y=0, relwidth=1, width=-(theme.CONTENT_X + 40),
            relheight=1,
        )

    def add_back_link(self, text="Menu"):
        link = LinkButton(
            self.margin_slot, self.fonts, text=f"← {text}",
            command=lambda: self.app.show_screen("menu"),
        )
        link.pack(anchor="e", padx=(0, 10), pady=(28, 0))
        return link


class FlatButton(tk.Frame):
    """A flat button with a visible focus ring; Enter and Space activate it.

    kind="primary" is solid ink, kind="secondary" is outlined.
    """

    def __init__(self, parent, fonts, text, command, kind="primary", width=None):
        super().__init__(parent, bg=parent["bg"], takefocus=1,
                         highlightthickness=2, highlightbackground=parent["bg"],
                         highlightcolor=theme.MARGIN)
        self.command = command
        self.kind = kind
        if kind == "primary":
            self._colors = (theme.INK, theme.PAPER, theme.INK_HOVER)
            inner_border = theme.INK
        else:
            self._colors = (theme.PAPER, theme.INK, theme.PAPER_DEEP)
            inner_border = theme.INK

        self.label = tk.Label(
            self, text=text, font=fonts["button"], bg=self._colors[0],
            fg=self._colors[1], padx=22, pady=10, cursor="hand2",
            highlightthickness=1, highlightbackground=inner_border,
        )
        if width:
            self.label.config(width=width)
        self.label.pack()

        for widget in (self, self.label):
            widget.bind("<Button-1>", self._invoke)
            widget.bind("<Enter>", lambda e: self.label.config(bg=self._colors[2]))
            widget.bind("<Leave>", lambda e: self.label.config(bg=self._colors[0]))
        self.bind("<Return>", self._invoke)
        self.bind("<space>", self._invoke)

    def set_text(self, text):
        self.label.config(text=text)

    def _invoke(self, event=None):
        self.command()
        return "break"


class LinkButton(tk.Label):
    """Plain text action, used for navigation in the margin."""

    def __init__(self, parent, fonts, text, command):
        super().__init__(
            parent, text=text, font=fonts["body"], bg=parent["bg"], fg=theme.INK,
            cursor="hand2", takefocus=1, highlightthickness=2,
            highlightbackground=parent["bg"], highlightcolor=theme.MARGIN,
        )
        self.command = command
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Return>", lambda e: command())
        self.bind("<space>", lambda e: command())
        self.bind("<Enter>", lambda e: self.config(fg=theme.MARGIN))
        self.bind("<Leave>", lambda e: self.config(fg=theme.INK))


class Segmented(tk.Frame):
    """One-of-many chooser drawn as joined boxes.

    Arrow keys move the choice when the control has focus. If `hints` is
    given (option -> callable returning text), the hint for the current
    choice is shown beneath the row.
    """

    def __init__(self, parent, fonts, options, variable, command=None, hints=None):
        super().__init__(parent, bg=parent["bg"])
        self.options = list(options)
        self.variable = variable
        self.command = command
        self.hints = hints or {}

        self.row = tk.Frame(self, bg=theme.INK, takefocus=1,
                            highlightthickness=2, highlightbackground=parent["bg"],
                            highlightcolor=theme.MARGIN)
        self.row.pack(anchor="w")
        self.cells = {}
        for i, option in enumerate(self.options):
            cell = tk.Label(
                self.row, text=option, font=fonts["body"], padx=16, pady=7,
                cursor="hand2",
            )
            cell.grid(row=0, column=i, padx=(1 if i == 0 else 0, 1), pady=1)
            cell.bind("<Button-1>", lambda e, o=option: self.select(o))
            self.cells[option] = cell

        self.hint_label = None
        if hints:
            self.hint_label = tk.Label(
                self, text="", font=fonts["label"], bg=parent["bg"], fg=theme.PENCIL,
                anchor="w", justify="left",
            )
            self.hint_label.pack(anchor="w", pady=(4, 0))

        self.row.bind("<Left>", lambda e: self._step(-1))
        self.row.bind("<Right>", lambda e: self._step(1))
        self.row.bind("<Button-1>", lambda e: self.row.focus_set())
        self.variable.trace_add("write", lambda *a: self._paint())
        self._paint()

    def select(self, option):
        self.row.focus_set()
        self.variable.set(option)
        if self.command:
            self.command()

    def refresh_hint(self):
        self._paint()

    def _step(self, delta):
        current = self.variable.get()
        idx = self.options.index(current) if current in self.options else 0
        self.select(self.options[(idx + delta) % len(self.options)])
        return "break"

    def _paint(self):
        current = self.variable.get()
        for option, cell in self.cells.items():
            if option == current:
                cell.config(bg=theme.INK, fg=theme.PAPER)
            else:
                cell.config(bg=theme.PAPER, fg=theme.INK)
        if self.hint_label is not None:
            hint = self.hints.get(current)
            self.hint_label.config(text=hint() if callable(hint) else (hint or ""))


def field_label(parent, fonts, text):
    """Small pencil label that names a form field, like a printed form."""
    return tk.Label(parent, text=text, font=fonts["label"], bg=parent["bg"],
                    fg=theme.PENCIL, anchor="w")


def format_date(stamp):
    """'2026-10-13T09:05:00' stored in UTC -> '13 Oct 2026, 10:05' local time."""
    from datetime import datetime, timezone
    try:
        moment = datetime.fromisoformat(stamp).replace(tzinfo=timezone.utc).astimezone()
    except (TypeError, ValueError):
        return stamp or ""
    return f"{moment.day} {moment:%b %Y, %H:%M}"


class RuledTable(tk.Frame):
    """A simple table: a header row and data rows separated by ruled lines.

    columns is a list of (heading, width_in_chars, anchor).
    """

    def __init__(self, parent, fonts, columns):
        super().__init__(parent, bg=parent["bg"])
        self.fonts = fonts
        self.columns = columns
        for c, (heading, width, anchor) in enumerate(columns):
            # Keep column widths fixed even when every cell in one is highlighted.
            self.grid_columnconfigure(c, minsize=fonts["body"].measure("0") * width)
            tk.Label(self, text=heading, font=fonts["label"], bg=self["bg"],
                     fg=theme.PENCIL, width=width, anchor=anchor).grid(
                row=0, column=c, sticky="ew", padx=(0, 18), pady=(0, 4))
        tk.Frame(self, bg=theme.INK, height=1).grid(
            row=1, column=0, columnspan=len(columns), sticky="ew")
        self._rows = []

    def set_rows(self, rows, highlight=None, highlight_column=None):
        """rows: list of value tuples. highlight: set of row indexes to mark,
        either the whole row or only highlight_column."""
        for widget in self._rows:
            widget.destroy()
        self._rows = []
        highlight = highlight or set()
        for r, values in enumerate(rows):
            grid_row = 2 + r * 2
            for c, value in enumerate(values):
                heading, width, anchor = self.columns[c]
                marked = r in highlight and highlight_column in (None, c)
                cell = tk.Label(self, text=value, font=self.fonts["body"],
                                bg=theme.HIGHLIGHT if marked else self["bg"],
                                fg=theme.INK, anchor=anchor, pady=2, padx=0 if not marked else 4)
                if not marked:
                    cell.config(width=width)
                # A highlighted cell hugs its text, like a highlighter stroke.
                cell.grid(row=grid_row, column=c, sticky="w" if marked else "ew",
                          padx=(0, 18), pady=4)
                self._rows.append(cell)
            rule = tk.Frame(self, bg=theme.RULE, height=1)
            rule.grid(row=grid_row + 1, column=0, columnspan=len(self.columns), sticky="ew")
            self._rows.append(rule)
