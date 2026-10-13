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
    "embed_metadata": True,
    "embed_thumbnail": True,
    "write_subtitles": False,
    "write_auto_subtitles": False,
    "embed_subtitles": False,
    "subtitle_languages": "all",
    "split_chapters": False,
    "export_description": False,
    "write_info_json": False,
    "overwrite_files": False,
    "video_container": "mp4",
    "preferred_frame_rate": "Any",
    "extra_ytdlp_args": "",
    "max_concurrent_downloads": 1,
    "cookies_from_browser": "none",
    "preferred_video_codec": "Any",
    "preferred_audio_codec": "Any",
    "preferred_subtitle_format": "best",
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
