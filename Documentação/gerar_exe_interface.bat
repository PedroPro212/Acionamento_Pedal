@echo off
title Gerando FS-01 Camera

echo ==========================================
echo   Gerando FS-01 Camera
echo ==========================================
echo.

python -m PyInstaller ^
 --noconfirm ^
 --clean ^
 --onefile ^
 --windowed ^
 --name FS01_Camera ^
 --add-data "..\logoFlash.png;." ^
 --add-data "..\logoProgramacaoDiaria.png;." ^
 "..\index.py"

echo.
echo ==========================================
echo   Processo finalizado
echo ==========================================
echo.

pause