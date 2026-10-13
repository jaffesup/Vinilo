@echo off
cd /d "%~dp0"
py -m pip install --upgrade pyinstaller
py -m PyInstaller --noconsole --onefile --name Vinilo main.py
echo.
echo Listo. Copia dist\Vinilo.exe junto a yt-dlp.exe y la carpeta ffmpeg.
pause
