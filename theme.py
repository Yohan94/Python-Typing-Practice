"""
Catppuccin Mocha color palette, fonts, and ttk styling shared across all tabs.
"""

from tkinter import font as tkfont
from tkinter import ttk

BG = "#1e1e2e"
SURFACE = "#313244"
SURFACE2 = "#45475a"
TEXT = "#cdd6f4"
TITLE = "#f5e0dc"
SUBTEXT = "#6c7086"
GREEN = "#a6e3a1"
RED = "#f38ba8"
RED_HOVER = "#eba0ac"
BLUE = "#89b4fa"
BLUE_HOVER = "#74c7ec"
TEAL = "#94e2d5"
YELLOW = "#f9e2af"


def build_fonts():
    return {
        "title": tkfont.Font(family="Helvetica", size=20, weight="bold"),
        "text": tkfont.Font(family="Consolas", size=18),
        "stats": tkfont.Font(family="Helvetica", size=13),
        "mono": tkfont.Font(family="Consolas", size=13),
    }


def build_style(root):
    """Configure ttk widgets (Notebook, Treeview, Combobox, Radiobutton) to
    match the Catppuccin Mocha palette used by the plain tk widgets."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure(
        "TNotebook.Tab", background=SURFACE, foreground=TEXT,
        padding=(16, 8), borderwidth=0, font=("Helvetica", 12)
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BLUE)],
        foreground=[("selected", BG)],
    )

    style.configure(
        "Treeview", background=SURFACE, fieldbackground=SURFACE, foreground=TEXT,
        rowheight=26, borderwidth=0, font=("Helvetica", 11)
    )
    style.configure(
        "Treeview.Heading", background=SURFACE2, foreground=TITLE,
        borderwidth=0, font=("Helvetica", 11, "bold")
    )
    style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", BG)])

    style.configure(
        "TCombobox", fieldbackground=SURFACE2, background=SURFACE2, foreground=TEXT,
        arrowcolor=TEXT, borderwidth=0
    )
    style.configure(
        "TRadiobutton", background=BG, foreground=TEXT, font=("Helvetica", 12)
    )
    style.map("TRadiobutton", background=[("active", BG)], foreground=[("active", BLUE)])

    style.configure(
        "TCheckbutton", background=BG, foreground=TEXT, font=("Helvetica", 12)
    )
    style.map("TCheckbutton", background=[("active", BG)], foreground=[("active", BLUE)])

    style.configure(
        "TButton", background=BLUE, foreground=BG, borderwidth=0,
        padding=(12, 6), font=("Helvetica", 11)
    )
    style.map("TButton", background=[("active", BLUE_HOVER)])

    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT)

    return style
