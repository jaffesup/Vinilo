"""Interfaz tkinter. Solo dibuja y reacciona; la lógica vive en downloader.py."""
import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import history
import paths
import settings
import theme
from downloader import (QUALITIES, DownloadQueue, Runner, Status,
                        extract_urls, update_command)

MODES = {"Automático": "auto", "Audio MP3": "audio", "Video MP4": "video"}


def status_text(job) -> str:
    s = job.status
    if s == Status.ANALYZING:
        return "Analizando…"
    if s == Status.PENDING:
        return "En espera"
    if s == Status.RUNNING:
        extra = f" · {job.item[0]}/{job.item[1]}" if job.item else ""
        return f"Descargando {job.progress:.0f}%{extra}"
    return {Status.DONE: "✔ Completado", Status.ERROR: "✖ Error",
            Status.CANCELLED: "■ Cancelado"}[s]


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Vinilo")
        root.geometry("900x780")
        root.minsize(780, 680)

        self.cfg = settings.load()
        if not Path(self.cfg["dest"]).is_dir():
            self.cfg["dest"] = str(paths.BASE_DIR)
        if self.cfg["mode"] not in MODES:
            self.cfg["mode"] = "Automático"
        if self.cfg["quality"] not in QUALITIES:
            self.cfg["quality"] = "720p"

        theme.apply(root)

        self.events = queue.Queue()
        self.queue = DownloadQueue(lambda name, *a: self.events.put((name, *a)))
        self.updater = Runner()
        self.updating = False

        self._build()
        theme.dark_title_bar(root)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(100, self._pump)

    # ---------- construcción ----------
    def _build(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Vinilo",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(main, style="Muted.TLabel",
                  text="Pega enlaces de canciones, videos o playlists. "
                       "El tipo se detecta solo."
                  ).pack(anchor="w", pady=(0, 14))

        row = ttk.Frame(main)
        row.pack(fill="x")
        self.url = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.url)
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self.add_from_entry())
        entry.focus()
        ttk.Button(row, text="Agregar",
                   command=self.add_from_entry).pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Pegar varios",
                   command=self.paste_many).pack(side="left", padx=(8, 0))

        opts = ttk.Frame(main)
        opts.pack(fill="x", pady=(12, 0))
        ttk.Label(opts, text="Tipo:").pack(side="left")
        self.mode = tk.StringVar(value=self.cfg["mode"])
        cb = ttk.Combobox(opts, textvariable=self.mode, values=list(MODES),
                          state="readonly", width=12)
        cb.pack(side="left", padx=(6, 20))
        cb.bind("<<ComboboxSelected>>", self._on_option)
        ttk.Label(opts, text="Calidad de video:").pack(side="left")
        self.quality = tk.StringVar(value=self.cfg["quality"])
        cb = ttk.Combobox(opts, textvariable=self.quality, values=QUALITIES,
                          state="readonly", width=16)
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", self._on_option)

        drow = ttk.Frame(main)
        drow.pack(fill="x", pady=(12, 0))
        ttk.Label(drow, text="Guardar en:").pack(side="left")
        self.dest = tk.StringVar(value=self.cfg["dest"])
        ttk.Entry(drow, textvariable=self.dest, state="readonly"
                  ).pack(side="left", fill="x", expand=True, padx=8)
        self.dest_btn = ttk.Button(drow, text="Cambiar…",
                                   command=self.choose_dest)
        self.dest_btn.pack(side="left")
        ttk.Button(drow, text="Abrir",
                   command=self.open_dest).pack(side="left", padx=(8, 0))

        ttk.Label(main, text="Cola de descargas",
                  style="Muted.TLabel").pack(anchor="w", pady=(16, 4))
        box = ttk.Frame(main)
        box.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(box, columns=("tipo", "titulo", "estado"),
                                 show="headings", selectmode="extended",
                                 height=8)
        for col, text, width, stretch in (("tipo", "Tipo", 110, False),
                                          ("titulo", "Título / enlace", 420, True),
                                          ("estado", "Estado", 170, False)):
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, stretch=stretch, anchor="w")
        sb = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Delete>", lambda e: self.remove_selected())

        qbar = ttk.Frame(main)
        qbar.pack(fill="x", pady=(8, 0))
        ttk.Button(qbar, text="Quitar seleccionados",
                   command=self.remove_selected).pack(side="left")
        ttk.Button(qbar, text="Limpiar terminados",
                   command=self.clear_finished).pack(side="left", padx=8)

        self.progress = ttk.Progressbar(main, maximum=100)
        self.progress.pack(fill="x", pady=(14, 4))
        self.status = tk.StringVar(value="Listo.")
        ttk.Label(main, textvariable=self.status).pack(anchor="w")

        arow = ttk.Frame(main)
        arow.pack(fill="x", pady=(12, 12))
        self.download_btn = ttk.Button(arow, text="Descargar",
                                       style="Accent.TButton",
                                       command=self.start_download)
        self.download_btn.pack(side="left")
        self.cancel_btn = ttk.Button(arow, text="Cancelar", state="disabled",
                                     command=self.cancel)
        self.cancel_btn.pack(side="left", padx=8)

        self.log = tk.Text(main, height=6, wrap="word", state="disabled",
                           font=("Consolas", 9), bg=theme.PANEL, fg=theme.FG,
                           insertbackground=theme.FG, relief="flat",
                           highlightthickness=1,
                           highlightbackground=theme.BORDER,
                           padx=8, pady=6)
        self.log.pack(fill="x")

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(12, 0))
        self.update_btn = ttk.Button(bottom, text="Actualizar yt-dlp",
                                     command=self.start_update)
        self.update_btn.pack(side="left")
        ttk.Button(bottom, text="Ver historial",
                   command=self.show_history).pack(side="left", padx=8)
        ttk.Button(bottom, text="Salir",
                   command=self.on_close).pack(side="right")

        self.add_log("Programa iniciado.")

    # ---------- utilidades ----------
    def add_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _save_settings(self):
        self.cfg.update(dest=self.dest.get(), mode=self.mode.get(),
                        quality=self.quality.get())
        settings.save(self.cfg)

    def _on_option(self, _event=None):
        self._save_settings()

    def _set_busy(self):
        busy = self.queue.running or self.updating
        state = "disabled" if busy else "normal"
        self.download_btn.configure(state=state)
        self.update_btn.configure(state=state)
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
        folder = filedialog.askdirectory(initialdir=self.dest.get(),
                                         title="Carpeta de destino")
        if folder:
            self.dest.set(str(Path(folder)))
            self._save_settings()
            self.add_log(f"Destino: {self.dest.get()}")

    # ---------- cola ----------
    def refresh_row(self, job_id):
        job = self.queue.get(job_id)
        iid = str(job_id)
        if job is None or not self.tree.exists(iid):
            return
        self.tree.item(iid, values=(job.kind.value if job.kind else "…",
                                    job.title or job.url, status_text(job)))

    def add_from_entry(self):
        text = self.url.get().strip()
        if text:
            self.add_urls(text)

    def paste_many(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            text = ""
        self.add_urls(text)

    def add_urls(self, text):
        urls = extract_urls(text)
        if not urls:
            messagebox.showwarning(
                "Enlace no válido",
                "No encontré ningún enlace que empiece por https://")
            return
        mode = MODES[self.mode.get()]
        for url in urls:
            job = self.queue.add(url, self.quality.get())
            if job is None:
                self.add_log(f"Ya está en la cola: {url}")
                continue
            self.tree.insert("", "end", iid=str(job.id), values=("…", url, ""))
            self.refresh_row(job.id)
            threading.Thread(target=self.queue.analyze, args=(job, mode),
                             daemon=True).start()
        self.url.set("")

    def remove_selected(self):
        for iid in self.tree.selection():
            if self.queue.remove(int(iid)):
                self.tree.delete(iid)
            else:
                self.status.set("No se puede quitar lo que se está descargando.")

    def clear_finished(self):
        for job_id in self.queue.clear_finished():
            if self.tree.exists(str(job_id)):
                self.tree.delete(str(job_id))

    # ---------- acciones ----------
    def _check_tools(self):
        if not paths.YTDLP.is_file():
            messagebox.showerror("Falta yt-dlp.exe",
                                 f"No encuentro:\n{paths.YTDLP}")
            return None
        ffmpeg = paths.find_ffmpeg_dir()
        if ffmpeg is None:
            messagebox.showerror(
                "Falta FFmpeg",
                "No encuentro ffmpeg.exe.\nColócalo en la carpeta 'ffmpeg' "
                "junto al programa.")
        return ffmpeg

    def start_download(self):
        if self.queue.running or self.updating:
            return
        self.add_from_entry()
        waiting = (Status.ANALYZING, Status.PENDING, Status.CANCELLED)
        if not any(j.status in waiting for j in self.queue.jobs):
            messagebox.showinfo("Cola vacía", "Agrega al menos un enlace.")
            return
        ffmpeg = self._check_tools()
        if ffmpeg is None:
            return
        self._save_settings()
        self.queue.start(ffmpeg, Path(self.dest.get()))
        for j in list(self.queue.jobs):
            self.refresh_row(j.id)
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
            messagebox.showerror("Falta yt-dlp.exe",
                                 f"No encuentro:\n{paths.YTDLP}")
            return
        self.updating = True
        self._set_busy()
        self.status.set("Actualizando yt-dlp…")
        self.add_log("\nBuscando actualizaciones de yt-dlp…")

        def work():
            code, _ = self.updater.run(
                update_command(), lambda l: self.events.put(("ulog", l)))
            self.events.put(("updated", code))

        threading.Thread(target=work, daemon=True).start()

    def on_close(self):
        if self.queue.running or self.updating:
            if not messagebox.askyesno("Descarga en curso",
                                       "Hay trabajo en curso. ¿Cancelar y salir?"):
                return
            self.cancel()
        self._save_settings()
        self.root.destroy()

    # ---------- eventos que vienen de los hilos ----------
    def _pump(self):
        try:
            while True:
                ev = self.events.get_nowait()
                handler = getattr(self, "_ev_" + ev[0])
                handler(*ev[1:])
        except queue.Empty:
            pass
        self.root.after(100, self._pump)

    def _queue_summary(self):
        jobs = self.queue.jobs
        done = sum(j.status in Status.FINISHED for j in jobs)
        return done, len(jobs)

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
        result = {Status.DONE: "Completada",
                  Status.CANCELLED: "Cancelada"}.get(
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
        stopped = any(j.status == Status.CANCELLED for j in jobs)
        if stopped:
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
            messagebox.showerror(
                "Algunas descargas fallaron",
                f"{bad} descarga(s) no se completaron. "
                "Revisa el registro para ver los detalles.")

    def _ev_ulog(self, text):
        self.add_log(text)

    def _ev_updated(self, code):
        self.updating = False
        self._set_busy()
        ok = code == 0
        self.status.set("yt-dlp actualizado." if ok else
                        f"La actualización terminó con código {code}.")
        self.add_log("Actualización terminada." if ok else
                     f"Actualización fallida. Código: {code}")
