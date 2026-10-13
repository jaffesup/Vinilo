"""Interfaz moderna de Vinilo basada en CustomTkinter.

La lógica de descargas se reutiliza desde gui.App para evitar duplicar
el motor, historial, ajustes y manejo de eventos.
"""
import tkinter as tk
from tkinter import ttk, filedialog
import customtkinter as ctk

from gui import App as BaseApp, MODES
import theme


class ModernApp(BaseApp):
    def _build(self):
        """Shell de navegación inspirado en WinUI; reutiliza la lógica de gui.App."""
        ctk.set_appearance_mode("dark" if self.cfg["theme"] == "dark" else "light")
        ctk.set_default_color_theme("blue")
        self.colors = {
            "bg": "#202020", "panel": "#2b2b2b", "panel2": "#333333",
            "field": "#1b1b1b", "text": "#ffffff", "muted": "#c5c5c5",
            "gold": "#60cdff", "gold_hover": "#8bd8ff", "line": "#414141",
            "green": "#6ccb5f",
        }
        c = self.colors
        self.root.configure(bg=c["bg"])
        self.root.title("Vinilo")
        self.root.geometry("1120x760")
        self.root.minsize(820, 620)

        # Estructura de aplicación: navegación a la izquierda y página a la derecha.
        shell = ctk.CTkFrame(self.root, fg_color=c["bg"], corner_radius=0)
        shell.pack(fill="both", expand=True)
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(shell, width=218, corner_radius=0,
                               fg_color="#191919", border_width=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="◉  VINILO", font=("Segoe UI Variable Display", 22, "bold"),
                     text_color=c["text"]).pack(anchor="w", padx=22, pady=(25, 2))
        ctk.CTkLabel(sidebar, text="DESCARGADOR MULTIMEDIA", font=("Segoe UI", 9, "bold"),
                     text_color=c["muted"]).pack(anchor="w", padx=24, pady=(0, 25))

        self._nav_buttons = {}
        self._pages = {}
        page_host = ctk.CTkFrame(shell, fg_color=c["bg"], corner_radius=0)
        page_host.grid(row=0, column=1, sticky="nsew")
        page_host.grid_rowconfigure(0, weight=1)
        page_host.grid_columnconfigure(0, weight=1)

        def make_page(key):
            if key == "settings":
                page = ctk.CTkScrollableFrame(
                    page_host, fg_color=c["bg"], corner_radius=0,
                    scrollbar_button_color=c["panel2"],
                    scrollbar_button_hover_color=c["line"],
                )
            else:
                page = ctk.CTkFrame(page_host, fg_color=c["bg"], corner_radius=0)
            page.grid(row=0, column=0, sticky="nsew")
            self._pages[key] = page
            return page

        def show_page(key):
            self._active_page = key
            self._pages[key].tkraise()
            for name, button in self._nav_buttons.items():
                selected = name == key
                button.configure(
                    fg_color="#383838" if selected else "transparent",
                    text_color=c["text"] if selected else c["muted"],
                    border_width=3 if selected else 0,
                    border_color=c["gold"] if selected else "#191919",
                )

        for key, label in (("downloads", "↓   Descargas"), ("settings", "⚙   Configuración")):
            button = ctk.CTkButton(
                sidebar, text=label, height=42, corner_radius=6, anchor="w",
                fg_color="transparent", hover_color="#303030",
                text_color=c["muted"], font=("Segoe UI", 12),
                command=lambda k=key: show_page(k),
            )
            button.pack(fill="x", padx=10, pady=3)
            self._nav_buttons[key] = button

        side_bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        side_bottom.pack(side="bottom", fill="x", padx=10, pady=14)
        ctk.CTkLabel(side_bottom, text="YT-DLP", text_color=c["muted"],
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 5))
        ctk.CTkButton(side_bottom, text="Actualizar yt-dlp", height=36,
                      fg_color="#292929", hover_color="#383838", text_color=c["text"],
                      anchor="w", command=self.start_update).pack(fill="x", pady=3)
        ctk.CTkButton(side_bottom, text="Abrir historial", height=36,
                      fg_color="#292929", hover_color="#383838", text_color=c["text"],
                      anchor="w", command=self.show_history).pack(fill="x", pady=3)
        ctk.CTkLabel(side_bottom, text="Inspirado en Parabolic · WinUI",
                     text_color="#858585", font=("Segoe UI", 9),
                     wraplength=180, justify="left").pack(anchor="w", padx=10, pady=(14, 0))

        downloads = make_page("downloads")
        downloads.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(downloads, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(24, 18))
        ctk.CTkLabel(header, text="Descargas", font=("Segoe UI Variable Display", 28, "bold"),
                     text_color=c["text"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Guarda audio, vídeo y listas de reproducción.",
                     font=("Segoe UI", 12), text_color=c["muted"]).pack(anchor="w", pady=(4, 0))

        # Cuadro para agregar uno o varios enlaces.
        add_card = ctk.CTkFrame(downloads, fg_color=c["panel"], corner_radius=8,
                                border_width=1, border_color=c["line"])
        add_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 14))
        ctk.CTkLabel(add_card, text="Agregar desde un enlace",
                     font=("Segoe UI", 14, "bold"), text_color=c["text"]).pack(
                         anchor="w", padx=18, pady=(16, 9))
        linkrow = ctk.CTkFrame(add_card, fg_color="transparent")
        linkrow.pack(fill="x", padx=18, pady=(0, 17))
        linkrow.grid_columnconfigure(0, weight=1)
        self.url = tk.StringVar()
        entry = ctk.CTkEntry(linkrow, textvariable=self.url, height=40, corner_radius=5,
                             border_width=1, border_color=c["line"], fg_color=c["field"],
                             text_color=c["text"], placeholder_text="Pega aquí un enlace de YouTube, YouTube Music o una playlist…")
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<Return>", lambda _e: self.add_from_entry())
        ctk.CTkButton(linkrow, text="Agregar", width=104, height=40, corner_radius=5,
                      fg_color=c["gold"], hover_color=c["gold_hover"],
                      text_color="#101010", font=("Segoe UI", 11, "bold"),
                      command=self.add_from_entry).grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(linkrow, text="Pegar varios", width=112, height=40, corner_radius=5,
                      fg_color=c["panel2"], hover_color="#454545", text_color=c["text"],
                      command=self.paste_many).grid(row=0, column=2)
        entry.focus()

        # Vista previa del elemento seleccionado.
        preview = ctk.CTkFrame(downloads, fg_color=c["panel"], corner_radius=8,
                               border_width=1, border_color=c["line"])
        preview.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 14))
        preview.grid_columnconfigure(1, weight=1)
        cover = ctk.CTkFrame(preview, fg_color=c["panel2"], corner_radius=5,
                             width=104, height=104)
        cover.grid(row=0, column=0, padx=14, pady=14, sticky="nw")
        cover.grid_propagate(False)
        self.preview_label = ctk.CTkLabel(cover, text="♫\nSIN MINIATURA",
                                          font=("Segoe UI", 11, "bold"),
                                          text_color=c["muted"], justify="center")
        self.preview_label.pack(fill="both", expand=True)
        info = ctk.CTkFrame(preview, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=14)
        ctk.CTkLabel(info, text="VISTA PREVIA", font=("Segoe UI", 9, "bold"),
                     text_color=c["gold"]).pack(anchor="w", pady=(0, 5))
        self.preview_title = ctk.CTkLabel(info, text="Selecciona un elemento de la cola",
                                          font=("Segoe UI", 15, "bold"), text_color=c["text"],
                                          anchor="w", justify="left", wraplength=600)
        self.preview_title.pack(anchor="w", fill="x")
        self.preview_hint = ctk.CTkLabel(info, text="La miniatura y los detalles aparecerán aquí.",
                                         font=("Segoe UI", 11), text_color=c["muted"],
                                         anchor="w", justify="left", wraplength=600)
        self.preview_hint.pack(anchor="w", pady=(5, 0))

        queuehead = ctk.CTkFrame(downloads, fg_color="transparent")
        queuehead.grid(row=3, column=0, sticky="new", padx=30, pady=(0, 8))
        ctk.CTkLabel(queuehead, text="Cola de descargas", font=("Segoe UI", 17, "bold"),
                     text_color=c["text"]).pack(side="left")
        ctk.CTkButton(queuehead, text="Reintentar errores", width=136, height=32,
                      corner_radius=5, fg_color=c["panel2"], hover_color="#454545",
                      text_color=c["text"], command=self.retry_failed).pack(
                          side="right", padx=(8, 0))
        ctk.CTkButton(queuehead, text="Quitar", width=76, height=32, corner_radius=5,
                      fg_color=c["panel2"], hover_color="#454545", text_color=c["text"],
                      command=self.remove_selected).pack(side="right", padx=(8, 0))
        ctk.CTkButton(queuehead, text="Limpiar terminados", width=132, height=32,
                      corner_radius=5, fg_color=c["panel2"], hover_color="#454545",
                      text_color=c["text"], command=self.clear_finished).pack(side="right")

        tableframe = ctk.CTkFrame(downloads, fg_color=c["panel"], corner_radius=8,
                                  border_width=1, border_color=c["line"])
        tableframe.grid(row=4, column=0, sticky="nsew", padx=30, pady=(0, 14))
        downloads.grid_rowconfigure(4, weight=1)
        self.tree = ttk.Treeview(tableframe, columns=("tipo", "titulo", "estado"),
                                 show="headings", selectmode="extended", height=6)
        for col, title, width, stretch in (
                ("tipo", "FORMATO", 125, False), ("titulo", "TÍTULO / ENLACE", 420, True),
                ("estado", "ESTADO", 150, False)):
            self.tree.heading(col, text=title, anchor="w")
            self.tree.column(col, width=width, stretch=stretch, anchor="w")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", background=c["panel"], fieldbackground=c["panel"],
                        foreground=c["text"], borderwidth=0, rowheight=38,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=c["panel2"], foreground=c["muted"],
                        relief="flat", padding=9, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#294b5b")],
                  foreground=[("selected", c["text"])])
        ybar = ttk.Scrollbar(tableframe, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        ybar.pack(side="right", fill="y", padx=(0, 8), pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        self.tree.bind("<Delete>", lambda _e: self.remove_selected())

        status_card = ctk.CTkFrame(downloads, fg_color=c["panel"], corner_radius=8,
                                   border_width=1, border_color=c["line"])
        status_card.grid(row=5, column=0, sticky="ew", padx=30, pady=(0, 20))
        statusrow = ctk.CTkFrame(status_card, fg_color="transparent")
        statusrow.pack(fill="x", padx=16, pady=(13, 7))
        ctk.CTkLabel(statusrow, text="ESTADO", font=("Segoe UI", 9, "bold"),
                     text_color=c["gold"]).pack(side="left")
        self.status = tk.StringVar(value="Listo para descargar.")
        ctk.CTkLabel(statusrow, textvariable=self.status, font=("Segoe UI", 11),
                     text_color=c["text"]).pack(side="left", padx=(12, 0))
        self.progress = ttk.Progressbar(status_card, orient="horizontal",
                                         mode="determinate", maximum=100, value=0)
        self.progress.pack(fill="x", padx=16, pady=(0, 12))
        controls = ctk.CTkFrame(status_card, fg_color="transparent")
        controls.pack(fill="x", padx=16, pady=(0, 13))
        self.download_btn = ctk.CTkButton(controls, text="↓  Iniciar descargas",
                                          height=38, corner_radius=5,
                                          fg_color=c["gold"], hover_color=c["gold_hover"],
                                          text_color="#101010", font=("Segoe UI", 11, "bold"),
                                          command=self.start_download)
        self.download_btn.pack(side="left")
        self.cancel_btn = ctk.CTkButton(controls, text="Cancelar", height=38,
                                        corner_radius=5, fg_color=c["panel2"],
                                        hover_color="#454545", text_color=c["text"],
                                        state="disabled", command=self.cancel)
        self.cancel_btn.pack(side="left", padx=(8, 0))
        self.log = ctk.CTkTextbox(status_card, height=72, corner_radius=5,
                                  border_width=1, border_color=c["line"],
                                  fg_color=c["field"], text_color=c["muted"],
                                  font=("Consolas", 9), wrap="word")
        self.log.pack(fill="x", padx=16, pady=(0, 13))
        self.log.configure(state="disabled")
        self.add_log("Vinilo iniciado.")

        # Preferencias y destino se organizan en una página propia, como en WinUI.
        settings_page = make_page("settings")
        settings_page.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(settings_page, text="Configuración",
                     font=("Segoe UI Variable Display", 28, "bold"),
                     text_color=c["text"]).pack(anchor="w", padx=30, pady=(24, 5))
        ctk.CTkLabel(settings_page, text="Personaliza el formato, la calidad y la ubicación de tus descargas.",
                     font=("Segoe UI", 12), text_color=c["muted"]).pack(
                         anchor="w", padx=30, pady=(0, 20))

        settings_card = ctk.CTkFrame(settings_page, fg_color=c["panel"], corner_radius=8,
                                     border_width=1, border_color=c["line"])
        settings_card.pack(fill="x", padx=30, pady=(0, 14))
        ctk.CTkLabel(settings_card, text="Preferencias de descarga",
                     font=("Segoe UI", 15, "bold"), text_color=c["text"]).pack(
                         anchor="w", padx=18, pady=(17, 12))
        self.mode = tk.StringVar(value=self.cfg["mode"])
        self.quality = tk.StringVar(value=self.cfg["quality"])
        self.audio_format = tk.StringVar(value=self.cfg["audio_format"])
        self.video_audio = tk.StringVar(value=self.cfg["video_audio"])
        self.theme_mode = tk.StringVar(value=self.cfg["theme"])
        grid = ctk.CTkFrame(settings_card, fg_color="transparent")
        grid.pack(fill="x", padx=12, pady=(0, 12))
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1, uniform="settings")
        self._modern_option(grid, 0, 0, "Contenido predeterminado", self.mode, list(MODES), self._on_option)
        from downloader import QUALITIES, AUDIO_FORMATS, VIDEO_AUDIO_OPTIONS
        self._modern_option(grid, 0, 1, "Calidad de vídeo", self.quality, QUALITIES, self._on_option)
        self._modern_option(grid, 1, 0, "Formato de audio", self.audio_format, AUDIO_FORMATS, self._on_option)
        self._modern_option(grid, 1, 1, "Audio en vídeo", self.video_audio, VIDEO_AUDIO_OPTIONS, self._on_option)
        self._modern_option(grid, 2, 0, "Apariencia", self.theme_mode, ["dark", "light"], self.change_theme)

        dest_card = ctk.CTkFrame(settings_page, fg_color=c["panel"], corner_radius=8,
                                 border_width=1, border_color=c["line"])
        dest_card.pack(fill="x", padx=30, pady=(0, 14))
        ctk.CTkLabel(dest_card, text="Ubicación de descarga",
                     font=("Segoe UI", 15, "bold"), text_color=c["text"]).pack(
                         anchor="w", padx=18, pady=(17, 8))
        ctk.CTkLabel(dest_card, text="Los archivos se organizan en subcarpetas de música y vídeo.",
                     font=("Segoe UI", 11), text_color=c["muted"]).pack(
                         anchor="w", padx=18, pady=(0, 9))
        self.dest = tk.StringVar(value=self.cfg["dest"])
        destline = ctk.CTkFrame(dest_card, fg_color="transparent")
        destline.pack(fill="x", padx=18, pady=(0, 17))
        self.dest_entry = ctk.CTkEntry(destline, textvariable=self.dest, height=38,
                                       corner_radius=5, border_color=c["line"],
                                       fg_color=c["field"], text_color=c["text"])
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.dest_btn = ctk.CTkButton(destline, text="Examinar…", width=105, height=38,
                                      corner_radius=5, fg_color=c["panel2"],
                                      hover_color="#454545", text_color=c["text"],
                                      command=self.choose_dest)
        self.dest_btn.pack(side="left", padx=(0, 8))
        ctk.CTkButton(destline, text="Abrir carpeta", width=118, height=38,
                      corner_radius=5, fg_color=c["panel2"], hover_color="#454545",
                      text_color=c["text"], command=self.open_dest).pack(side="left")

        about_card = ctk.CTkFrame(settings_page, fg_color=c["panel"], corner_radius=8,
                                  border_width=1, border_color=c["line"])
        about_card.pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkLabel(about_card, text="Acerca de Vinilo",
                     font=("Segoe UI", 14, "bold"), text_color=c["text"]).pack(
                         anchor="w", padx=18, pady=(15, 5))
        ctk.CTkLabel(about_card, text="Motor yt-dlp · Conversión con FFmpeg · Interfaz Python",
                     font=("Segoe UI", 11), text_color=c["muted"]).pack(
                         anchor="w", padx=18, pady=(0, 15))

        # Opciones avanzadas inspiradas en la sección Downloader de Parabolic.
        advanced = ctk.CTkFrame(settings_page, fg_color=c["panel"], corner_radius=8,
                                border_width=1, border_color=c["line"])
        advanced.pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkLabel(advanced, text="Descargas avanzadas",
                     font=("Segoe UI", 15, "bold"), text_color=c["text"]).pack(
                         anchor="w", padx=18, pady=(17, 5))
        ctk.CTkLabel(advanced,
                     text="Estas opciones se aplican a los enlaces nuevos. Algunas dependen de que el sitio y FFmpeg las admitan.",
                     font=("Segoe UI", 11), text_color=c["muted"], wraplength=700,
                     justify="left").pack(anchor="w", padx=18, pady=(0, 12))
        self.advanced_vars = {
            "embed_metadata": tk.BooleanVar(value=self.cfg.get("embed_metadata", True)),
            "embed_thumbnail": tk.BooleanVar(value=self.cfg.get("embed_thumbnail", True)),
            "write_subtitles": tk.BooleanVar(value=self.cfg.get("write_subtitles", False)),
            "write_auto_subtitles": tk.BooleanVar(value=self.cfg.get("write_auto_subtitles", False)),
            "embed_subtitles": tk.BooleanVar(value=self.cfg.get("embed_subtitles", False)),
            "split_chapters": tk.BooleanVar(value=self.cfg.get("split_chapters", False)),
            "export_description": tk.BooleanVar(value=self.cfg.get("export_description", False)),
            "write_info_json": tk.BooleanVar(value=self.cfg.get("write_info_json", False)),
            "overwrite_files": tk.BooleanVar(value=self.cfg.get("overwrite_files", False)),
        }
        checks = ctk.CTkFrame(advanced, fg_color="transparent")
        checks.pack(fill="x", padx=14, pady=(0, 12))
        for key, label in (
            ("embed_metadata", "Incrustar metadatos"),
            ("embed_thumbnail", "Incrustar y guardar miniatura"),
            ("write_subtitles", "Descargar subtítulos disponibles"),
            ("write_auto_subtitles", "Descargar subtítulos automáticos"),
            ("embed_subtitles", "Incrustar subtítulos en el vídeo"),
            ("split_chapters", "Separar vídeo por capítulos"),
            ("export_description", "Guardar descripción en archivo"),
            ("write_info_json", "Guardar metadatos JSON"),
            ("overwrite_files", "Sobrescribir archivos existentes"),
        ):
            ctk.CTkCheckBox(checks, text=label, variable=self.advanced_vars[key],
                            command=self._save_settings, text_color=c["text"],
                            fg_color=c["gold"], hover_color=c["gold_hover"],
                            border_color=c["muted"], checkmark_color="#101010").pack(
                                anchor="w", padx=6, pady=5)
        advanced_grid = ctk.CTkFrame(advanced, fg_color="transparent")
        advanced_grid.pack(fill="x", padx=18, pady=(0, 18))
        advanced_grid.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(advanced_grid, text="Idiomas de subtítulos",
                     text_color=c["muted"]).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=5)
        self.subtitle_languages = tk.StringVar(value=self.cfg.get("subtitle_languages", "all"))
        ctk.CTkEntry(advanced_grid, textvariable=self.subtitle_languages,
                     placeholder_text="all, es, en", height=34).grid(
                         row=0, column=1, sticky="ew", pady=5)
        ctk.CTkLabel(advanced_grid, text="Contenedor de vídeo",
                     text_color=c["muted"]).grid(row=1, column=0, sticky="w", padx=(0, 12), pady=5)
        self.video_container = tk.StringVar(value=self.cfg.get("video_container", "mp4"))
        ctk.CTkOptionMenu(advanced_grid, variable=self.video_container,
                          values=["mp4", "webm", "mkv"], height=34,
                          fg_color=c["panel2"], button_color=c["panel2"],
                          button_hover_color="#454545").grid(
                              row=1, column=1, sticky="ew", pady=5)
        ctk.CTkLabel(advanced_grid, text="FPS preferidos",
                     text_color=c["muted"]).grid(row=2, column=0, sticky="w", padx=(0, 12), pady=5)
        self.preferred_frame_rate = tk.StringVar(value=self.cfg.get("preferred_frame_rate", "Any"))
        ctk.CTkOptionMenu(advanced_grid, variable=self.preferred_frame_rate,
                          values=["Any", "24", "25", "30", "50", "60"], height=34,
                          fg_color=c["panel2"], button_color=c["panel2"],
                          button_hover_color="#454545").grid(
                              row=2, column=1, sticky="ew", pady=5)
        ctk.CTkLabel(advanced_grid, text="Argumentos extra de yt-dlp",
                     text_color=c["muted"]).grid(row=3, column=0, sticky="w", padx=(0, 12), pady=5)
        self.extra_ytdlp_args = tk.StringVar(value=self.cfg.get("extra_ytdlp_args", ""))
        ctk.CTkEntry(advanced_grid, textvariable=self.extra_ytdlp_args,
                     placeholder_text="Ej.: --extractor-retries 3", height=34).grid(
                         row=3, column=1, sticky="ew", pady=5)
        ctk.CTkLabel(advanced_grid, text="Descargas simultáneas",
                     text_color=c["muted"]).grid(row=4, column=0, sticky="w", padx=(0, 12), pady=5)
        self.max_concurrent_downloads = tk.StringVar(
            value=str(self.cfg.get("max_concurrent_downloads", 1)))
        ctk.CTkOptionMenu(advanced_grid, variable=self.max_concurrent_downloads,
                          values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                          height=34, fg_color=c["panel2"], button_color=c["panel2"],
                          button_hover_color="#454545").grid(
                              row=4, column=1, sticky="ew", pady=5)
        for var in (self.subtitle_languages, self.video_container,
                    self.preferred_frame_rate, self.extra_ytdlp_args,
                    self.max_concurrent_downloads):
            var.trace_add("write", lambda *_: self._save_settings())

        show_page("downloads")

    def _advanced_options(self):
        values = {key: variable.get() for key, variable in self.advanced_vars.items()}
        values.update(
            subtitle_languages=self.subtitle_languages.get().strip() or "all",
            video_container=self.video_container.get(),
            preferred_frame_rate=self.preferred_frame_rate.get(),
            extra_ytdlp_args=self.extra_ytdlp_args.get().strip(),
            max_concurrent_downloads=max(1, min(10, int(self.max_concurrent_downloads.get()))),
        )
        return values

    def _save_settings(self):
        if hasattr(self, "advanced_vars"):
            self.cfg.update(self._advanced_options())
        super()._save_settings()

    def _ev_job(self, job_id):
        job = self.queue.get(job_id)
        if job and job.status == "pending" and not getattr(job, "_preferences_asked", False):
            job._preferences_asked = True
            self._ask_download_preferences(job)
        super()._ev_job(job_id)

    def _ask_download_preferences(self, job):
        c = self.colors
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Preferencias de descarga")
        dialog.geometry("520x540")
        dialog.minsize(480, 500)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=c["bg"])
        outer = ctk.CTkFrame(dialog, fg_color=c["panel"], corner_radius=18,
                              border_width=1, border_color=c["line"])
        outer.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(outer, text="PREPARAR DESCARGA",
                     font=("Segoe UI", 11, "bold"), text_color=c["gold"]).pack(
                         anchor="w", padx=18, pady=(18, 5))
        ctk.CTkLabel(outer, text=job.title or job.url, wraplength=440,
                     justify="left", font=("Segoe UI", 15, "bold"),
                     text_color=c["text"]).pack(anchor="w", padx=18, pady=(0, 14))
        ctk.CTkLabel(outer, text=("Playlist detectada" if job.kind and job.kind.is_playlist
                                  else "Contenido individual detectado"),
                     text_color=c["muted"]).pack(anchor="w", padx=18, pady=(0, 8))
        inferred = "audio" if job.kind and job.kind.is_audio else "video"
        initial = {"Audio": "audio", "Video": "video"}.get(self.cfg.get("mode"), inferred)
        mode_var = tk.StringVar(value=initial)
        modebox = ctk.CTkFrame(outer, fg_color="transparent")
        modebox.pack(fill="x", padx=18, pady=(0, 12))
        ctk.CTkLabel(modebox, text="¿Qué quieres descargar?", text_color=c["muted"]).pack(
            anchor="w", pady=(0, 6))
        ctk.CTkRadioButton(modebox, text="Solo audio", variable=mode_var, value="audio",
                           fg_color=c["gold"], text_color=c["text"]).pack(side="left", padx=(0, 18))
        ctk.CTkRadioButton(modebox, text="Vídeo con audio", variable=mode_var, value="video",
                           fg_color=c["gold"], text_color=c["text"]).pack(side="left")
        from downloader import QUALITIES, AUDIO_FORMATS, VIDEO_AUDIO_OPTIONS
        quality_var = tk.StringVar(value=job.quality or self.quality.get())
        audio_var = tk.StringVar(value=job.audio_format or self.audio_format.get())
        va_var = tk.StringVar(value=job.video_audio or self.video_audio.get())
        self._dialog_option(outer, "Calidad del vídeo", quality_var, QUALITIES, c)
        self._dialog_option(outer, "Formato de audio", audio_var, AUDIO_FORMATS, c)
        self._dialog_option(outer, "Audio dentro del vídeo", va_var, VIDEO_AUDIO_OPTIONS, c)
        dest_var = tk.StringVar(value=self.dest.get())
        ctk.CTkLabel(outer, text="Carpeta de descarga", text_color=c["muted"]).pack(
            anchor="w", padx=18, pady=(8, 5))
        destrow = ctk.CTkFrame(outer, fg_color="transparent")
        destrow.pack(fill="x", padx=18)
        ctk.CTkEntry(destrow, textvariable=dest_var, height=34, fg_color=c["field"],
                     border_color=c["line"], text_color=c["text"]).pack(
                         side="left", fill="x", expand=True, padx=(0, 7))
        def browse():
            folder = filedialog.askdirectory(parent=dialog,
                initialdir=dest_var.get() or self.dest.get(), title="Seleccionar carpeta de descarga")
            if folder:
                dest_var.set(folder)
        ctk.CTkButton(destrow, text="Elegir…", width=88, command=browse,
                      fg_color=c["panel2"], hover_color=c["line"],
                      text_color=c["text"]).pack(side="left")
        buttons = ctk.CTkFrame(outer, fg_color="transparent")
        buttons.pack(fill="x", padx=18, pady=(18, 18))
        def confirm():
            from downloader import Kind
            playlist = bool(job.kind and job.kind.is_playlist)
            job.kind = ((Kind.PLAYLIST if playlist else Kind.SONG) if mode_var.get() == "audio"
                        else (Kind.VIDEO_PLAYLIST if playlist else Kind.VIDEO))
            job.quality, job.audio_format, job.video_audio = (
                quality_var.get(), audio_var.get(), va_var.get())
            job.dest = dest_var.get().strip() or self.dest.get()
            job.options = self._advanced_options()
            self.mode.set("Audio" if mode_var.get() == "audio" else "Video")
            self.quality.set(job.quality)
            self.audio_format.set(job.audio_format)
            self.video_audio.set(job.video_audio)
            self.dest.set(job.dest)
            self._save_settings()
            self.add_log("Preferencias aplicadas a: " + (job.title or job.url))
            dialog.destroy()
            self.refresh_row(job.id)
        ctk.CTkButton(buttons, text="Confirmar", height=38, fg_color=c["gold"],
                      hover_color=c["gold_hover"], text_color="#171717",
                      command=confirm).pack(side="right")
        ctk.CTkButton(buttons, text="Cancelar trabajo", height=38, fg_color=c["panel2"],
                      hover_color=c["line"], text_color=c["text"],
                      command=lambda: self._cancel_preferences(job, dialog)).pack(
                          side="right", padx=(0, 8))
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._cancel_preferences(job, dialog))
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")
        dialog.wait_window()

    def _dialog_option(self, parent, label, variable, values, colors):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=4)
        ctk.CTkLabel(row, text=label, text_color=colors["muted"],
                     width=155, anchor="w").pack(side="left")
        ctk.CTkOptionMenu(row, variable=variable, values=list(values),
                          fg_color=colors["panel2"], button_color=colors["field"],
                          button_hover_color=colors["line"], dropdown_fg_color=colors["panel"],
                          text_color=colors["text"], width=210).pack(side="right", fill="x", expand=True)

    def _cancel_preferences(self, job, dialog):
        self.queue.remove(job.id)
        if self.tree.exists(str(job.id)):
            self.tree.delete(str(job.id))
        self.add_log("Descarga descartada antes de iniciar: " + job.url)
        dialog.destroy()

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

    def _selection_changed(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        job = self.queue.get(int(selection[0]))
        if not job:
            return
        self.preview_title.configure(text=job.title or job.url)
        if job.thumbnail and job.thumbnail != self.preview_url:
            self.preview_url = job.thumbnail
            self.preview_label.configure(image=None, text="♫\nCARGANDO…")
            threading.Thread(target=self._load_preview, args=(job.id, job.thumbnail), daemon=True).start()
        elif not job.thumbnail:
            self.preview_label.configure(image=None, text="♫\nSIN PORTADA")
            self.preview_hint.configure(text="No hay miniatura disponible para este enlace.")
