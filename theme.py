"""Temas de Vinilo: minimalismo editorial, crema, carbón y acentos vivos."""
from tkinter import ttk

# Paleta inspirada en el diseño de referencia, adaptada para mantener legibilidad.
PALETTES = {
    "dark": {
        "BG": "#414141", "PANEL": "#075653", "FIELD": "#262629",
        "BORDER": "#555555", "FG": "#fff8e9", "MUTED": "#c8c4bd",
        "ACCENT": "#1717f5", "ACCENT_HOVER": "#3535ff",
        "SELECT": "#176f6b",
    },
    "light": {
        "BG": "#414141", "PANEL": "#fff1d6", "FIELD": "#ffffff",
        "BORDER": "#d8cbb8", "FG": "#191919", "MUTED": "#77736e",
        "ACCENT": "#1717f5", "ACCENT_HOVER": "#3535ff",
        "SELECT": "#d9ddff",
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
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    s.configure(".", background=BG, foreground=FG, fieldbackground=FIELD,
                bordercolor=BORDER, lightcolor=BG, darkcolor=BG,
                troughcolor=PANEL, focuscolor=ACCENT, font=FONT)
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=PANEL)
    s.configure("TLabel", background=BG, foreground=FG)
    s.configure("Card.TLabel", background=PANEL, foreground=FG)
    s.configure("Title.TLabel", font=("Segoe UI", 27, "bold"))
    s.configure("Muted.TLabel", foreground=MUTED)

    # Botones sobrios y redondez visual aproximada con padding amplio de ttk.
    s.configure("TButton", background=FIELD, foreground="#ffffff",
                bordercolor=FIELD, padding=(14, 9), relief="flat")
    s.map("TButton", background=[("disabled", BORDER), ("active", BORDER)],
          foreground=[("disabled", MUTED)])
    s.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                bordercolor=ACCENT, padding=(24, 11),
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map("Accent.TButton",
          background=[("disabled", BORDER), ("active", ACCENT_HOVER)],
          bordercolor=[("active", ACCENT_HOVER)])

    s.configure("TEntry", fieldbackground=FIELD, foreground=FG,
                insertcolor=FG, bordercolor=BORDER, padding=10, relief="flat")
    s.map("TEntry", bordercolor=[("focus", ACCENT)])
    s.configure("TCombobox", fieldbackground=FIELD, background=FIELD,
                foreground=FG, arrowcolor=FG, bordercolor=BORDER, padding=9)
    s.map("TCombobox", fieldbackground=[("readonly", FIELD)],
          selectbackground=[("readonly", FIELD)],
          selectforeground=[("readonly", FG)],
          bordercolor=[("focus", ACCENT)])

    s.configure("TProgressbar", troughcolor=PANEL, background=ACCENT,
                bordercolor=PANEL, thickness=9)
    s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                foreground=FG, bordercolor=BORDER, borderwidth=0, rowheight=36,
                font=("Segoe UI", 10))
    s.map("Treeview", background=[("selected", p["SELECT"])],
          foreground=[("selected", FG)])
    s.configure("Treeview.Heading", background=FIELD, foreground=FG,
                relief="flat", padding=10, font=("Segoe UI", 9, "bold"))
    s.configure("TScrollbar", background=BORDER, troughcolor=BG,
                bordercolor=BG, arrowcolor=FG)
    s.configure("TLabelframe", background=BG, foreground=FG,
                bordercolor=BORDER, relief="flat", padding=8)
    s.configure("TLabelframe.Label", background=BG, foreground=FG,
                font=("Segoe UI", 10, "bold"))


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
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
            )
    except Exception:
        pass
