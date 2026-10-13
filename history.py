"""Historial de descargas (sin dependencias de interfaz)."""
from datetime import datetime

from paths import HISTORY_FILE


def append(result: str, url: str) -> None:
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {result}: {url}\n")


def exists() -> bool:
    return HISTORY_FILE.exists()
