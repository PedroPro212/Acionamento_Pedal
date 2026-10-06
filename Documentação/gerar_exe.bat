@echo off
title Gerar EXE - FS-01 Camera
python -m PyInstaller --noconfirm --clean --onefile --windowed --name FS01_Camera FS01_Camera.py
echo.
echo Se tudo ocorreu corretamente, o executavel esta em: dist\FS01_Camera.exe
pause
