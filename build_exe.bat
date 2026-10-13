@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo          VINILO - CONSTRUIR EXE
echo ========================================
echo.
py -m pip install --upgrade pip
if errorlevel 1 goto error
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto error
py -m PyInstaller --noconfirm --clean --noconsole --onefile --name Vinilo --collect-all PIL main.py
if errorlevel 1 goto error
echo.
echo EXE creado: dist\Vinilo.exe
echo Para usarlo como portable, copia Vinilo.exe a una carpeta
echo junto a yt-dlp.exe y la carpeta ffmpeg con ffmpeg.exe.
echo Tus preferencias e historial se guardan junto al ejecutable.
echo.
pause
exit /b 0
:error
echo.
echo ERROR: No se pudo construir el ejecutable. Revisa el mensaje anterior.
pause
exit /b 1
