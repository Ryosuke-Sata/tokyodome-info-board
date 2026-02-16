import customtkinter as ctk
import tkinter as tk  # 一部標準機能用
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import datetime as dt
import threading
import traceback

# データ取得モジュールのインポート（変更なし）
import tokyodome_eventdata
import train_troubledata

# --- テーマとカラー設定 ---
ctk.set_appearance_mode("dark")  # ダークモード設定
ctk.set_default_color_theme("blue")  # アクセントカラー

# カラーパレット定義
COLOR_BG = "#1A1A1A"            # 背景色
COLOR_FRAME = "#2B2B2B"         # フレーム背景色
COLOR_TEXT_MAIN = "#FFFFFF"     # メインテキスト色
COLOR_TEXT_SUB = "#AAAAAA"      # サブテキスト色
COLOR_ACCENT_RED = "#FF5555"    # 強調色（赤）
COLOR_ACCENT_GREEN = "#55FF55"  # 強調色（緑）

# フォント設定（モダンなフォントを指定）
FONT_MAIN = ("Meiryo UI", 12)
FONT_TIME = ("Meiryo UI", 100, "bold")
FONT_DATE = ("Meiryo UI", 24)
FONT_EVENT_TITLE = ("Meiryo UI", 16, "bold")
FONT_EVENT_NAME = ("Meiryo UI", 32, "bold")
FONT_TRAIN_TITLE = ("Meiryo UI", 18, "bold")
FONT_TRAIN_INFO = ("Meiryo UI", 14)
FONT_STATUS = ("Meiryo UI", 10)

jst = ZoneInfo("Asia/Tokyo")
current_time = datetime.now(jst)

# グローバル変数の管理
counter = 0
status_label = None
eventdata = []
traindata = []

# ウィジェット参照保持用
datetime_frame_ref = None
current_event_frame_ref = None
current_train_scroll_frame_ref = None

# データディレクトリとファイルパスの管理（変更なし）
DATA_DIR = "data"
event_file_path = os.path.join(DATA_DIR, "event_data.json")
train_file_path = os.path.join(DATA_DIR, "train_data.json")

# 曜日リスト
WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

# --- GUIコンポーネント構築関数 ---

def setup_gui_layout():
    """メインウィンドウのグリッドレイアウトを設定"""
    # 左側（電車情報）:右側（日時・イベント） = 1:2 の比率
    root.grid_columnconfigure(0, weight=1, minsize=400)
    root.grid_columnconfigure(1, weight=2)
    # 上段（日時）:中段（イベント）:下段（ステータス）
    root.grid_rowconfigure(0, weight=1, minsize=200)
    root.grid_rowconfigure(1, weight=2)
    root.grid_rowconfigure(2, weight=0, minsize=40)

def create_statusbar():
    """ステータスバーと終了ボタンを作成"""
    global counter, status_label
    
    status_frame = ctk.CTkFrame(root, corner_radius=0, fg_color=COLOR_FRAME, height=40)
    status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    
    status_label = ctk.CTkLabel(status_frame, text=f"ステータス : 起動中...", font=FONT_STATUS, text_color=COLOR_TEXT_SUB)
    status_label.pack(side=tk.LEFT, padx=20)
    
    # スタイリッシュな終了ボタン
    destroy_button = ctk.CTkButton(status_frame, text="終了", command=root.destroy, 
                                     fg_color=COLOR_ACCENT_RED, hover_color="#CC4444", 
                                     width=80, height=30, font=FONT_STATUS)
    destroy_button.pack(side=tk.RIGHT, padx=20, pady=5)

def update_time_and_status_logic():
    """時刻とステータスの更新ロジック"""
    global counter, status_label, current_time, datetime_frame_ref
    
    counter += 1
    status_label.configure(text=f"システム稼働時間 : {counter} 秒経過")
    
    current_time = datetime.now(jst)
    time_str = current_time.strftime("%H:%M:%S")
    w_idx = current_time.weekday()
    date_str = f"{current_time.strftime('%Y.%m.%d')} ({WEEKDAYS[w_idx]})"
    
    # DateTimeフレーム内のラベルを更新
    if datetime_frame_ref:
        for widget in datetime_frame_ref.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                if widget.cget("font") == FONT_TIME:
                    widget.configure(text=time_str)
                elif widget.cget("font") == FONT_DATE:
                    widget.configure(text=date_str)

    root.after(1000, update_time_and_status_logic)

def create_datetime_frame():
    """日時表示フレームを作成"""
    global datetime_frame_ref
    datetime_frame = ctk.CTkFrame(root, corner_radius=15, fg_color=COLOR_FRAME)
    datetime_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=(20, 10))
    datetime_frame_ref = datetime_frame

    # 初期表示用の日時文字列
    w_idx = current_time.weekday()
    date_str = f"{current_time.strftime('%Y.%m.%d')} ({WEEKDAYS[w_idx]})"
    time_str = current_time.strftime("%H:%M:%S")
    
    time_label = ctk.CTkLabel(datetime_frame, text=time_str, font=FONT_TIME, text_color=COLOR_TEXT_MAIN)
    time_label.place(relx=0.5, rely=0.45, anchor="center")
    
    date_label = ctk.CTkLabel(datetime_frame, text=date_str, font=FONT_DATE, text_color=COLOR_TEXT_SUB)
    date_label.place(relx=0.5, rely=0.8, anchor="center")

def read_eventdata():
    global eventdata
    try:
        if not os.path.exists(event_file_path):
            eventdata = []
            return
        with open(event_file_path, "r", encoding="utf-8") as f:
            eventdata = json.load(f)
    except Exception:
        print("イベントデータの読み込みに失敗しました。")
        traceback.print_exc()
        eventdata = []

def update_event_ui():
    """イベント情報UIを更新"""
    global eventdata, current_event_frame_ref
    
    # フレームの再作成（内部のクリアのため）
    if current_event_frame_ref is not None:
        current_event_frame_ref.destroy()

    # 新しいフレームを作成
    event_frame = ctk.CTkFrame(root, corner_radius=15, fg_color=COLOR_FRAME)
    event_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(10, 20))
    current_event_frame_ref = event_frame

    # 最終更新時刻の取得
    formatted_event_time = "不明"
    try:
        if os.path.exists(event_file_path):
            event_time_timestamp = os.path.getmtime(event_file_path)
            event_time_dt = dt.datetime.fromtimestamp(event_time_timestamp)
            formatted_event_time = event_time_dt.strftime('%m/%d %H:%M')
    except Exception:
        pass

    # データの解析
    event_kind = "-"
    event_name = "データなし"
    event_time = "-"
    name_text_color = COLOR_TEXT_MAIN

    try:
        day_index = current_time.day - 1
        if eventdata and 0 <= day_index < len(eventdata):
            day_data = eventdata[day_index]
            if len(day_data) <= 3:
                event_name = "本日の予定はありません"
                name_text_color = COLOR_TEXT_SUB
            elif len(day_data) >= 5:
                event_kind = f"{day_data[3]}"
                event_name = f"{day_data[4]}"
                if len(day_data) >= 6:
                    event_time = f"{day_data[5]}"
                else:
                    event_time = "時間情報なし"
        else:
             event_name = "データ取得中または予定なし"
             name_text_color = COLOR_TEXT_SUB
    except Exception:
        event_name = "データ読込エラー"
        name_text_color = COLOR_ACCENT_RED
        traceback.print_exc()
    
    # UIパーツの配置
    title_label = ctk.CTkLabel(event_frame, text="TOKYO DOME EVENT", font=FONT_EVENT_TITLE, text_color=COLOR_TEXT_SUB)
    title_label.pack(anchor="nw", padx=20, pady=(20, 0))

    kind_label = ctk.CTkLabel(event_frame, text=event_kind, font=("Meiryo UI", 20), text_color=COLOR_ACCENT_GREEN)
    kind_label.pack(anchor="w", padx=20, pady=(10, 0))

    name_label = ctk.CTkLabel(event_frame, text=event_name, font=FONT_EVENT_NAME, text_color=name_text_color, wraplength=600)
    name_label.pack(anchor="w", padx=20, pady=(10, 20))
    
    time_label = ctk.CTkLabel(event_frame, text=f"OPEN/START: {event_time}", font=("Meiryo UI", 18), text_color=COLOR_TEXT_MAIN)
    time_label.pack(anchor="w", padx=20, pady=(0, 10))
    
    update_label = ctk.CTkLabel(event_frame, text=f"最終更新 : {formatted_event_time}", font=FONT_STATUS, text_color=COLOR_TEXT_SUB)
    update_label.pack(side=tk.BOTTOM, anchor="se", padx=20, pady=15)


def read_traindata():
    global traindata
    try:
        if not os.path.exists(train_file_path):
            traindata = []
            return
        with open(train_file_path, "r", encoding="utf-8") as f:
            traindata = json.load(f)
    except Exception:
        print("電車データの読み込みに失敗しました。")
        traceback.print_exc()
        traindata = []

def update_train_ui():
    """電車運行情報UIを更新"""
    global traindata, current_train_scroll_frame_ref
    
    # フレームの再作成
    if current_train_scroll_frame_ref is not None:
        current_train_scroll_frame_ref.destroy()
    
    # 親フレーム（タイトルとスクロールエリアを格納）
    train_parent_frame = ctk.CTkFrame(root, corner_radius=15, fg_color=COLOR_FRAME)
    train_parent_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(20, 10), pady=20)
    
    # タイトル
    title_label = ctk.CTkLabel(train_parent_frame, text="首都圏の運行情報", font=FONT_TRAIN_TITLE, text_color=COLOR_TEXT_MAIN)
    title_label.pack(anchor="nw", padx=20, pady=(20, 10))

    # スクロール可能なフレームを作成
    scroll_frame = ctk.CTkScrollableFrame(train_parent_frame, corner_radius=10, fg_color="transparent")
    scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    current_train_scroll_frame_ref = train_parent_frame # 参照を保持するのは親フレーム

    # 最終更新時刻
    formatted_train_time = "不明"
    try:
        if os.path.exists(train_file_path):
            train_time_timestamp = os.path.getmtime(train_file_path)
            train_time_dt = dt.datetime.fromtimestamp(train_time_timestamp)
            formatted_train_time = train_time_dt.strftime('%m/%d %H:%M')
    except Exception:
        pass

    # データ表示
    if traindata:
        for item in traindata:
            line = item.get("路線", "不明")
            status = item.get("状況", "不明")
            detail = item.get("詳細", "")
            
            # 状況に応じて色を変える（視認性向上）
            status_color = COLOR_ACCENT_RED if "平常" not in status and "不明" not in status else COLOR_TEXT_MAIN
            
            # 各路線の情報カード
            card = ctk.CTkFrame(scroll_frame, corner_radius=8, fg_color="#333333", border_width=1, border_color="#444444")
            card.pack(fill=tk.X, pady=5, padx=5)
            
            header = ctk.CTkLabel(card, text=f"● {line}", font=FONT_TRAIN_INFO, text_color=COLOR_TEXT_MAIN, anchor="w")
            header.pack(fill=tk.X, padx=10, pady=(10, 0))
            
            status_lbl = ctk.CTkLabel(card, text=f"状況: {status}", font=("Meiryo UI", 14, "bold"), text_color=status_color, anchor="w")
            status_lbl.pack(fill=tk.X, padx=10, pady=(5, 0))
            
            detail_lbl = ctk.CTkLabel(card, text=detail, font=("Meiryo UI", 12), text_color=COLOR_TEXT_SUB, wraplength=350, anchor="w", justify="left")
            detail_lbl.pack(fill=tk.X, padx=10, pady=(5, 10))

    else:
        no_info = ctk.CTkLabel(
            scroll_frame,
            text="現在、主要な遅延情報はありません\nまたはデータを取得中です...",
            font=FONT_TRAIN_INFO,
            text_color=COLOR_TEXT_SUB,
            anchor="center"
        )
        no_info.pack(pady=50)

    update_label = ctk.CTkLabel(train_parent_frame, text=f"最終更新 : {formatted_train_time}", font=FONT_STATUS, text_color=COLOR_TEXT_SUB)
    update_label.pack(side=tk.BOTTOM, anchor="sw", padx=20, pady=15)


# --- スレッド処理（変更なし） ---
# ロジック部分は既存のコードをそのまま流用します

def run_train_scraping_thread():
    try:
        train_troubledata.main()
    except Exception:
        print("電車情報の更新スレッドでエラーが発生しました。")
    root.after(0, after_train_scraping)

def after_train_scraping():
    read_traindata()
    update_train_ui() # UI更新関数名を変更
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
    update_event_ui() # UI更新関数名を変更
    root.after(3600000, start_event_update_cycle)

def start_event_update_cycle():
    scraping_thread = threading.Thread(target=run_event_scraping_thread)
    scraping_thread.daemon = True
    scraping_thread.start()

# --- メイン処理 ---

# ルートウィンドウの作成（tk.Tkの代わりにctk.CTkを使用）
root = ctk.CTk()
root.title("Tokyo Dome Info Board")
# ウィンドウサイズを少し小さく固定して密度感を出す（レイアウト崩れ防止）
root.geometry("1280x720")
root.resizable(False, False)

# レイアウト設定
setup_gui_layout()

# 各UIコンポーネントの作成と配置
create_statusbar()
create_datetime_frame()

# 初期データの読み込みと表示
read_eventdata()
update_event_ui()
read_traindata()
update_train_ui()

# 時計更新の開始
update_time_and_status_logic()

# バックグラウンド更新の開始
root.after(1000, start_event_update_cycle)
root.after(1000, start_train_update_cycle)

# ループ開始
root.mainloop()