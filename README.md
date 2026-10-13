# Vinilo

Descargador de música, vídeos y playlists para Windows con interfaz gráfica inspirada en aplicaciones de escritorio modernas y una paleta cálida de café y vainilla. Usa [yt-dlp](https://github.com/yt-dlp/yt-dlp) y [FFmpeg](https://ffmpeg.org/).

## Características

- **Detección automática:** analiza el enlace y propone el tipo de contenido. También puedes forzar modo Audio o Vídeo.
- **Audio:** MP3, M4A, OPUS, FLAC y WAV.
- **Vídeo:** MP4 con calidad de 360p, 480p, 720p, 1080p, 1440p, 2160p o mejor disponible.
- **Preferencia de audio para vídeo:** mejor disponible, preferir AAC o preferir M4A cuando el formato fuente lo permita.
- **Portadas y miniaturas:** intenta descargar la miniatura y añadirla a los metadatos del archivo. La disponibilidad depende de la plataforma y de los códecs compatibles.
- **Vista previa:** selecciona una fila de la cola para intentar ver su portada/miniatura. Requiere Pillow.
- **Cola de descargas:** varios enlaces, progreso, cancelación, reanudación de trabajos cancelados e historial.
- **Destino configurable:** elige la carpeta de salida; audio y vídeo se separan en subcarpetas `musica` y `videos`.
- **Apariencia:** tema claro y oscuro, con colores café y vainilla.
- **Ventana adaptable:** contenido desplazable y barras para navegar cuando la ventana no tiene suficiente espacio.
- **Preferencias persistentes:** guarda tema, formato, calidad, modo y ubicación en `config.json`.

## Ejecutar desde el código

Requiere Windows y Python 3.10 o superior.

```bat
py -m pip install -r requirements.txt
py main.py
```

Coloca `yt-dlp.exe` junto a los archivos del proyecto y FFmpeg en una carpeta `ffmpeg` (o asegúrate de que esté disponible en PATH). Descarga las versiones oficiales desde:
- [yt-dlp Releases](https://github.com/yt-dlp/yt-dlp/releases)
- [FFmpeg builds para Windows](https://www.gyan.dev/ffmpeg/builds/) (build Essentials)

## Crear el ejecutable portable

1. En Windows, instala Python y asegúrate de que el comando `py` funcione.
2. Ejecuta `build_exe.bat`.
3. El ejecutable se generará en `dist\Vinilo.exe`.
4. Copia `Vinilo.exe` a una carpeta junto a `yt-dlp.exe` y la carpeta `ffmpeg` que contiene `ffmpeg.exe`.

El ejecutable de Vinilo es portable; yt-dlp y FFmpeg se distribuyen por separado. La configuración y el historial se guardan en la carpeta del ejecutable. En modo de archivo único, PyInstaller puede tardar un poco más al abrir por primera vez.

## Estructura

| Archivo | Función |
|---|---|
| `main.py` | Punto de entrada |
| `gui.py` | Interfaz, preferencias y vista previa |
| `downloader.py` | Detección, comandos, procesos y cola |
| `theme.py` | Temas claro y oscuro |
| `settings.py` | Preferencias guardadas |
| `history.py` | Historial de descargas |
| `paths.py` | Rutas y búsqueda de FFmpeg |
| `requirements.txt` | Dependencia para miniaturas |
| `build_exe.bat` | Construcción del ejecutable |
| `Media_Manager.Bat` | Versión original por consola (se conserva sin cambios) |

## Aviso

Descarga únicamente contenido que tengas derecho a descargar y respeta las condiciones de uso de cada plataforma. La miniatura puede no estar disponible o no ser compatible con la incrustación en algunos formatos.
