"""Temas claro y oscuro con una paleta cálida vainilla/café."""
from tkinter import ttk

PALETTES = {
    "dark": {
        "BG": "#211b17", "PANEL": "#2b231e", "FIELD": "#352a23",
        "BORDER": "#514035", "FG": "#f8edda", "MUTED": "#c0ad98",
        "ACCENT": "#c58b55", "ACCENT_HOVER": "#d9a674",
        "SELECT": "#65462f",
    },
    "light": {
        "BG": "#f7f0e4", "PANEL": "#fffaf1", "FIELD": "#fffdf8",
        "BORDER": "#e0d0bb", "FG": "#3d2b20", "MUTED": "#806b58",
        "ACCENT": "#9b6337", "ACCENT_HOVER": "#b77a49",
        "SELECT": "#ead6bd",
    },
}
FONT = ("Segoe UI", 10)
BG, PANEL, FIELD, BORDER, FG, MUTED, ACCENT, ACCENT_HOVER = (
    PALETTES["dark"][k] for k in
    ("BG", "PANEL", "FIELD", "BORDER", "FG", "MUTED", "ACCENT", "ACCENT_HOVER")
)


def apply(root, mode="dark") -> None:
    global BG, PANEL, FIELD, BORDER, FG, MUTED, ACCENT, ACCENT_HOVER
    p = PALETTES.get(mode, PALETTES["dark"])
    BG, PANEL, FIELD, BORDER, FG, MUTED, ACCENT, ACCENT_HOVER = (
        p[k] for k in ("BG", "PANEL", "FIELD", "BORDER", "FG", "MUTED", "ACCENT", "ACCENT_HOVER")
    )
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=BG)
    root.option_add("*TCombobox*Listbox.background", FIELD)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    s.configure(".", background=BG, foreground=FG, fieldbackground=FIELD,
                bordercolor=BORDER, lightcolor=BG, darkcolor=BG,
                troughcolor=PANEL, focuscolor=ACCENT, font=FONT)
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=PANEL)
    s.configure("TLabel", background=BG, foreground=FG)
    s.configure("Card.TLabel", background=PANEL, foreground=FG)
    s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
    s.configure("Muted.TLabel", foreground=MUTED)
    s.configure("TButton", background=PANEL, foreground=FG,
                bordercolor=BORDER, padding=(12, 7))
    s.map("TButton", background=[("disabled", BG), ("active", BORDER)],
          foreground=[("disabled", MUTED)])
    s.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                bordercolor=ACCENT, padding=(22, 9),
                font=("Segoe UI", 10, "bold"))
    s.map("Accent.TButton", background=[("disabled", BORDER), ("active", ACCENT_HOVER)],
          bordercolor=[("active", ACCENT_HOVER)])
    s.configure("TEntry", fieldbackground=FIELD, foreground=FG,
                insertcolor=FG, bordercolor=BORDER, padding=7)
    s.map("TEntry", bordercolor=[("focus", ACCENT)])
    s.configure("TCombobox", fieldbackground=FIELD, background=PANEL,
                foreground=FG, arrowcolor=FG, bordercolor=BORDER, padding=6)
    s.map("TCombobox", fieldbackground=[("readonly", FIELD)],
          selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", FG)],
          bordercolor=[("focus", ACCENT)])
    s.configure("TProgressbar", troughcolor=PANEL, background=ACCENT,
                bordercolor=PANEL, thickness=8)
    s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                foreground=FG, bordercolor=BORDER, borderwidth=0, rowheight=30)
    s.map("Treeview", background=[("selected", p["SELECT"])],
          foreground=[("selected", FG)])
    s.configure("Treeview.Heading", background=BORDER, foreground=FG,
                relief="flat", padding=7, font=("Segoe UI", 9, "bold"))
    s.configure("TScrollbar", background=BORDER, troughcolor=PANEL,
                bordercolor=PANEL, arrowcolor=FG)
    s.configure("TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    s.configure("TLabelframe.Label", background=BG, foreground=FG)


def dark_title_bar(root, mode="dark") -> None:
    """Intenta ajustar la barra de título en Windows."""
    if mode != "dark":
        return
    try:
        import ctypes
        root.update()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(1)
        for attr in (20, 19):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr,
                ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass
