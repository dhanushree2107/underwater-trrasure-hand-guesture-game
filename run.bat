@echo off
title Underwater Treasure Hunt
cd /d "%~dp0"
echo ===================================================
echo        Starting Underwater Treasure Hunt
echo ===================================================
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py main.py
) else (
    python main.py
)
if %ERRORLEVEL% neq 0 (
    echo.
    echo [Notice] Application closed or exited with code %ERRORLEVEL%.
    pause
)
