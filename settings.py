"""Preferencias guardadas en config.json (sin dependencias de interfaz)."""
import json

from paths import BASE_DIR, CONFIG_FILE

DEFAULTS = {"dest": str(BASE_DIR), "quality": "720p", "mode": "Automático"}


def load() -> dict:
    data = dict(DEFAULTS)
    try:
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            data.update(saved)
    except (OSError, ValueError):
        pass
    return data


def save(data: dict) -> None:
    try:
        CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                               encoding="utf-8")
    except OSError:
        pass
