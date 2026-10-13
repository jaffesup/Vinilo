"""Tema oscuro para ttk."""
from tkinter import ttk

BG = "#14161a"
PANEL = "#1c1f26"
FIELD = "#23272f"
BORDER = "#2d323c"
FG = "#e6e8ee"
MUTED = "#8b93a5"
ACCENT = "#7c5cff"
ACCENT_HOVER = "#9277ff"
FONT = ("Segoe UI", 10)


def apply(root) -> None:
    s = ttk.Style(root)
    s.theme_use("clam")
    root.configure(bg=BG)

    # lista desplegable de los Combobox (no es ttk)
    root.option_add("*TCombobox*Listbox.background", FIELD)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    s.configure(".", background=BG, foreground=FG, fieldbackground=FIELD,
                bordercolor=BORDER, lightcolor=BG, darkcolor=BG,
                troughcolor=PANEL, focuscolor=BG, font=FONT)
    s.configure("TFrame", background=BG)
    s.configure("TLabel", background=BG, foreground=FG)
    s.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
    s.configure("Muted.TLabel", foreground=MUTED)

    s.configure("TButton", background=PANEL, foreground=FG,
                bordercolor=BORDER, padding=(14, 8))
    s.map("TButton", background=[("disabled", BG), ("active", BORDER)],
          foreground=[("disabled", MUTED)])

    s.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                bordercolor=ACCENT, padding=(26, 9),
                font=("Segoe UI", 10, "bold"))
    s.map("Accent.TButton",
          background=[("disabled", "#3a3560"), ("active", ACCENT_HOVER)],
          bordercolor=[("disabled", "#3a3560"), ("active", ACCENT_HOVER)],
          foreground=[("disabled", "#8a84b8")])

    s.configure("TEntry", fieldbackground=FIELD, foreground=FG,
                insertcolor=FG, bordercolor=BORDER, padding=6)
    s.map("TEntry", bordercolor=[("focus", ACCENT)],
          fieldbackground=[("readonly", FIELD)],
          foreground=[("readonly", MUTED)])

    s.configure("TCombobox", fieldbackground=FIELD, background=PANEL,
                foreground=FG, arrowcolor=FG, bordercolor=BORDER, padding=5,
                selectbackground=FIELD, selectforeground=FG)
    s.map("TCombobox", fieldbackground=[("readonly", FIELD)],
          selectbackground=[("readonly", FIELD)],
          selectforeground=[("readonly", FG)],
          bordercolor=[("focus", ACCENT)])

    s.configure("TProgressbar", troughcolor=PANEL, background=ACCENT,
                bordercolor=PANEL, lightcolor=ACCENT, darkcolor=ACCENT,
                thickness=8)

    s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                foreground=FG, bordercolor=BORDER, borderwidth=0, rowheight=28)
    s.map("Treeview", background=[("selected", "#3b3470")],
          foreground=[("selected", "#ffffff")])
    s.configure("Treeview.Heading", background=BORDER, foreground=FG,
                relief="flat", padding=6, font=("Segoe UI", 9, "bold"))
    s.map("Treeview.Heading", background=[("active", BORDER)])

    s.configure("TScrollbar", background=BORDER, troughcolor=PANEL,
                bordercolor=PANEL, arrowcolor=FG)
    s.map("TScrollbar", background=[("active", MUTED)])


def dark_title_bar(root) -> None:
    """Barra de título oscura en Windows 10/11 (si falla, no pasa nada)."""
    try:
        import ctypes
        root.update()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(1)
        for attr in (20, 19):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass
