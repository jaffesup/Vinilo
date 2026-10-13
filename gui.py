"""Interfaz gráfica adaptable de Vinilo."""
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.request import Request, urlopen
from io import BytesIO

import history
import paths
import settings
import theme
from downloader import (AUDIO_FORMATS, QUALITIES, VIDEO_AUDIO_OPTIONS,
                        DownloadQueue, Runner, Status, extract_urls, update_command)

MODES = {"Automático": "auto", "Audio": "audio", "Video": "video"}


def status_text(job) -> str:
    if job.status == Status.ANALYZING:
        return "Analizando…"
    if job.status == Status.PENDING:
        return "En espera"
    if job.status == Status.RUNNING:
        extra = f" · {job.item[0]}/{job.item[1]}" if job.item else ""
        return f"Descargando {job.progress:.0f}%{extra}"
    return {Status.DONE: "✓ Completado", Status.ERROR: "✕ Error",
            Status.CANCELLED: "■ Cancelado"}.get(job.status, str(job.status))


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vinilo")
        root.geometry("1000x850")
        root.minsize(680, 600)
        self.cfg = settings.load()
        if not Path(self.cfg["dest"]).is_dir():
            self.cfg["dest"] = str(paths.BASE_DIR)
        if self.cfg["mode"] not in MODES:
            self.cfg["mode"] = "Automático"
        if self.cfg["quality"] not in QUALITIES:
            self.cfg["quality"] = "720p"
        if self.cfg["audio_format"] not in AUDIO_FORMATS:
            self.cfg["audio_format"] = "MP3"
        if self.cfg["video_audio"] not in VIDEO_AUDIO_OPTIONS:
            self.cfg["video_audio"] = VIDEO_AUDIO_OPTIONS[0]
        if self.cfg["theme"] not in ("dark", "light"):
            self.cfg["theme"] = "dark"

        theme.apply(root, self.cfg["theme"])
        self.events = queue.Queue()
        self.queue = DownloadQueue(lambda name, *a: self.events.put((name, *a)))
        self.updater = Runner()
        self.updating = False
        self.preview_image = None
        self.preview_url = ""
        self._build()
        theme.dark_title_bar(root, self.cfg["theme"])
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(100, self._pump)

    def _build(self):
        # Lienzo desplazable para conservar el diseño en pantallas pequeñas.
        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(outer, bg=theme.BG, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        main = ttk.Frame(self.canvas, padding=(28, 24, 28, 28))
        self.main_window = self.canvas.create_window((0, 0), window=main, anchor="nw")
        main.bind("<Configure>", lambda _e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(
            self.main_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._mousewheel)

        # Cabecera editorial, con un acento dorado discreto.
        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 22))
        brand = ttk.Frame(header)
        brand.pack(side="left", fill="x", expand=True)
        ttk.Label(brand, text="VINILO  /  MEDIA DOWNLOADER",
                  style="Eyebrow.TLabel").pack(anchor="w", pady=(0, 5))
        ttk.Label(brand, text="Tus medios. A tu manera.",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(brand, text="Una forma sencilla de guardar audio y vídeo.",
                  style="Muted.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Label(header, text="●  LISTO", style="Eyebrow.TLabel").pack(
            side="right", anchor="ne", padx=(10, 2), pady=(8, 0))

        # Área principal para añadir enlaces.
        linkcard = ttk.LabelFrame(main, text="  01  ·  NUEVA DESCARGA  ", padding=16)
        linkcard.pack(fill="x", pady=(0, 14))
        ttk.Label(linkcard, text="Pega uno o varios enlaces",
                  style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self.url = tk.StringVar()
        urlrow = ttk.Frame(linkcard)
        urlrow.pack(fill="x")
        entry = ttk.Entry(urlrow, textvariable=self.url)
        entry.pack(side="left", fill="x", expand=True, ipady=3)
        entry.bind("<Return>", lambda _e: self.add_from_entry())
        entry.focus()
        ttk.Button(urlrow, text="＋  Agregar enlace", style="Accent.TButton",
                   command=self.add_from_entry).pack(side="left", padx=(10, 0))
        ttk.Button(urlrow, text="Pegar varios", command=self.paste_many).pack(
            side="left", padx=(8, 0))
        ttk.Label(linkcard, text="Compatible con enlaces individuales y listas de reproducción.",
                  style="Muted.TLabel").pack(anchor="w", pady=(9, 0))

        self.mode = tk.StringVar(value=self.cfg["mode"])
        self.quality = tk.StringVar(value=self.cfg["quality"])
        self.audio_format = tk.StringVar(value=self.cfg["audio_format"])
        self.video_audio = tk.StringVar(value=self.cfg["video_audio"])
        self.theme_mode = tk.StringVar(value=self.cfg["theme"])

        # Preferencias en una tarjeta compacta de dos columnas.
        options = ttk.LabelFrame(main, text="  02  ·  AJUSTES DE DESCARGA  ", padding=16)
        options.pack(fill="x", pady=(0, 14))
        options.columnconfigure(1, weight=1, uniform="prefs")
        options.columnconfigure(3, weight=1, uniform="prefs")
        self._option_cell(options, 0, 0, "Contenido", self.mode,
                          list(MODES), self._on_option)
        self._option_cell(options, 0, 2, "Calidad de vídeo", self.quality,
                          QUALITIES, self._on_option)
        self._option_cell(options, 1, 0, "Formato de audio", self.audio_format,
                          AUDIO_FORMATS, self._on_option)
        self._option_cell(options, 1, 2, "Audio en vídeo", self.video_audio,
                          VIDEO_AUDIO_OPTIONS, self._on_option)
        self._option_cell(options, 2, 0, "Tema", self.theme_mode,
                          ["dark", "light"], self.change_theme)
        ttk.Label(options, text="Preferencias guardadas automáticamente.",
                  style="Muted.TLabel").grid(row=2, column=2, columnspan=2,
                                              sticky="e", padx=(12, 0), pady=(12, 0))

        # Destino con acciones agrupadas.
        destrow = ttk.LabelFrame(main, text="  03  ·  DESTINO  ", padding=14)
        destrow.pack(fill="x", pady=(0, 14))
        self.dest = tk.StringVar(value=self.cfg["dest"])
        ttk.Label(destrow, text="Guardar archivos en", style="Muted.TLabel").pack(
            anchor="w", pady=(0, 7))
        destcontrols = ttk.Frame(destrow)
        destcontrols.pack(fill="x")
        ttk.Entry(destcontrols, textvariable=self.dest, state="readonly").pack(
            side="left", fill="x", expand=True, ipady=2)
        self.dest_btn = ttk.Button(destcontrols, text="Elegir carpeta",
                                   command=self.choose_dest)
        self.dest_btn.pack(side="left", padx=(9, 0))
        ttk.Button(destcontrols, text="Abrir", command=self.open_dest).pack(
            side="left", padx=(7, 0))

        # Vista previa discreta; se conserva la carga asíncrona de miniaturas.
        preview = ttk.LabelFrame(main, text="  VISTA PREVIA  ", padding=14)
        preview.pack(fill="x", pady=(0, 18))
        self.preview_label = tk.Label(
            preview, text="SIN\\nPORTADA", bg=theme.FIELD, fg=theme.MUTED,
            width=18, height=7, compound="center", relief="flat",
            anchor="center", font=("Segoe UI", 9, "bold")
        )
        self.preview_label.pack(side="left", padx=(0, 16))
        previewinfo = ttk.Frame(preview)
        previewinfo.pack(side="left", fill="both", expand=True, pady=(8, 0))
        ttk.Label(previewinfo, text="CONTENIDO SELECCIONADO",
                  style="Eyebrow.TLabel").pack(anchor="w", pady=(0, 7))
        self.preview_title = ttk.Label(previewinfo, text="Sin selección",
                                       style="Section.TLabel", wraplength=560)
        self.preview_title.pack(anchor="w", fill="x")
        self.preview_hint = ttk.Label(
            previewinfo, text="La miniatura aparecerá aquí cuando selecciones un elemento.",
            style="Muted.TLabel", wraplength=560
        )
        self.preview_hint.pack(anchor="w", pady=(7, 0))

        # Cola y acciones relacionadas.
        queuehead = ttk.Frame(main)
        queuehead.pack(fill="x", pady=(0, 8))
        ttk.Label(queuehead, text="04  ·  Cola de descargas",
                  style="Section.TLabel").pack(side="left")
        ttk.Button(queuehead, text="Limpiar terminados",
                   command=self.clear_finished).pack(side="right")
        ttk.Button(queuehead, text="Quitar seleccionados",
                   command=self.remove_selected).pack(side="right", padx=(0, 8))

        tableframe = ttk.Frame(main)
        tableframe.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tableframe, columns=("tipo", "titulo", "estado"),
                                 show="headings", selectmode="extended", height=7)
        for col, title, width, stretch in (
                ("tipo", "FORMATO", 125, False),
                ("titulo", "TÍTULO / ENLACE", 420, True),
                ("estado", "ESTADO", 175, False)):
            self.tree.heading(col, text=title, anchor="w")
            self.tree.column(col, width=width, stretch=stretch, anchor="w")
        ybar = ttk.Scrollbar(tableframe, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(tableframe, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        tableframe.rowconfigure(0, weight=1)
        tableframe.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        self.tree.bind("<Delete>", lambda _e: self.remove_selected())

        # Estado, progreso y controles principales.
        statuscard = ttk.LabelFrame(main, text="  ESTADO DE LA SESIÓN  ", padding=14)
        statuscard.pack(fill="x", pady=(14, 0))
        self.status = tk.StringVar(value="Listo para descargar.")
        ttk.Label(statuscard, textvariable=self.status,
                  style="Section.TLabel").pack(anchor="w", pady=(0, 9))
        self.progress = ttk.Progressbar(statuscard, maximum=100)
        self.progress.pack(fill="x")
        actions = ttk.Frame(statuscard)
        actions.pack(fill="x", pady=(13, 0))
        self.download_btn = ttk.Button(
            actions, text="↓  Descargar ahora", style="Accent.TButton",
            command=self.start_download
        )
        self.download_btn.pack(side="left")
        self.cancel_btn = ttk.Button(actions, text="Cancelar", state="disabled",
                                     command=self.cancel)
        self.cancel_btn.pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Actualizar yt-dlp",
                   command=self.start_update).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="Historial", command=self.show_history).pack(
            side="left", padx=(8, 0))
        ttk.Button(actions, text="Salir", command=self.on_close).pack(side="right")

        ttk.Label(main, text="REGISTRO DE ACTIVIDAD",
                  style="Eyebrow.TLabel").pack(anchor="w", pady=(20, 7))
        self.log = tk.Text(
            main, height=5, wrap="word", state="disabled",
            font=("Consolas", 9), bg=theme.PANEL, fg=theme.FG,
            insertbackground=theme.FG, relief="flat",
            highlightthickness=1, highlightbackground=theme.BORDER,
            padx=12, pady=10
        )
        self.log.pack(fill="x")
        self.add_log("Vinilo iniciado.")

    def _option_cell(self, parent, row, column, label, variable, values, callback):
        cell = ttk.Frame(parent)
        cell.grid(row=row, column=column, columnspan=2, sticky="ew",
                  padx=(0, 14) if column == 0 else (0, 0),
                  pady=(0, 10) if row < 2 else (0, 0))
        ttk.Label(cell, text=label, style="Muted.TLabel").pack(anchor="w", pady=(0, 5))
        cb = ttk.Combobox(cell, textvariable=variable, values=values, state="readonly")
        cb.pack(fill="x")
        cb.bind("<<ComboboxSelected>>", callback)

    def _option_row(self, parent, row, label, variable, values, callback):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
        cb = ttk.Combobox(parent, textvariable=variable, values=values,
                          state="readonly")
        cb.grid(row=row, column=1, sticky="ew", pady=4)
        cb.bind("<<ComboboxSelected>>", callback)

    def _mousewheel(self, event):
        if self.root.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _save_settings(self):
        self.cfg.update(dest=self.dest.get(), mode=self.mode.get(),
                        quality=self.quality.get(), audio_format=self.audio_format.get(),
                        video_audio=self.video_audio.get(), theme=self.theme_mode.get())
        settings.save(self.cfg)

    def _on_option(self, _event=None):
        self._save_settings()

    def change_theme(self, _event=None):
        self._save_settings()
        theme.apply(self.root, self.theme_mode.get())
        self.canvas.configure(bg=theme.BG)
        self.preview_label.configure(bg=theme.FIELD, fg=theme.MUTED)
        self.log.configure(bg=theme.PANEL, fg=theme.FG,
                           insertbackground=theme.FG,
                           highlightbackground=theme.BORDER)
        theme.dark_title_bar(self.root, self.theme_mode.get())
        self.add_log("Tema actualizado: " + ("oscuro" if self.theme_mode.get() == "dark" else "claro"))

    def _set_busy(self):
        busy = self.queue.running or self.updating
        state = "disabled" if busy else "normal"
        self.download_btn.configure(state=state)
        self.dest_btn.configure(state=state)
        self.cancel_btn.configure(state="normal" if busy else "disabled")

    def _open(self, path: Path):
        try:
            if path.suffix == "":
                path.mkdir(parents=True, exist_ok=True)
            os.startfile(str(path))
        except Exception as exc:
            messagebox.showerror("No se pudo abrir", str(exc))

    def open_dest(self):
        self._open(Path(self.dest.get()))

    def show_history(self):
        if not history.exists():
            messagebox.showinfo("Historial", "Todavía no hay descargas guardadas.")
            return
        self._open(paths.HISTORY_FILE)

    def choose_dest(self):
        folder = filedialog.askdirectory(initialdir=self.dest.get(), title="Carpeta de destino")
        if folder:
            self.dest.set(str(Path(folder)))
            self._save_settings()
            self.add_log("Destino: " + self.dest.get())

    def refresh_row(self, job_id):
        job = self.queue.get(job_id)
        iid = str(job_id)
        if job is None or not self.tree.exists(iid):
            return
        self.tree.item(iid, values=(job.kind.value if job.kind else "Analizando…",
                                    job.title or job.url, status_text(job)))

    def add_from_entry(self):
        value = self.url.get().strip()
        if value:
            self.add_urls(value)

    def paste_many(self):
        try:
            value = self.root.clipboard_get()
        except tk.TclError:
            value = ""
        self.add_urls(value)

    def add_urls(self, text):
        urls = extract_urls(text)
        if not urls:
            messagebox.showwarning("Enlace no válido", "No encontré ningún enlace http(s).")
            return
        mode = "auto"  # El formato definitivo se elige tras analizar el enlace.
        for url in urls:
            job = self.queue.add(url, self.quality.get(), self.audio_format.get(),
                                 self.video_audio.get())
            if job is None:
                self.add_log("Ya está en la cola: " + url)
                continue
            self.tree.insert("", "end", iid=str(job.id),
                             values=("Analizando…", url, "Analizando…"))
            threading.Thread(target=self.queue.analyze, args=(job, mode), daemon=True).start()
        self.url.set("")

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
            self.preview_label.configure(image="", text="Cargando miniatura…")
            threading.Thread(target=self._load_preview, args=(job.id, job.thumbnail),
                             daemon=True).start()
        elif not job.thumbnail:
            self.preview_label.configure(image="", text="Sin miniatura disponible")
            self.preview_hint.configure(text="Comprueba que el enlace sea accesible.")

    def _load_preview(self, job_id, url):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=12) as response:
                data = response.read(8 * 1024 * 1024)
            from PIL import Image, ImageTk
            image = Image.open(BytesIO(data))
            image.thumbnail((190, 145))
            self.events.put(("preview", job_id, url, image.copy()))
        except Exception as exc:
            self.events.put(("preview_error", job_id, url, str(exc)))

    def _ev_preview(self, job_id, url, image):
        if not self.root.winfo_exists() or self.preview_url != url:
            return
        try:
            from PIL import ImageTk
            self.preview_image = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.preview_image, text="")
            self.preview_hint.configure(text="Miniatura del contenido seleccionado")
        except Exception:
            self.preview_label.configure(image="", text="Miniatura no disponible")
            self.preview_hint.configure(text="Instala Pillow para mostrar imágenes.")

    def _ev_preview_error(self, job_id, url, error):
        if self.preview_url == url:
            self.preview_label.configure(image="", text="Vista previa no disponible")
            self.preview_hint.configure(text="La miniatura no pudo cargarse.")

    def remove_selected(self):
        for iid in self.tree.selection():
            if self.queue.remove(int(iid)):
                self.tree.delete(iid)
            else:
                self.status.set("No se puede quitar un elemento en descarga.")

    def clear_finished(self):
        for job_id in self.queue.clear_finished():
            if self.tree.exists(str(job_id)):
                self.tree.delete(str(job_id))

    def retry_failed(self):
        retried = self.queue.retry_failed()
        for job_id in retried:
            self.refresh_row(job_id)
        if retried:
            self.status.set(f"{len(retried)} descarga(s) fallida(s) preparada(s) para reintentar.")
        else:
            self.status.set("No hay descargas fallidas para reintentar.")

    def _check_tools(self):
        if not paths.YTDLP.is_file():
            messagebox.showerror("Falta yt-dlp.exe", f"No encuentro:\n{paths.YTDLP}")
            return None
        ffmpeg = paths.find_ffmpeg_dir()
        if ffmpeg is None:
            messagebox.showerror("Falta FFmpeg",
                "No encuentro ffmpeg.exe. Colócalo junto al programa o dentro de 'ffmpeg'.")
        return ffmpeg

    def start_download(self):
        if self.queue.running or self.updating:
            return
        self.add_from_entry()
        if not any(j.status in (Status.ANALYZING, Status.PENDING, Status.CANCELLED)
                   for j in self.queue.jobs):
            messagebox.showinfo("Cola vacía", "Agrega al menos un enlace.")
            return
        ffmpeg = self._check_tools()
        if ffmpeg is None:
            return
        self._save_settings()
        self.queue.start(ffmpeg, Path(self.dest.get()), self.cfg.get("max_concurrent_downloads", 1))
        for job in list(self.queue.jobs):
            self.refresh_row(job.id)
        self.progress["value"] = 0
        self.status.set("Iniciando…")
        self._set_busy()

    def cancel(self):
        if self.queue.running:
            self.queue.cancel()
        elif self.updating:
            self.updater.cancel()
        self.status.set("Cancelando…")

    def start_update(self):
        if self.queue.running or self.updating:
            return
        if not paths.YTDLP.is_file():
            messagebox.showerror("Falta yt-dlp.exe", f"No encuentro:\n{paths.YTDLP}")
            return
        self.updating = True
        self._set_busy()
        self.status.set("Actualizando yt-dlp…")
        self.add_log("Buscando actualizaciones de yt-dlp…")
        def work():
            code, _ = self.updater.run(update_command(),
                lambda line: self.events.put(("ulog", line)))
            self.events.put(("updated", code))
        threading.Thread(target=work, daemon=True).start()

    def on_close(self):
        if self.queue.running or self.updating:
            if not messagebox.askyesno("Trabajo en curso", "¿Cancelar el trabajo y salir?"):
                return
            self.cancel()
        self._save_settings()
        self.root.destroy()

    def _pump(self):
        try:
            while True:
                event = self.events.get_nowait()
                handler = getattr(self, "_ev_" + event[0])
                handler(*event[1:])
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._pump)

    def _queue_summary(self):
        jobs = self.queue.jobs
        return sum(j.status in Status.FINISHED for j in jobs), len(jobs)

    def _ev_job(self, job_id):
        self.refresh_row(job_id)
        job = self.queue.get(job_id)
        if job and job.status == Status.RUNNING:
            done, total = self._queue_summary()
            self.progress["value"] = job.progress
            title = job.title if len(job.title) <= 45 else job.title[:42] + "…"
            self.status.set(f"Cola {done}/{total} · {title} · {job.progress:.0f}%")

    def _ev_line(self, _job_id, text):
        self.add_log(text)
        if "[ExtractAudio]" in text or "[Merger]" in text:
            self.status.set("Convirtiendo / uniendo…")

    def _ev_done(self, job_id):
        job = self.queue.get(job_id)
        if job is None:
            return
        result = {Status.DONE: "Completada", Status.CANCELLED: "Cancelada"}.get(
            job.status, f"Fallida (código {job.code})")
        try:
            history.append(result, job.url)
        except OSError as exc:
            self.add_log(f"No se pudo guardar el historial: {exc}")

    def _ev_finished(self):
        self._set_busy()
        jobs = self.queue.jobs
        ok = sum(j.status == Status.DONE for j in jobs)
        bad = sum(j.status == Status.ERROR for j in jobs)
        if any(j.status == Status.CANCELLED for j in jobs):
            self.status.set("Cancelado. Pulsa Descargar para reanudar.")
            return
        self.progress["value"] = 100 if ok and not bad else 0
        self.status.set(f"Cola terminada: {ok} completadas, {bad} con error.")
        try:
            import winsound
            winsound.MessageBeep()
        except Exception:
            pass
        if bad:
            messagebox.showerror("Algunas descargas fallaron",
                f"{bad} descarga(s) no se completaron. Revisa el registro.")

    def _ev_ulog(self, text):
        self.add_log(text)

    def _ev_updated(self, code):
        self.updating = False
        self._set_busy()
        ok = code == 0
        self.status.set("yt-dlp actualizado." if ok else f"Actualización con código {code}.")
        self.add_log("Actualización terminada." if ok else f"Actualización fallida. Código: {code}")
