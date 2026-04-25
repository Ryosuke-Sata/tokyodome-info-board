import os
import json
import threading
import webbrowser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_FILE = os.path.join(BASE_DIR, "data", "event_data.json")
TRAIN_FILE = os.path.join(BASE_DIR, "data", "train_data.json")

def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_file_mtime(file_path):
    """ファイルの最終更新時刻を取得する"""
    if os.path.exists(file_path):
        dt_obj = datetime.fromtimestamp(os.path.getmtime(file_path))
        return dt_obj.strftime('%m/%d %H:%M')
    return "不明"

@app.route('/')
def index():
    events = load_data(EVENT_FILE)
    trains = load_data(TRAIN_FILE)
    
    # 最終更新時刻の取得
    event_mtime = get_file_mtime(EVENT_FILE)
    train_mtime = get_file_mtime(TRAIN_FILE)

    # 日付計算（今日と明日）
    jst = ZoneInfo("Asia/Tokyo")
    now = datetime.now(jst)
    tomorrow = now + timedelta(days=1)
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    
    today_str = f"今日 {now.month}/{now.day} ({weekdays[now.weekday()]})"
    tomorrow_str = f"明日 {tomorrow.month}/{tomorrow.day} ({weekdays[tomorrow.weekday()]})"
    
    today_idx = now.day - 1
    tomorrow_idx = tomorrow.day - 1

    return render_template('index.html', 
                           events=events, trains=trains,
                           event_mtime=event_mtime, train_mtime=train_mtime,
                           today_str=today_str, tomorrow_str=tomorrow_str,
                           today_idx=today_idx, tomorrow_idx=tomorrow_idx)

if __name__ == '__main__':
    url = "http://127.0.0.1:5000"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(host="0.0.0.0", port=5000, debug=False)