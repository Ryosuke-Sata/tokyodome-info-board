import tkinter as tk
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import datetime as dt
import threading
import traceback

import tokyodome_eventdata
import train_troubledata

jst = ZoneInfo("Asia/Tokyo")
current_time = datetime.now(jst)

# グローバル変数の管理
counter = 0
status_label = None
status_bar = None
eventdata = []
traindata = []

# ウィジェット参照保持用
current_event_frame = None
current_train_frame = None

# フォントサイズの管理
time_fontsize = 200
date_fontsize = 40
event_kind_fontsize = 40
event_name_fontsize = 25
event_time_fontsize = 40
train_kind_fontsize = 40
train_data_fontsize = 15
train_delay_fontsize = 15

# --- 修正: データディレクトリとファイルパスの管理 ---
DATA_DIR = "data"
event_file_path = os.path.join(DATA_DIR, "event_data.json")
train_file_path = os.path.join(DATA_DIR, "train_data.json")

# 曜日リスト（ロケール依存を回避するため手動設定）
WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

# メニューバーの作成
def menubar():
    menu = tk.Menu(root)
    all_menu = tk.Menu(menu, tearoff = 0)
    menu.add_cascade(label = "≡", menu = all_menu)
    all_menu.add_command(label = "終了", command = root.destroy)
    root.config(menu = menu)

# 下部バーの作成
def statusbar():
    global counter, status_label, status_bar
    status_bar = tk.Frame(root, relief = tk.SUNKEN, bd = 1)
    status_bar.pack(side = tk.BOTTOM, fill = tk.X)
    status_label = tk.Label(status_bar, text = f"ステータス : {counter}秒経過", anchor = "w")
    status_label.pack(side = tk.LEFT, padx = 10)
    destroy_button = tk.Button(status_bar, text = "終了", command = root.destroy)
    destroy_button.pack(side = tk.RIGHT, padx = 10)

def status_front():
    global status_bar
    if status_bar:
        status_bar.tkraise()

def update_status():
    global counter, status_label, current_time, time, date
    
    counter += 1
    status_label.config(text = f"ステータス : {counter}秒経過")
    
    current_time = datetime.now(jst)
    
    # --- 修正: 曜日の取得ロジックを変更 ---
    time_str = current_time.strftime("%H:%M:%S")
    # weekday()は 0=月, 6=日 を返す
    w_idx = current_time.weekday()
    date_str = f"{current_time.strftime('%Y年%m月%d日')}（{WEEKDAYS[w_idx]}）"
    
    time.config(text = time_str)
    date.config(text = date_str)
    
    root.after(1000, update_status)

def date_time_status():
    global time, date
    time_frame = tk.Frame(root, bd = 1, relief = "solid")
    time_frame.place(
        relx = 1/3,
        rely = 0,
        relwidth = 2/3,
        relheight = 1/2
    )
    time = tk.Label(
        time_frame,
        text = f"{current_time.strftime('%H:%M:%S')}",
        font = ("Yu Gothic UI", time_fontsize))
    time.place(relx = 0.5, rely = 0.5, anchor = "center")
    
    # --- 修正: 初回表示の曜日ロジックも変更 ---
    w_idx = current_time.weekday()
    initial_date_str = f"{current_time.strftime('%Y年%m月%d日')}（{WEEKDAYS[w_idx]}）"

    date = tk.Label(
        time_frame,
        text = initial_date_str,
        font = ("Yu Gothic UI", date_fontsize)
    )
    date.pack(anchor = "nw", padx = 20, pady = 10)

def read_eventdata():
    global eventdata
    try:
        if not os.path.exists(event_file_path):
            return
        
        with open(event_file_path, "r", encoding = "utf-8") as f:
            eventdata = json.load(f)
    except Exception:
        print("イベントデータの読み込みに失敗しました。")
        traceback.print_exc()

def current_event_status():
    global eventdata, current_event_frame
    
    if current_event_frame is not None:
        current_event_frame.destroy()

    formatted_event_time = "不明"
    try:
        if os.path.exists(event_file_path):
            event_time_timestamp = os.path.getmtime(event_file_path)
            event_time_dt = dt.datetime.fromtimestamp(event_time_timestamp)
            formatted_event_time = event_time_dt.strftime('%m/%d %H:%M:%S')
    except Exception:
        pass

    current_event_frame = tk.Frame(root, bd = 1, relief = "solid")
    current_event_frame.place(
        relx = 1/3,
        rely = 1/2,
        relwidth = 2/3,
        relheight = 1/2
    )

    event_kind = ""
    event_name = "データなし"
    event_time = ""
    local_event_name_fontsize = event_name_fontsize

    try:
        day_index = current_time.day - 1
        
        if eventdata and 0 <= day_index < len(eventdata):
            day_data = eventdata[day_index]
            
            if len(day_data) <= 3:
                event_name = "予定なし"
                local_event_name_fontsize = 70
            elif len(day_data) == 4:
                pass
            elif len(day_data) == 5:
                event_kind = f"{day_data[3]}"
                event_name = f"{day_data[4]}"
                event_time = "時間情報なし"
            elif len(day_data) >= 6:
                event_kind = f"{day_data[3]}"
                event_name = f"{day_data[4]}"
                event_time = f"{day_data[5]}"
    except Exception:
        event_name = "データ読込エラー"
        traceback.print_exc()
    
    current_event_name = tk.Label(
        current_event_frame,
        text = event_name,
        font = ("Yu Gothic UI", local_event_name_fontsize)
    )
    current_event_name.place(relx = 0.5, rely = 0.45, anchor = "center")
    
    current_event_kind = tk.Label(
        current_event_frame,
        text = f"本日のイベント : {event_kind}",
        font = ("Yu Gothic UI", event_kind_fontsize)
    )
    current_event_kind.place(relx = 0.01, rely = 0.01, anchor = "nw")
    
    event_update_data = tk.Label(
        current_event_frame,
        text = f"最終更新 : {formatted_event_time}",
        font = ("Yu Gothic UI", 20)
    )
    event_update_data.place(relx = 0.99, rely = 0.01, anchor = "ne")
    
    current_event_time_label = tk.Label(
        current_event_frame,
        text = f"{event_time}",
        font = ("Yu Gothic UI", event_time_fontsize)
    )
    current_event_time_label.place(relx = 0.5, rely = 0.75, anchor = "center")
    
    status_front()

def read_traindata():
    global traindata
    try:
        if not os.path.exists(train_file_path):
            return
        
        with open(train_file_path, "r", encoding = "utf-8") as f:
            traindata = json.load(f)
    except Exception:
        print("電車データの読み込みに失敗しました。")
        traceback.print_exc()

def current_train_status():
    global traindata, current_train_frame
    
    if current_train_frame is not None:
        current_train_frame.destroy()

    formatted_train_time = "不明"
    try:
        if os.path.exists(train_file_path):
            train_time_timestamp = os.path.getmtime(train_file_path)
            train_time_dt = dt.datetime.fromtimestamp(train_time_timestamp)
            formatted_train_time = train_time_dt.strftime('%m/%d %H:%M:%S')
    except Exception:
        pass
    
    current_train_frame = tk.Frame(root, bd = 1, relief = "solid")
    current_train_frame.place(
        relx = 0,
        rely = 0,
        relwidth = 1/3,
        relheight = 1
    )
    current_train = tk.Label(
        current_train_frame,
        text = "現在の運行情報",
        font = ("Yu Gothic UI", train_kind_fontsize)
    )
    current_train.pack(anchor = "nw", padx = 20, pady = 10)
    
    if traindata:
        for item in traindata:
            line = item.get("路線", "不明")
            status = item.get("状況", "不明")
            detail = item.get("詳細", "")
            
            train_delay = tk.Label(
                current_train_frame,
                text = f"・{line} : {status}",
                font = ("Yu Gothic UI", train_data_fontsize)
            )
            train_delay.pack(anchor = "nw", padx = 20, pady = 10)
            
            train_detail = tk.Label(
                current_train_frame,
                text = f"{detail}",
                font = ("Yu Gothic UI", train_delay_fontsize),
                wraplength=400,
                justify="left"
            )
            train_detail.pack(anchor = "nw", padx = 60, pady = 0)
    else:
        no_info = tk.Label(
            current_train_frame,
            text = "現在、遅延情報はありません\nまたはデータ取得中です",
            font = ("Yu Gothic UI", train_data_fontsize)
        )
        no_info.pack(anchor = "nw", padx = 20, pady = 20)

    train_update_data = tk.Label(
        current_train_frame,
        text = f"最終更新 : {formatted_train_time}",
        font = ("Yu Gothic UI", 20)
    )
    train_update_data.pack(anchor = "nw", side = tk.BOTTOM, padx = 20, pady = 25)
    
    status_front()

def run_train_scraping_thread():
    try:
        train_troubledata.main()
    except Exception:
        print("電車情報の更新スレッドでエラーが発生しました。")
    root.after(0, after_train_scraping)

def after_train_scraping():
    read_traindata()
    current_train_status()
    root.after(600000, start_train_update_cycle)

def start_train_update_cycle():
    scraping_thread = threading.Thread(target=run_train_scraping_thread)
    scraping_thread.daemon = True 
    scraping_thread.start()

def run_event_scraping_thread():
    try:
        tokyodome_eventdata.fetch_event_data()
    except Exception:
        print("イベント情報の更新スレッドでエラーが発生しました。")
    root.after(0, after_event_scraping)

def after_event_scraping():
    read_eventdata()
    current_event_status()
    root.after(3600000, start_event_update_cycle)

def start_event_update_cycle():
    scraping_thread = threading.Thread(target=run_event_scraping_thread)
    scraping_thread.daemon = True
    scraping_thread.start()

root = tk.Tk()
root.title("TokyoDome Event Info")
root.geometry("1600x900")

menubar()
statusbar()
date_time_status()
update_status()

read_eventdata()
current_event_status()
read_traindata()
current_train_status()

root.after(1000, start_event_update_cycle)
root.after(1000, start_train_update_cycle)

root.mainloop()