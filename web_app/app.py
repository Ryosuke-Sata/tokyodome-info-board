import os
import json
import threading
import webbrowser
import time
import sys
import signal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, render_template, jsonify, request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import core.tokyodome_eventdata as tokyodome_eventdata
import core.train_troubledata as train_troubledata

app = Flask(__name__)

EVENT_FILE = os.path.join(BASE_DIR, "data", "event_data.json")
TRAIN_FILE = os.path.join(BASE_DIR, "data", "train_data.json")

def auto_update_train():
    """10分おきに電車情報を取得するループ"""
    while True:
        try:
            train_troubledata.main()
        except Exception as e:
            print(f"電車情報の更新に失敗: {e}")
        time.sleep(600)

def auto_update_event():
    """1時間おきにイベント情報を取得するループ"""
    while True:
        try:
            tokyodome_eventdata.fetch_event_data()
        except Exception as e:
            print(f"イベント情報の更新に失敗: {e}")
        time.sleep(3600)


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

@app.route('/api/data')
def get_data():
    force_update = request.args.get('force_update') == 'true'
    
    if force_update:
        print("--- 手動での電車情報更新を開始します ---")
        try:
            train_troubledata.main()
        except Exception as e:
            print(f"手動更新エラー: {e}")

    events = load_data(EVENT_FILE)
    trains = load_data(TRAIN_FILE)
    
    data = {
        "events": events,
        "trains": trains,
        "event_mtime": get_file_mtime(EVENT_FILE),
        "train_mtime": get_file_mtime(TRAIN_FILE)
    }
    return jsonify(data)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("\n--- 終了信号を受信しました。サーバーをシャットダウンします ---")
    
    # 即座に自爆するのではなく、0.5秒後に自爆するタイマーをセットする
    def kill_server():
        os.kill(os.getpid(), signal.SIGINT)
        
    threading.Timer(0.5, kill_server).start()
    
    # タイマーが動いている間に、ブラウザへ「終了するよ」と返事をする
    return jsonify({"status": "shutting down"})

if __name__ == '__main__':
    train_thread = threading.Thread(target=auto_update_train, daemon=True)
    event_thread = threading.Thread(target=auto_update_event, daemon=True)
    train_thread.start()
    event_thread.start()

    url = "http://127.0.0.1:5000"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    app.run(host="0.0.0.0", port=5000, debug=False)