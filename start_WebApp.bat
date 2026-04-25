@echo off
echo =========================================
echo  Starting Tokyo Dome Info Board...
echo =========================================

cd /d "%~dp0"

call .venv\Scripts\activate

python web_app\app.py

pause