"""Interfaz moderna de Vinilo basada en CustomTkinter.

La lógica de descargas se reutiliza desde gui.App para evitar duplicar
el motor, historial, ajustes y manejo de eventos.
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from gui import App as BaseApp
import theme


class ModernApp(BaseApp):
    def _build(self):
        ctk.set_appearance_mode("dark" if self.cfg["theme"] == "dark" else "light")
        ctk.set_default_color_theme("dark-blue")
        self.colors = {
            "bg": "#171817", "panel": "#222421", "panel2": "#2b2d29",
            "field": "#30322e", "text": "#f3f1eb", "muted": "#aaa99f",
            "gold": "#c6a66a", "gold_hover": "#d9bb80", "line": "#3a3c36",
            "green": "#8fae8a",
        }
        c = self.colors
        self.root.configure(bg=c["bg"])

        shell = ctk.CTkFrame(self.root, fg_color=c["bg"], corner_radius=0)
        shell.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(shell, bg=c["bg"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(shell, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        main = ctk.CTkFrame(self.canvas, fg_color=c["bg"], corner_radius=0)
        self.main_window = self.canvas.create_window((0, 0), window=main, anchor="nw")
        main.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.main_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._mousewheel)
        main.grid_columnconfigure(0, weight=1)
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=26, pady=24)
        content.grid_columnconfigure(0, weight=1)

        # Marca y cabecera tipo aplicación musical.
        head = ctk.CTkFrame(content, fg_color="transparent")
        head.pack(fill="x", pady=(0, 22))
        brand = ctk.CTkFrame(head, fg_color="transparent")
        brand.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(brand, text="VINILO", font=("Segoe UI", 29, "bold"), text_color=c["text"]).pack(anchor="w")
        ctk.CTkLabel(brand, text="TU COLECCIÓN. TU RITMO.", font=("Segoe UI", 10, "bold"), text_color=c["gold"]).pack(anchor="w", pady=(1, 0))
        ctk.CTkLabel(head, text="●  LISTO PARA DESCARGAR", font=("Segoe UI", 10, "bold"), text_color=c["green"], fg_color=c["panel"], corner_radius=18, width=205, height=36).pack(side="right", anchor="n", pady=5)

        # Zona destacada: portada grande y formulario integrado.
        hero = ctk.CTkFrame(content, fg_color=c["panel"], corner_radius=22, border_width=1, border_color=c["line"])
        hero.pack(fill="x", pady=(0, 16))
        hero.grid_columnconfigure(1, weight=1)
        cover_wrap = ctk.CTkFrame(hero, fg_color=c["panel2"], corner_radius=17, width=190, height=190)
        cover_wrap.grid(row=0, column=0, rowspan=2, padx=18, pady=18, sticky="nw")
        cover_wrap.grid_propagate(False)
        self.preview_label = ctk.CTkLabel(cover_wrap, text="♫\n\nSIN PORTADA", font=("Segoe UI", 17, "bold"), text_color=c["muted"], fg_color="transparent", justify="center")
        self.preview_label.pack(fill="both", expand=True, padx=8, pady=8)
        hero_info = ctk.CTkFrame(hero, fg_color="transparent")
        hero_info.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(22, 0))
        ctk.CTkLabel(hero_info, text="AÑADIR A TU COLECCIÓN", font=("Segoe UI", 10, "bold"), text_color=c["gold"]).pack(anchor="w", pady=(0, 7))
        self.preview_title = ctk.CTkLabel(hero_info, text="¿Qué quieres guardar hoy?", font=("Segoe UI", 20, "bold"), text_color=c["text"], anchor="w", justify="left", wraplength=560)
        self.preview_title.pack(anchor="w", fill="x")
        self.preview_hint = ctk.CTkLabel(hero_info, text="Pega un enlace de audio, vídeo o una playlist.", font=("Segoe UI", 11), text_color=c["muted"], anchor="w", justify="left", wraplength=560)
        self.preview_hint.pack(anchor="w", pady=(6, 13))
        linkrow = ctk.CTkFrame(hero, fg_color="transparent")
        linkrow.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=(0, 20))
        linkrow.grid_columnconfigure(0, weight=1)
        self.url = tk.StringVar()
        entry = ctk.CTkEntry(linkrow, textvariable=self.url, height=43, corner_radius=13, border_width=1, border_color=c["line"], fg_color=c["field"], text_color=c["text"], placeholder_text="Pega aquí el enlace…")
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<Return>", lambda _e: self.add_from_entry())
        ctk.CTkButton(linkrow, text="＋ Agregar", height=43, corner_radius=13, fg_color=c["gold"], hover_color=c["gold_hover"], text_color="#171717", font=("Segoe UI", 11, "bold"), command=self.add_from_entry).grid(row=0, column=1, padx=(0, 7))
        ctk.CTkButton(linkrow, text="Pegar varios", height=43, corner_radius=13, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.paste_many).grid(row=0, column=2)
        entry.focus()

        # Ajustes como chips y controles de bordes suaves.
        settings_card = ctk.CTkFrame(content, fg_color=c["panel"], corner_radius=20, border_width=1, border_color=c["line"])
        settings_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(settings_card, text="PREFERENCIAS", font=("Segoe UI", 11, "bold"), text_color=c["gold"]).pack(anchor="w", padx=18, pady=(16, 10))
        self.mode = tk.StringVar(value=self.cfg["mode"])
        self.quality = tk.StringVar(value=self.cfg["quality"])
        self.audio_format = tk.StringVar(value=self.cfg["audio_format"])
        self.video_audio = tk.StringVar(value=self.cfg["video_audio"])
        self.theme_mode = tk.StringVar(value=self.cfg["theme"])
        grid = ctk.CTkFrame(settings_card, fg_color="transparent")
        grid.pack(fill="x", padx=18, pady=(0, 16))
        for col in range(3): grid.grid_columnconfigure(col, weight=1, uniform="pref")
        self._modern_option(grid, 0, 0, "Contenido", self.mode, list({"Automático": "auto", "Audio": "audio", "Video": "video"}), self._on_option)
        self._modern_option(grid, 0, 1, "Calidad", self.quality, __import__("downloader").QUALITIES, self._on_option)
        self._modern_option(grid, 0, 2, "Formato de audio", self.audio_format, __import__("downloader").AUDIO_FORMATS, self._on_option)
        self._modern_option(grid, 1, 0, "Audio en vídeo", self.video_audio, __import__("downloader").VIDEO_AUDIO_OPTIONS, self._on_option)
        self._modern_option(grid, 1, 1, "Apariencia", self.theme_mode, ["dark", "light"], self.change_theme)
        destbox = ctk.CTkFrame(grid, fg_color="transparent")
        destbox.grid(row=1, column=2, sticky="ew", padx=7, pady=(12, 0))
        ctk.CTkLabel(destbox, text="Carpeta de destino", text_color=c["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 6))
        self.dest = tk.StringVar(value=self.cfg["dest"])
        destline = ctk.CTkFrame(destbox, fg_color="transparent")
        destline.pack(fill="x")
        self.dest_btn = ctk.CTkButton(destline, text="Elegir carpeta", height=34, corner_radius=10, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.choose_dest)
        self.dest_btn.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(destline, text="↗", width=38, height=34, corner_radius=10, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.open_dest).pack(side="left", padx=(6, 0))

        # Cola visual con la tabla completa para mantener selección y teclado.
        queuehead = ctk.CTkFrame(content, fg_color="transparent")
        queuehead.pack(fill="x", pady=(2, 9))
        ctk.CTkLabel(queuehead, text="A CONTINUACIÓN", font=("Segoe UI", 17, "bold"), text_color=c["text"]).pack(side="left")
        ctk.CTkButton(queuehead, text="Limpiar terminados", height=34, corner_radius=11, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.clear_finished).pack(side="right")
        ctk.CTkButton(queuehead, text="Quitar", height=34, corner_radius=11, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.remove_selected).pack(side="right", padx=(0, 7))
        tableframe = ctk.CTkFrame(content, fg_color=c["panel"], corner_radius=17, border_width=1, border_color=c["line"])
        tableframe.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tableframe, columns=("tipo", "titulo", "estado"), show="headings", selectmode="extended", height=6)
        for col, title, width, stretch in (("tipo", "TIPO", 105, False), ("titulo", "TÍTULO / ENLACE", 360, True), ("estado", "ESTADO", 155, False)):
            self.tree.heading(col, text=title, anchor="w")
            self.tree.column(col, width=width, stretch=stretch, anchor="w")
        style = ttk.Style(self.root)
        style.configure("Treeview", background=c["panel"], fieldbackground=c["panel"], foreground=c["text"], borderwidth=0, rowheight=40, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=c["panel2"], foreground=c["muted"], relief="flat", padding=10, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#51452e")], foreground=[("selected", c["text"])])
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        self.tree.bind("<Delete>", lambda _e: self.remove_selected())

        # Reproductor de progreso fijo dentro de una tarjeta amplia.
        player = ctk.CTkFrame(content, fg_color=c["panel"], corner_radius=20, border_width=1, border_color=c["line"])
        player.pack(fill="x", pady=(16, 0))
        self.status = tk.StringVar(value="Listo para descargar.")
        statusrow = ctk.CTkFrame(player, fg_color="transparent")
        statusrow.pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(statusrow, text="ESTADO", font=("Segoe UI", 10, "bold"), text_color=c["gold"]).pack(side="left")
        ctk.CTkLabel(statusrow, textvariable=self.status, font=("Segoe UI", 11), text_color=c["text"]).pack(side="left", padx=(12, 0))
        self.progress = ctk.CTkProgressBar(player, height=8, corner_radius=8, progress_color=c["gold"], fg_color=c["line"])
        self.progress.pack(fill="x", padx=18, pady=(0, 14))
        self.progress.set(0)
        controls = ctk.CTkFrame(player, fg_color="transparent")
        controls.pack(fill="x", padx=18, pady=(0, 17))
        self.download_btn = ctk.CTkButton(controls, text="↓  Descargar", height=42, corner_radius=13, fg_color=c["gold"], hover_color=c["gold_hover"], text_color="#171717", font=("Segoe UI", 11, "bold"), command=self.start_download)
        self.download_btn.pack(side="left")
        self.cancel_btn = ctk.CTkButton(controls, text="Cancelar", height=42, corner_radius=13, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], state="disabled", command=self.cancel)
        self.cancel_btn.pack(side="left", padx=(8, 0))
        ctk.CTkButton(controls, text="Actualizar yt-dlp", height=42, corner_radius=13, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.start_update).pack(side="left", padx=(8, 0))
        ctk.CTkButton(controls, text="Historial", height=42, corner_radius=13, fg_color=c["panel2"], hover_color=c["line"], text_color=c["text"], command=self.show_history).pack(side="left", padx=(8, 0))
        ctk.CTkButton(controls, text="Salir", height=42, corner_radius=13, fg_color="transparent", hover_color=c["line"], text_color=c["muted"], command=self.on_close).pack(side="right")

        ctk.CTkLabel(content, text="REGISTRO DE ACTIVIDAD", font=("Segoe UI", 10, "bold"), text_color=c["gold"]).pack(anchor="w", pady=(19, 7))
        self.log = ctk.CTkTextbox(content, height=105, corner_radius=14, border_width=1, border_color=c["line"], fg_color=c["panel"], text_color=c["muted"], font=("Consolas", 10), wrap="word")
        self.log.pack(fill="x")
        self.log.configure(state="disabled")
        self.add_log("Vinilo iniciado.")

    def _modern_option(self, parent, row, col, label, variable, values, callback):
        c = self.colors
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=row, column=col, sticky="ew", padx=7, pady=(0, 12) if row == 0 else (0, 0))
        ctk.CTkLabel(box, text=label, text_color=c["muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 6))
        widget = ctk.CTkOptionMenu(box, variable=variable, values=values, height=36, corner_radius=10, fg_color=c["panel2"], button_color=c["field"], button_hover_color=c["line"], dropdown_fg_color=c["panel"], text_color=c["text"], font=("Segoe UI", 10), command=lambda _v: callback())
        widget.pack(fill="x")

    def change_theme(self, _event=None):
        self._save_settings()
        # CustomTkinter conserva el modo elegido; los tonos de la marca se mantienen
        # coherentes para no provocar un destello o reconstrucción de la ventana.
        ctk.set_appearance_mode("dark" if self.theme_mode.get() == "dark" else "light")
        self.add_log("Apariencia guardada: " + ("oscura" if self.theme_mode.get() == "dark" else "clara") + ". Reinicia Vinilo para aplicar el cambio completo.")

    def add_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _ev_preview(self, job_id, url, image):
        if not self.root.winfo_exists() or self.preview_url != url:
            return
        try:
            from PIL import Image
            self.preview_image = ctk.CTkImage(light_image=image, dark_image=image, size=(174, 174))
            self.preview_label.configure(image=self.preview_image, text="")
            self.preview_hint.configure(text="Miniatura del contenido seleccionado")
        except Exception:
            self.preview_label.configure(image=None, text="♫\nSIN PORTADA")
            self.preview_hint.configure(text="Miniatura no disponible")

    def _ev_preview_error(self, job_id, url, error):
        if self.preview_url == url:
            self.preview_label.configure(image=None, text="♫\nSIN PORTADA")
            self.preview_hint.configure(text="La miniatura no pudo cargarse.")
\n    def _selection_changed(self, _event=None):\n        selection = self.tree.selection()\n        if not selection:\n            return\n        job = self.queue.get(int(selection[0]))\n        if not job:\n            return\n        self.preview_title.configure(text=job.title or job.url)\n        if job.thumbnail and job.thumbnail != self.preview_url:\n            self.preview_url = job.thumbnail\n            self.preview_label.configure(image=None, text="♫\\nCARGANDO…")\n            threading.Thread(target=self._load_preview, args=(job.id, job.thumbnail), daemon=True).start()\n        elif not job.thumbnail:\n            self.preview_label.configure(image=None, text="♫\\nSIN PORTADA")\n            self.preview_hint.configure(text="No hay miniatura disponible para este enlace.")\n