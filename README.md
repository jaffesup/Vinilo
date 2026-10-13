<<<<<<< HEAD
# YT-DLP Media Manager

Descargador de música, videos y playlists con interfaz gráfica para Windows.
Usa [yt-dlp](https://github.com/yt-dlp/yt-dlp) y [FFmpeg](https://ffmpeg.org/) por debajo.

## Características

- Detecta solo si el enlace es canción, video o playlist.
- Cola de descargas: agrega varios enlaces o pégalos todos juntos.
- MP3 con portada y etiquetas incrustadas.
- Videos MP4 en 360p, 480p, 720p, 1080p o la mejor calidad disponible.
- Carpeta de destino configurable y tema oscuro.
- Historial de descargas y botón para actualizar yt-dlp.

## Uso (ejecutable)

1. Descarga `MediaManager.exe` desde la sección **Releases**.
2. Colócalo en una carpeta junto a:
   - `yt-dlp.exe` (de https://github.com/yt-dlp/yt-dlp/releases)
   - la carpeta `ffmpeg` con `ffmpeg.exe` dentro, en cualquier subcarpeta (de https://www.gyan.dev/ffmpeg/builds/, versión "essentials")
3. Abre `MediaManager.exe`.

## Uso (desde el código)

Requiere Python 3.10 o superior. No hay dependencias que instalar.

```
py main.py
```

## Generar el ejecutable

```
build_exe.bat
```

El resultado queda en `dist\MediaManager.exe`.

## Estructura

| Archivo | Función |
|---|---|
| `downloader.py` | Lógica: comandos de yt-dlp, detección, cola (sin interfaz) |
| `gui.py` | Interfaz tkinter |
| `theme.py` | Tema oscuro |
| `settings.py` | Preferencias en `config.json` |
| `history.py` | Historial de descargas |
| `paths.py` | Rutas y búsqueda de FFmpeg |
| `main.py` | Punto de entrada |
| `Media_Manager.Bat` | Versión original en consola |

## Aviso

Descarga solo contenido que tengas derecho a descargar y respeta los términos de servicio de cada plataforma.
=======
# Vinilo
Interfaz de descarga de música y videos que usa yt-dlp
>>>>>>> 9eb063bee942063ce4032bef3577d7ae82fc9175
