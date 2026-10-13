"""Preferencias de Vinilo guardadas en config.json."""
import json

from paths import BASE_DIR, CONFIG_FILE

DEFAULTS = {
    "dest": str(BASE_DIR),
    "quality": "720p",
    "mode": "Automático",
    "audio_format": "MP3",
    "video_audio": "Mejor disponible",
    "theme": "dark",
}


def load() -> dict:
    data = dict(DEFAULTS)
    try:
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            data.update({key: value for key, value in saved.items()
                         if key in DEFAULTS})
    except (OSError, ValueError, TypeError):
        pass
    return data


def save(data: dict) -> None:
    """Guarda solo opciones reconocidas; errores de escritura no rompen la app."""
    payload = {key: data.get(key, value) for key, value in DEFAULTS.items()}
    try:
        CONFIG_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                               encoding="utf-8")
    except OSError:
        pass
