"""Lógica de descarga. No importa tkinter: se puede probar o reutilizar
con otra interfaz. Los eventos se avisan con un callback que se llama
desde hilos de trabajo; la interfaz decide cómo pasarlos a su hilo."""
import json
import re
import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

from paths import YTDLP

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # evita ventanas negras
MUSIC_SUB = "musica"
VIDEO_SUB = "videos"
QUALITIES = ["360p", "480p", "720p", "1080p", "Mejor disponible"]


class Kind(Enum):
    SONG = "Canción MP3"
    PLAYLIST = "Playlist MP3"
    VIDEO = "Video MP4"
    VIDEO_PLAYLIST = "Playlist MP4"

    @property
    def is_audio(self) -> bool:
        return self in (Kind.SONG, Kind.PLAYLIST)

    @property
    def is_playlist(self) -> bool:
        return self in (Kind.PLAYLIST, Kind.VIDEO_PLAYLIST)


class Status:
    ANALYZING = "analyzing"
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"
    FINISHED = (DONE, ERROR, CANCELLED)


# ---------------------------------------------------------------- utilidades
def video_format(quality: str) -> str:
    if quality == "Mejor disponible":
        return "bv*+ba/b"
    h = quality.removesuffix("p")
    return f"bv*[height<={h}]+ba/b[height<={h}]/b"


def extract_urls(text: str) -> list:
    """Todos los enlaces http(s) de un texto, sin repetir y en orden."""
    seen, out = set(), []
    for url in re.findall(r"https?://[^\s<>\"']+", text):
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def is_playlist_url(url: str) -> bool:
    return urlparse(url).path.startswith("/playlist")


def probe(url: str, timeout: int = 40) -> Optional[dict]:
    """Pregunta a yt-dlp qué es el enlace (sin descargar). None si falla."""
    cmd = [str(YTDLP), "-J", "--flat-playlist", "--no-warnings"]
    if not is_playlist_url(url):
        cmd.append("--no-playlist")
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=NO_WINDOW)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def resolve_kind(url: str, info: Optional[dict], mode: str = "auto") -> Kind:
    """Decide el tipo. mode: 'auto', 'audio' o 'video'.
    Playlist: lo dicen los metadatos (o la URL si no hubo respuesta).
    Canción vs video: music.youtube.com o categoría 'Music' = canción."""
    playlist = (info.get("_type") == "playlist") if info else is_playlist_url(url)

    if mode == "audio":
        audio = True
    elif mode == "video":
        audio = False
    else:
        music = "music.youtube.com" in urlparse(url).netloc
        if info and not playlist:
            music = music or "Music" in (info.get("categories") or []) \
                or bool(info.get("track"))
        audio = music or playlist      # las playlists son MP3 por defecto

    if playlist:
        return Kind.PLAYLIST if audio else Kind.VIDEO_PLAYLIST
    return Kind.SONG if audio else Kind.VIDEO


def describe(url: str, info: Optional[dict]) -> str:
    if not info:
        return url
    title = info.get("title") or url
    if info.get("_type") == "playlist":
        n = len(info.get("entries") or [])
        return f"{title} ({n} elementos)" if n else title
    return title


def build_command(kind: Kind, url: str, ffmpeg_dir: Path, dest: Path,
                  quality: str = "720p") -> list:
    cmd = [str(YTDLP), "--newline", "--windows-filenames", "--embed-metadata",
           "--ffmpeg-location", str(ffmpeg_dir)]

    if kind.is_audio:
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0",
                "--embed-thumbnail", "--convert-thumbnails", "jpg"]
        folder = Path(dest) / MUSIC_SUB
    else:
        cmd += ["-f", video_format(quality), "--merge-output-format", "mp4"]
        folder = Path(dest) / VIDEO_SUB

    if kind.is_playlist:
        cmd += ["--yes-playlist", "--ignore-errors"]
        template = "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"
    else:
        cmd += ["--no-playlist"]
        template = "%(title)s.%(ext)s"

    return cmd + ["-P", str(folder), "-o", template, url]


def update_command() -> list:
    return [str(YTDLP), "-U"]


_PERCENT = re.compile(r"\[download\]\s+(\d+(?:\.\d+)?)%")
_ITEM = re.compile(r"Downloading (?:item|video) (\d+) of (\d+)")


def parse_percent(line: str) -> Optional[float]:
    m = _PERCENT.search(line)
    return float(m.group(1)) if m else None


def parse_item(line: str) -> Optional[tuple]:
    m = _ITEM.search(line)
    return (int(m.group(1)), int(m.group(2))) if m else None


# -------------------------------------------------------------------- Runner
class Runner:
    """Ejecuta un comando y espera a que termine (bloqueante)."""

    def __init__(self):
        self._proc = None
        self._cancelled = False

    def run(self, cmd: list, on_line: Callable[[str], None]) -> tuple:
        """Devuelve (código, fue_cancelado)."""
        self._cancelled = False
        code = -1
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=NO_WINDOW)
            for line in self._proc.stdout:
                line = line.strip()
                if line:
                    on_line(line)
            code = self._proc.wait()
        except Exception as exc:
            on_line(f"Error: {exc}")
        finally:
            self._proc = None
        return code, self._cancelled

    def cancel(self) -> None:
        proc = self._proc
        if proc and proc.poll() is None:
            self._cancelled = True
            # /T mata también a ffmpeg, que es proceso hijo de yt-dlp
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           creationflags=NO_WINDOW,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------- Cola
@dataclass
class Job:
    id: int
    url: str
    quality: str = "720p"
    title: str = ""
    kind: Optional[Kind] = None
    status: str = Status.ANALYZING
    progress: float = 0.0
    item: Optional[tuple] = None
    code: Optional[int] = None


class DownloadQueue:
    """Cola de descargas que se procesa de una en una.

    on_event(nombre, *args) se llama desde hilos de trabajo:
      ("job", id)         el trabajo cambió (estado, progreso, título)
      ("line", id, texto) línea de salida de yt-dlp
      ("done", id)        el trabajo terminó (bien, mal o cancelado)
      ("finished",)       la cola se vació o se detuvo
    """

    def __init__(self, on_event: Callable):
        self._emit = on_event
        self.jobs = []
        self.running = False
        self._lock = threading.Lock()
        self._next_id = 1
        self._stop = False
        self._runner = Runner()

    def get(self, job_id: int) -> Optional[Job]:
        with self._lock:
            return next((j for j in self.jobs if j.id == job_id), None)

    def add(self, url: str, quality: str) -> Optional[Job]:
        """None si ese enlace ya está activo en la cola."""
        active = (Status.ANALYZING, Status.PENDING, Status.RUNNING)
        with self._lock:
            if any(j.url == url and j.status in active for j in self.jobs):
                return None
            job = Job(self._next_id, url, quality)
            self._next_id += 1
            self.jobs.append(job)
            return job

    def remove(self, job_id: int) -> bool:
        with self._lock:
            for i, j in enumerate(self.jobs):
                if j.id == job_id:
                    if j.status == Status.RUNNING:
                        return False
                    del self.jobs[i]
                    return True
        return False

    def clear_finished(self) -> list:
        with self._lock:
            ids = [j.id for j in self.jobs if j.status in Status.FINISHED]
            self.jobs = [j for j in self.jobs if j.id not in ids]
        return ids

    def analyze(self, job: Job, mode: str = "auto") -> None:
        """Bloqueante: la interfaz la llama en un hilo."""
        info = probe(job.url)
        if self.get(job.id) is None:       # lo quitaron mientras se analizaba
            return
        job.kind = resolve_kind(job.url, info, mode)
        job.title = describe(job.url, info)
        job.status = Status.PENDING
        if info is None:
            self._emit("line", job.id,
                       "No se pudo analizar el enlace; se detecta por su dirección.")
        self._emit("job", job.id)

    def start(self, ffmpeg_dir: Path, dest: Path) -> bool:
        if self.running:
            return False
        self._stop = False
        with self._lock:
            for j in self.jobs:
                if j.status == Status.CANCELLED:   # reanudar lo interrumpido
                    j.status, j.progress, j.item = Status.PENDING, 0.0, None
        self.running = True
        threading.Thread(target=self._worker, args=(ffmpeg_dir, dest),
                         daemon=True).start()
        return True

    def cancel(self) -> None:
        self._stop = True
        self._runner.cancel()

    # ---- interno
    def _worker(self, ffmpeg_dir, dest):
        try:
            while not self._stop:
                with self._lock:
                    job = next((j for j in self.jobs
                                if j.status == Status.PENDING), None)
                    waiting = any(j.status == Status.ANALYZING
                                  for j in self.jobs)
                if job is None:
                    if waiting:
                        time.sleep(0.3)
                        continue
                    break
                self._run_job(job, ffmpeg_dir, dest)
        finally:
            self.running = False
            self._emit("finished")

    def _run_job(self, job, ffmpeg_dir, dest):
        job.status, job.progress, job.item = Status.RUNNING, 0.0, None
        self._emit("job", job.id)
        cmd = build_command(job.kind, job.url, ffmpeg_dir, dest, job.quality)

        def on_line(line):
            changed = False
            item = parse_item(line)
            if item:
                job.item, job.progress, changed = item, 0.0, True
            pct = parse_percent(line)
            if pct is not None:
                job.progress, changed = pct, True
            self._emit("line", job.id, line)
            if changed:
                self._emit("job", job.id)

        code, cancelled = self._runner.run(cmd, on_line)
        job.code = code
        if cancelled:
            job.status = Status.CANCELLED
        elif code == 0:
            job.status, job.progress = Status.DONE, 100.0
        else:
            job.status = Status.ERROR
        self._emit("job", job.id)
        self._emit("done", job.id)
