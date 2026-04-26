#!/bin/bash
echo "========================================="
echo " Starting Tokyo Dome Info Board..."
echo "========================================="

# このファイルがあるフォルダ（プロジェクトのルート）に移動
cd "$(dirname "$0")"

# .venvが存在しない場合（初回起動時）の自動セットアップ処理
# Macでは Scripts ではなく bin になります
if [ ! -f ".venv/bin/activate" ]; then
    echo "[INFO] First run detected. Creating virtual environment..."
    # Macのデフォルト環境では python3 コマンドを使うのが一般的です
    python3 -m venv .venv
    
    echo "[INFO] Activating virtual environment..."
    source .venv/bin/activate
    
    echo "[INFO] Installing required packages..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "[INFO] Launching app..."
python web_app/app.py