"""Tema sobrio para Vinilo: carbón, grises, blanco y oro suave."""
from tkinter import ttk

PALETTES = {
    "dark": {
        "BG": "#171717", "PANEL": "#222222", "FIELD": "#2b2b2b",
        "BORDER": "#393939", "FG": "#f5f5f3", "MUTED": "#a5a5a0",
        "ACCENT": "#c6a15b", "ACCENT_HOVER": "#d8b873",
        "SELECT": "#51452e", "ON_ACCENT": "#171717",
    },
    "light": {
        "BG": "#f2f2ef", "PANEL": "#ffffff", "FIELD": "#f7f7f5",
        "BORDER": "#deded8", "FG": "#222220", "MUTED": "#777771",
        "ACCENT": "#a8843e", "ACCENT_HOVER": "#947333",
        "SELECT": "#eee4cf", "ON_ACCENT": "#ffffff",
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
        p[k] for k in
        ("BG", "PANEL", "FIELD", "BORDER", "FG", "MUTED", "ACCENT", "ACCENT_HOVER")
    )
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=BG)
    root.option_add("*TCombobox*Listbox.background", FIELD)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", p["ON_ACCENT"])

    s.configure(".", background=BG, foreground=FG, fieldbackground=FIELD,
                bordercolor=BORDER, lightcolor=BG, darkcolor=BG,
                troughcolor=PANEL, focuscolor=ACCENT, font=FONT)
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=PANEL)
    s.configure("TLabel", background=BG, foreground=FG)
    s.configure("Card.TLabel", background=PANEL, foreground=FG)
    s.configure("Title.TLabel", font=("Segoe UI", 30, "bold"),
                foreground=FG, background=BG)
    s.configure("Section.TLabel", font=("Segoe UI", 13, "bold"),
                foreground=FG)
    s.configure("Eyebrow.TLabel", font=("Segoe UI", 9, "bold"),
                foreground=ACCENT)
    s.configure("Muted.TLabel", foreground=MUTED)

    s.configure("TButton", background=FIELD, foreground=FG,
                bordercolor=FIELD, padding=(13, 9), relief="flat",
                font=("Segoe UI", 9))
    s.map("TButton", background=[("disabled", BORDER), ("active", BORDER)],
          foreground=[("disabled", MUTED)])
    s.configure("Accent.TButton", background=ACCENT, foreground=p["ON_ACCENT"],
                bordercolor=ACCENT, padding=(20, 11),
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map("Accent.TButton",
          background=[("disabled", BORDER), ("active", ACCENT_HOVER)],
          foreground=[("disabled", MUTED), ("active", p["ON_ACCENT"])],
          bordercolor=[("active", ACCENT_HOVER)])
    s.configure("TEntry", fieldbackground=FIELD, foreground=FG,
                insertcolor=FG, bordercolor=BORDER, padding=11, relief="flat")
    s.map("TEntry", bordercolor=[("focus", ACCENT)])
    s.configure("TCombobox", fieldbackground=FIELD, background=FIELD,
                foreground=FG, arrowcolor=ACCENT, bordercolor=BORDER, padding=9)
    s.map("TCombobox", fieldbackground=[("readonly", FIELD)],
          selectbackground=[("readonly", FIELD)],
          selectforeground=[("readonly", FG)],
          bordercolor=[("focus", ACCENT)])
    s.configure("TProgressbar", troughcolor=BORDER, background=ACCENT,
                bordercolor=BORDER, thickness=8)
    s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                foreground=FG, bordercolor=BORDER, borderwidth=0,
                rowheight=38, font=("Segoe UI", 10))
    s.map("Treeview", background=[("selected", p["SELECT"])],
          foreground=[("selected", FG)])
    s.configure("Treeview.Heading", background=FIELD, foreground=MUTED,
                relief="flat", padding=11, font=("Segoe UI", 9, "bold"))
    s.map("Treeview.Heading", background=[("active", BORDER)])
    s.configure("TScrollbar", background=BORDER, troughcolor=BG,
                bordercolor=BG, arrowcolor=FG)
    s.configure("TLabelframe", background=PANEL, foreground=FG,
                bordercolor=BORDER, relief="flat", padding=12)
    s.configure("TLabelframe.Label", background=PANEL, foreground=ACCENT,
                font=("Segoe UI", 9, "bold"))


def dark_title_bar(root, mode="dark") -> None:
    """Intenta ajustar la barra de título en Windows."""
    try:
        import ctypes
        root.update()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(1 if mode == "dark" else 0)
        for attr in (20, 19):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
            )
    except Exception:
        pass
