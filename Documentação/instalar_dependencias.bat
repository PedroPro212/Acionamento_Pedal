@echo off
title Instalacao - FS-01 Camera
python --version
if errorlevel 1 (
    echo Python nao encontrado. Instale Python 3.11 ou superior e marque "Add Python to PATH".
    pause
    exit /b 1
)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Dependencias instaladas.
pause
