"""Rutas del programa. Funciona igual como script y como .exe (PyInstaller)."""
import shutil
import sys
from pathlib import Path


def _app_dir() -> Path:
    # En un .exe, __file__ apunta a una carpeta temporal; hay que usar
    # la ubicación real del ejecutable.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = _app_dir()
YTDLP = BASE_DIR / "yt-dlp.exe"
HISTORY_FILE = BASE_DIR / "historial.txt"
CONFIG_FILE = BASE_DIR / "config.json"


def find_ffmpeg_dir():
    """Busca ffmpeg.exe sin depender del nombre de versión de la carpeta."""
    if (BASE_DIR / "ffmpeg.exe").is_file():
        return BASE_DIR
    root = BASE_DIR / "ffmpeg"
    if root.is_dir():
        for exe in root.rglob("ffmpeg.exe"):
            return exe.parent
    found = shutil.which("ffmpeg")
    return Path(found).parent if found else None
