import tkinter as tk
from datetime import datetime
from zoneinfo import ZoneInfo
import locale
import json
import os
import datetime as dt
import tokyodome_eventdata
import train_troubledata
import threading

locale.setlocale(locale.LC_TIME, "ja")
jst = ZoneInfo("Asia/Tokyo")
current_time = datetime.now(jst)

# グローバル変数の管理
counter = 0
status_label = None
status_bar = None
eventdata = []
traindata = []

# フォントサイズの管理
time_fontsize = 200
date_fontsize = 40
event_kind_fontsize = 40
event_name_fontsize = 25
event_time_fontsize = 40
train_kind_fontsize = 40
train_data_fontsize = 15
train_delay_fontsize = 15

# ファイルパスの管理
event_file_path = "event_data.json"
train_file_path = "train_data.json"

# メニューバーの作成
def menubar():
    menu = tk.Menu(root)
    all_menu = tk.Menu(menu, tearoff = 0)
    menu.add_cascade(label = "≡", menu = all_menu)
    all_menu.add_command(label = "終了", command = root.destroy)
    root.config(menu = menu)

# 下部バーの作成
def statusbar():
    # ステータスバーの作成
    global counter, status_label, status_bar
    status_bar = tk.Frame(root, relief = tk.SUNKEN, bd = 1)
    status_bar.pack(side = tk.BOTTOM, fill = tk.X)
    # アプリ経過時間の表示
    status_label = tk.Label(status_bar, text = f"ステータス : {counter}秒経過", anchor = "w")
    status_label.pack(side = tk.LEFT, padx = 10)
    # 終了ボタンの作成
    destroy_button = tk.Button(status_bar, text = "終了", command = root.destroy)
    destroy_button.pack(side = tk.RIGHT, padx = 10)

# 下部バーを最前列に変更する関数
def status_front():
    global status_bar
    status_bar.tkraise()

# 経過時間の計算および時刻と日付の更新
def update_status():
    global counter, status_label, current_time, time, date
    status_label.config(text = f"ステータス : {counter}秒経過")
    counter += 1
    current_time = datetime.now(jst)
    time.config(text = f"{current_time.strftime("%H:%M:%S")}")
    date.config(text = f"{current_time.strftime("%Y年%m月%d日（%a）")}")
    root.after(1000, update_status)

# 日付と時間の表示
def date_time_status():
    # フレームの作成
    global time, date
    time_frame = tk.Frame(root, bd = 1, relief = "solid")
    time_frame.place(
        relx = 1/3,
        rely = 0,
        relwidth = 2/3,
        relheight = 1/2
    )
    # 時間の表示
    time = tk.Label(
        time_frame,
        text = f"{current_time.strftime("%H:%M:%S")}",
        font = ("Yu Gothic UI", time_fontsize))
    time.place(relx = 0.5, rely = 0.5, anchor = "center")
    # 日付の表示
    date = tk.Label(
        time_frame,
        text = f"{current_time.strftime("%Y年%m月%d日（%a）")}",
        font = ("Yu Gothic UI", date_fontsize)
    )
    date.pack(anchor = "nw", padx = 20, pady = 10)

# イベントファイルの読み込み
def read_eventdata():
    global eventdata
    try:
        with open(event_file_path, "r", encoding = "utf-8") as f:
            eventdata = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    except Exception as e:
        pass

# 本日のイベントの表示
def current_event_status():
    global eventdata
    # ファイルの保存時間の取得
    try:
        event_time_timestamp = os.path.getmtime(event_file_path)
        event_time_dt = dt.datetime.fromtimestamp(event_time_timestamp)
        formatted_event_time = event_time_dt.strftime('%m/%d %H:%M:%S')

        print(f"ファイルパス: {event_file_path}")
        print(f"最終更新日時: {formatted_event_time}")

    except FileNotFoundError:
        print(f"エラー: ファイル '{event_file_path}' が見つかりません。")

    current_event_frame = tk.Frame(root, bd = 1, relief = "solid")
    current_event_frame.place(
        relx = 1/3,
        rely = 1/2,
        relwidth = 2/3,
        relheight = 1/2
    )
    if len(eventdata[current_time.day - 1]) <= 3:
        event_kind = ""
        event_name = "予定なし"
        event_time = ""
        event_name_fontsize = 70
    elif len(eventdata[current_time.day - 1]) == 4:
        event_kind = ""
        event_name = ""
        event_time = ""
        event_name_fontsize = 25
    elif len(eventdata[current_time.day - 1]) == 5:
        event_kind = f"{eventdata[current_time.day - 1][3]}"
        event_name = f"{eventdata[current_time.day - 1][4]}"
        event_time = "時間情報なし"
        event_name_fontsize = 25
    elif len(eventdata[current_time.day - 1]) >= 6:
        event_kind = f"{eventdata[current_time.day - 1][3]}"
        event_name = f"{eventdata[current_time.day - 1][4]}"
        event_time = f"{eventdata[current_time.day - 1][5]}"
        event_name_fontsize = 25
    
    # イベントのフォントサイズを，文字列の長さに応じて適切な値に変更する条件分岐を作成する
    # イベント情報の更新時間について考える
    current_event_name = tk.Label(
        current_event_frame,
        text = event_name,
        font = ("Yu Gothic UI", event_name_fontsize)
    )
    current_event_name.place(relx = 0.5, rely = 0.45, anchor = "center")
    # イベント種類の表示
    current_event_kind = tk.Label(
        current_event_frame,
        text = f"本日のイベント : {event_kind}",
        font = ("Yu Gothic UI", event_kind_fontsize)
    )
    current_event_kind.place(relx = 0.01, rely = 0.01, anchor = "nw")
    # ファイル更新時間の表示
    event_update_data = tk.Label(
        current_event_frame,
        text = f"最終更新 : {formatted_event_time}",
        font = ("Yu Gothic UI", 20)
    )
    event_update_data.place(relx = 0.99, rely = 0.01, anchor = "ne")
    # イベント時間の表示
    current_event_time = tk.Label(
        current_event_frame,
        text = f"{event_time}",
        font = ("Yu Gothic UI", event_time_fontsize)
    )
    current_event_time.place(relx = 0.5, rely = 0.75, anchor = "center")
    status_front()

# 電車ファイルの読み込み
def read_traindata():
    global traindata
    try:
        with open(train_file_path, "r", encoding = "utf-8") as f:
            traindata = json.load(f)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    except Exception as e:
        pass

# 電車の運行情報の表示
def current_train_status():
    global traindata
    # ファイルの保存時間の取得
    try:
        train_time_timestamp = os.path.getmtime(train_file_path)
        train_time_dt = dt.datetime.fromtimestamp(train_time_timestamp)
        formatted_train_time = train_time_dt.strftime('%m/%d %H:%M:%S')

        print(f"ファイルパス: {train_file_path}")
        print(f"最終更新日時: {formatted_train_time}")

    except FileNotFoundError:
        print(f"エラー: ファイル '{train_file_path}' が見つかりません。")
    
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
    for i in range(len(traindata)):
        train_delay = tk.Label(
            current_train_frame,
            text = f"・{traindata[i]["路線"]} : {traindata[i]["状況"]}",
            font = ("Yu Gothic UI", train_data_fontsize)
        )
        train_delay.pack(anchor = "nw", padx = 20, pady = 10)
        train_detail = tk.Label(
            current_train_frame,
            text = f"{traindata[i]["詳細"]}",
            font = ("Yu Gothic UI", train_delay_fontsize)
        )
        train_detail.pack(anchor = "nw", padx = 60, pady = 0)
    train_update_data = tk.Label(
        current_train_frame,
        text = f"最終更新 : {formatted_train_time}",
        font = ("Yu Gothic UI", 20)
    )
    train_update_data.pack(anchor = "nw", side = tk.BOTTOM, padx = 20, pady = 25)
    status_front()

def run_scraping_thread():
    train_troubledata.main()
    read_traindata()

def check_scraping_thread(thread):
    if thread.is_alive():
        root.after(100, lambda: check_scraping_thread(thread))
    else:
        current_train_status()
        root.after(600000, train_update_status)

def train_update_status():
    scraping_thread = threading.Thread(target = run_scraping_thread)
    scraping_thread.daemon = True 
    scraping_thread.start()
    check_scraping_thread(scraping_thread)

# rootウィンドウの作成
root = tk.Tk()
root.title("F××k TokyoDome Event")
root.geometry("1600x900")

# 要素の配置
menubar()
statusbar()
date_time_status()
update_status()
read_eventdata()
current_event_status()
read_traindata()
current_train_status()
train_update_status()

# ループ
root.mainloop()