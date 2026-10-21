"""
Exercise-book look shared across all screens: cool ruled paper, navy ink,
a red margin line, pencil grey for text not yet typed and a highlighter
for the next character.
"""

from tkinter import font as tkfont
from tkinter import ttk

PAPER = "#EEF2F3"
PAPER_DEEP = "#E1E8EB"
RULE = "#B9CCE0"
MARGIN = "#D9465B"
MARGIN_TINT = "#F6D5DA"
INK = "#1D2F5C"
INK_HOVER = "#2C4580"
PENCIL = "#8A93A3"
HIGHLIGHT = "#F2E35C"

# The red margin sits this far from the left edge of every screen; content
# starts at CONTENT_X so the margin column stays free for navigation.
MARGIN_X = 88
CONTENT_X = 120

# Classic typographic scale (Bringhurst): 10 / 12 / 14 / 18 / 24 / 36 / 48.
UI_FAMILIES = ("Bahnschrift", "Segoe UI", "Helvetica Neue", "DejaVu Sans", "Helvetica")
TEXT_FAMILIES = ("Sitka Text", "Georgia", "Cambria", "DejaVu Serif", "Times")
DISPLAY_FAMILIES = ("Sitka Heading", "Georgia", "Cambria", "DejaVu Serif", "Times")


def _first_available(candidates):
    installed = set(tkfont.families())
    for family in candidates:
        if family in installed:
            return family
    return candidates[-1]


def build_fonts():
    """Create named fonts once the Tk root exists."""
    ui = _first_available(UI_FAMILIES)
    text = _first_available(TEXT_FAMILIES)
    display = _first_available(DISPLAY_FAMILIES)
    return {
        "display": tkfont.Font(family=display, size=36),
        "heading": tkfont.Font(family=display, size=24),
        "sentence": tkfont.Font(family=text, size=24),
        "note": tkfont.Font(family=text, size=12, slant="italic"),
        "body": tkfont.Font(family=ui, size=12),
        "label": tkfont.Font(family=ui, size=10),
        "button": tkfont.Font(family=ui, size=12, weight="bold"),
        "stat": tkfont.Font(family=ui, size=36, weight="bold"),
        "stat_small": tkfont.Font(family=ui, size=18, weight="bold"),
    }


def build_style(root, fonts):
    """Style the few ttk widgets still in use (Combobox, Checkbutton)."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=PAPER)

    style.configure(
        "TCombobox", fieldbackground=PAPER, background=PAPER, foreground=INK,
        arrowcolor=INK, bordercolor=INK, lightcolor=PAPER, darkcolor=PAPER,
        padding=(6, 6), selectbackground=HIGHLIGHT, selectforeground=INK,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", PAPER), ("focus", PAPER)],
        bordercolor=[("focus", MARGIN)],
        arrowcolor=[("active", MARGIN)],
        background=[("active", PAPER)],
    )
    root.option_add("*TCombobox*Listbox.background", PAPER)
    root.option_add("*TCombobox*Listbox.foreground", INK)
    root.option_add("*TCombobox*Listbox.selectBackground", HIGHLIGHT)
    root.option_add("*TCombobox*Listbox.selectForeground", INK)
    root.option_add("*TCombobox*Listbox.font", fonts["body"])

    style.configure(
        "TCheckbutton", background=PAPER, foreground=INK, font=fonts["body"],
        indicatorbackground=PAPER, indicatorforeground=PAPER,
        upperbordercolor=INK, lowerbordercolor=INK, focuscolor=MARGIN,
        padding=(0, 4),
    )
    style.map(
        "TCheckbutton",
        background=[("active", PAPER)],
        indicatorbackground=[("disabled", PAPER_DEEP), ("selected", INK)],
        foreground=[("disabled", PENCIL)],
        upperbordercolor=[("disabled", PENCIL)],
        lowerbordercolor=[("disabled", PENCIL)],
    )

    return style
