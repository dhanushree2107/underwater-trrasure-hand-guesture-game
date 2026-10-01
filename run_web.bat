@echo off
title Underwater Treasure Hunt - Web Version
cd /d "%~dp0"
echo ===================================================
echo   Starting Underwater Treasure Hunt (Web Version)
echo ===================================================
echo Opening http://localhost:8000 in your browser...
start http://localhost:8000
python server.py
pause
