@echo off
echo =========================================
echo  Starting Tokyo Dome Info Board...
echo =========================================

cd /d "%~dp0"

:: .venvが存在しない場合（初回起動時）の自動セットアップ処理
if not exist ".venv\Scripts\activate" (
    echo [INFO] First run detected. Creating virtual environment...
    python -m venv .venv
    
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate
    
    echo [INFO] Installing required packages...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

echo [INFO] Launching app...
python web_app\app.py

pause