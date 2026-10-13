
@echo off
setlocal
title YT-DLP Media Manager
cd /d "%~dp0"

set "YTDLP=%~dp0yt-dlp.exe"
set "MUSICA=%~dp0musica"
set "VIDEOS=%~dp0videos"
set "FFMPEG=%~dp0ffmpeg\ffmpeg-9.0.2-essentials_build\bin"

if not exist "%YTDLP%" (
    echo ERROR: No se encuentra yt-dlp.exe
    pause
    exit /b 1
)

if not exist "%MUSICA%" mkdir "%MUSICA%"
if not exist "%VIDEOS%" mkdir "%VIDEOS%"

:MENU
cls
echo ==========================================
echo         YT-DLP MEDIA MANAGER
echo ==========================================
echo.
echo  [1] Descargar una cancion MP3
echo  [2] Descargar una playlist MP3
echo  [3] Descargar un video MP4
echo  [4] Actualizar yt-dlp
echo  [5] Abrir carpeta de descargas
echo  [6] Salir
echo.
echo ==========================================
set "OPCION="
set /p "OPCION=Selecciona una opcion: "

if "%OPCION%"=="1" goto CANCION
if "%OPCION%"=="2" goto PLAYLIST
if "%OPCION%"=="3" goto VIDEO
if "%OPCION%"=="4" goto ACTUALIZAR
if "%OPCION%"=="5" goto CARPETA
if "%OPCION%"=="6" goto FIN

echo.
echo Opcion no valida.
pause
goto MENU

:CANCION
cls
echo ===== DESCARGAR CANCION MP3 =====
set "URL="
set /p "URL=Pega el enlace: "
if not defined URL goto MENU

if exist "%FFMPEG%\ffmpeg.exe" (
    "%YTDLP%" --ffmpeg-location "%FFMPEG%" -x --audio-format mp3 --audio-quality 0 --windows-filenames -P "%MUSICA%" -o "%%(title)s.%%(ext)s" "%URL%"
) else (
    echo ERROR: No se encuentra FFmpeg.
)
pause
goto MENU

:PLAYLIST
cls
echo ===== DESCARGAR PLAYLIST MP3 =====
set "URL="
set /p "URL=Pega el enlace de la playlist: "
if not defined URL goto MENU

if exist "%FFMPEG%\ffmpeg.exe" (
    "%YTDLP%" --ffmpeg-location "%FFMPEG%" --yes-playlist -x --audio-format mp3 --audio-quality 0 --windows-filenames -P "%MUSICA%" -o "%%(playlist_title)s\%%(playlist_index)03d - %%(title)s.%%(ext)s" "%URL%"
) else (
    echo ERROR: No se encuentra FFmpeg.
)
pause
goto MENU

:VIDEO
cls
echo ==========================================
echo          DESCARGAR VIDEO MP4
echo ==========================================
echo.
echo  [1] 360p
echo  [2] 480p
echo  [3] 720p HD
echo  [4] 1080p Full HD
echo  [5] Mejor calidad disponible
echo  [6] Volver al menu
echo.

set "CALIDAD="
set "FORMATO="
set /p "CALIDAD=Selecciona la calidad: "

if "%CALIDAD%"=="6" goto MENU
if "%CALIDAD%"=="1" set "FORMATO=bv*[height<=360]+ba/b[height<=360]/b"
if "%CALIDAD%"=="2" set "FORMATO=bv*[height<=480]+ba/b[height<=480]/b"
if "%CALIDAD%"=="3" set "FORMATO=bv*[height<=720]+ba/b[height<=720]/b"
if "%CALIDAD%"=="4" set "FORMATO=bv*[height<=1080]+ba/b[height<=1080]/b"
if "%CALIDAD%"=="5" set "FORMATO=bv*+ba/b"

if not defined FORMATO (
    echo Opcion no valida.
    pause
    goto VIDEO
)

set "URL="
set /p "URL=Pega el enlace del video: "
if not defined URL goto MENU

if exist "%FFMPEG%\ffmpeg.exe" (
    "%YTDLP%" --ffmpeg-location "%FFMPEG%" -f "%FORMATO%" --merge-output-format mp4 --windows-filenames -P "%VIDEOS%" -o "%%(title)s.%%(ext)s" "%URL%"
) else (
    echo ERROR: No se encuentra FFmpeg.
)

echo.
echo Proceso finalizado.
pause
goto MENU

:ACTUALIZAR
cls
echo ===== ACTUALIZAR YT-DLP =====
"%YTDLP%" -U
pause
goto MENU

:CARPETA
if not exist "%MUSICA%" mkdir "%MUSICA%"
if not exist "%VIDEOS%" mkdir "%VIDEOS%"
start "" "%~dp0"
goto MENU

:FIN
echo Hasta pronto.
endlocal
exit /b
