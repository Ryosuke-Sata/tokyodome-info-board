import customtkinter as ctk
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import traceback
import datetime as dt

# データ取得モジュールのインポート
import core.tokyodome_eventdata as tokyodome_eventdata
import core.train_troubledata as train_troubledata

# --- テーマとカラー設定 ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# カラーパレット定義
COLOR_BG = "#1A1A1A"
COLOR_FRAME = "#2B2B2B"
COLOR_CARD_BG = "#333333"  # 内部カード用
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_SUB = "#AAAAAA"
COLOR_ACCENT_RED = "#FF5555"
COLOR_ACCENT_GREEN = "#55FF55"

# URL定義
URL_EVENT = "https://www.tokyo-dome.co.jp/dome/event/schedule.html"
URL_TRAIN = "https://transit.yahoo.co.jp/diainfo/area/4"

# フォント設定
FONT_MAIN = ("Meiryo UI", 12)
FONT_TIME = ("Meiryo UI", 100, "bold")
FONT_DATE = ("Meiryo UI", 24)
FONT_EVENT_TITLE = ("Meiryo UI", 16, "bold")
FONT_EVENT_NAME = ("Meiryo UI", 24, "bold") # 少しサイズ調整
FONT_EVENT_DATE = ("Meiryo UI", 14, "bold")
FONT_TRAIN_TITLE = ("Meiryo UI", 18, "bold")
FONT_TRAIN_INFO = ("Meiryo UI", 14)
FONT_STATUS = ("Meiryo UI", 10)
FONT_BTN = ("Meiryo UI", 11)

jst = ZoneInfo("Asia/Tokyo")
current_time = datetime.now(jst)

# グローバル変数
counter = 0
status_label = None
eventdata = []
traindata = []

# ウィジェット参照保持用
datetime_frame_ref = None
current_event_frame_ref = None
current_train_scroll_frame_ref = None
train_refresh_btn_ref = None

# データディレクトリ
DATA_DIR = "data"
event_file_path = os.path.join(DATA_DIR, "event_data.json")
train_file_path = os.path.join(DATA_DIR, "train_data.json")

WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]

# --- URLを開く関数 ---
def open_url(url):
    webbrowser.open(url)

# --- GUIコンポーネント構築関数 ---

def setup_gui_layout():
    """メインウィンドウのグリッドレイアウトを設定"""
    root.grid_columnconfigure(0, weight=1, minsize=400)
    root.grid_columnconfigure(1, weight=2)
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
    """イベント情報UIを更新（今日と明日を左右に並べて表示）"""
    global eventdata, current_event_frame_ref
    
    if current_event_frame_ref is not None:
        current_event_frame_ref.destroy()

    event_frame = ctk.CTkFrame(root, corner_radius=15, fg_color=COLOR_FRAME)
    event_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(10, 20))
    current_event_frame_ref = event_frame

    # --- ヘッダー部分 ---
    header_frame = ctk.CTkFrame(event_frame, fg_color="transparent")
    header_frame.pack(fill=tk.X, padx=20, pady=(15, 0))

    title_label = ctk.CTkLabel(header_frame, text="TOKYO DOME EVENT", font=FONT_EVENT_TITLE, text_color=COLOR_TEXT_SUB)
    title_label.pack(side=tk.LEFT)

    link_btn = ctk.CTkButton(header_frame, text="公式サイト ↗", width=80, height=24, font=FONT_BTN,
                             fg_color="transparent", border_width=1, border_color="#555555",
                             command=lambda: open_url(URL_EVENT))
    link_btn.pack(side=tk.RIGHT)

    # --- コンテンツエリア（左右分割） ---
    content_area = ctk.CTkFrame(event_frame, fg_color="transparent")
    content_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # グリッド設定（2カラム）
    content_area.grid_columnconfigure(0, weight=1)
    content_area.grid_columnconfigure(1, weight=1)
    content_area.grid_rowconfigure(0, weight=1)

    # 日付計算
    today_date = current_time
    tomorrow_date = current_time + timedelta(days=1)
    
    # 曜日取得
    w_idx_today = today_date.weekday()
    w_idx_tom = tomorrow_date.weekday()
    
    today_str = f"今日 {today_date.month}/{today_date.day} ({WEEKDAYS[w_idx_today]})"
    tomorrow_str = f"明日 {tomorrow_date.month}/{tomorrow_date.day} ({WEEKDAYS[w_idx_tom]})"

    # --- インデックスによるデータ取得ロジック ---
    # リストは1日=インデックス0 から始まると仮定
    today_index = today_date.day - 1
    tomorrow_index = today_index + 1

    def get_event_data_by_index(idx):
        """インデックスを指定してイベント情報を取得"""
        kind = "-"
        name = "予定なし"
        time = "-"
        is_active = False

        if eventdata and 0 <= idx < len(eventdata):
            day_data = eventdata[idx]
            if len(day_data) <= 3:
                name = "予定はありません"
            elif len(day_data) >= 5:
                kind = f"{day_data[3]}"
                name = f"{day_data[4]}"
                is_active = True
                if len(day_data) >= 6:
                    time = f"{day_data[5]}"
                else:
                    time = "時間情報なし"
        else:
            name = "データなし"
        
        return kind, name, time, is_active

    # 内部関数: カード描画
    def create_event_card(parent, col, title_text, data_idx):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=COLOR_CARD_BG)
        card.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        
        # データの取得
        kind, name, time, is_active = get_event_data_by_index(data_idx)
        name_color = COLOR_TEXT_MAIN if is_active else COLOR_TEXT_SUB

        # 日付見出し
        lbl_date = ctk.CTkLabel(card, text=title_text, font=FONT_EVENT_DATE, text_color=COLOR_TEXT_SUB)
        lbl_date.pack(anchor="w", padx=15, pady=(15, 5))
        
        # イベント種別
        lbl_kind = ctk.CTkLabel(card, text=kind, font=("Meiryo UI", 16), text_color=COLOR_ACCENT_GREEN)
        lbl_kind.pack(anchor="w", padx=15, pady=(5, 0))
        
        # イベント名
        lbl_name = ctk.CTkLabel(card, text=name, font=FONT_EVENT_NAME, text_color=name_color, wraplength=400, justify="left")
        lbl_name.pack(anchor="w", padx=15, pady=(5, 10))
        
        # 時間
        lbl_time = ctk.CTkLabel(card, text=f"OPEN/START: {time}", font=("Meiryo UI", 14), text_color=COLOR_TEXT_MAIN)
        lbl_time.pack(anchor="w", padx=15, pady=(0, 15))

    # カードの生成（左：今日、右：明日）
    create_event_card(content_area, 0, today_str, today_index)
    create_event_card(content_area, 1, tomorrow_str, tomorrow_index)

    # --- 最終更新時刻 ---
    formatted_event_time = "不明"
    try:
        if os.path.exists(event_file_path):
            event_time_timestamp = os.path.getmtime(event_file_path)
            event_time_dt = dt.datetime.fromtimestamp(event_time_timestamp)
            formatted_event_time = event_time_dt.strftime('%m/%d %H:%M')
    except Exception:
        pass

    update_label = ctk.CTkLabel(event_frame, text=f"最終更新 : {formatted_event_time}", font=FONT_STATUS, text_color=COLOR_TEXT_SUB)
    update_label.pack(side=tk.BOTTOM, anchor="se", padx=20, pady=10)


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
    global traindata, current_train_scroll_frame_ref, train_refresh_btn_ref
    
    if current_train_scroll_frame_ref is not None:
        current_train_scroll_frame_ref.destroy()
    
    train_parent_frame = ctk.CTkFrame(root, corner_radius=15, fg_color=COLOR_FRAME)
    train_parent_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(20, 10), pady=20)
    
    # --- ヘッダー部分 ---
    header_frame = ctk.CTkFrame(train_parent_frame, fg_color="transparent")
    header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

    title_label = ctk.CTkLabel(header_frame, text="首都圏の運行情報", font=FONT_TRAIN_TITLE, text_color=COLOR_TEXT_MAIN)
    title_label.pack(side=tk.LEFT)

    btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    btn_frame.pack(side=tk.RIGHT)

    # 更新ボタン
    refresh_btn = ctk.CTkButton(btn_frame, text="↻ 更新", width=60, height=24, font=FONT_BTN,
                                fg_color="#444444", hover_color="#555555",
                                command=start_manual_train_update)
    refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
    train_refresh_btn_ref = refresh_btn 

    link_btn = ctk.CTkButton(btn_frame, text="Yahoo!路線 ↗", width=80, height=24, font=FONT_BTN,
                             fg_color="transparent", border_width=1, border_color="#555555",
                             command=lambda: open_url(URL_TRAIN))
    link_btn.pack(side=tk.LEFT)
    # ------------------

    scroll_frame = ctk.CTkScrollableFrame(train_parent_frame, corner_radius=10, fg_color="transparent")
    scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    current_train_scroll_frame_ref = train_parent_frame

    formatted_train_time = "不明"
    try:
        if os.path.exists(train_file_path):
            train_time_timestamp = os.path.getmtime(train_file_path)
            train_time_dt = dt.datetime.fromtimestamp(train_time_timestamp)
            formatted_train_time = train_time_dt.strftime('%m/%d %H:%M')
    except Exception:
        pass

    if traindata:
        for item in traindata:
            line = item.get("路線", "不明")
            status = item.get("状況", "不明")
            detail = item.get("詳細", "")
            
            status_color = COLOR_ACCENT_RED if "平常" not in status and "不明" not in status else COLOR_TEXT_MAIN
            
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


# --- スレッド処理 (UIブロック回避) ---

def start_manual_train_update():
    """手動更新をUIスレッドをブロックせずに開始する"""
    global train_refresh_btn_ref
    if train_refresh_btn_ref:
        train_refresh_btn_ref.configure(text="更新中...", state="disabled")
    
    thread = threading.Thread(target=run_train_scraping_thread_bg)
    thread.daemon = True
    thread.start()

def run_train_scraping_thread_bg():
    print("バックグラウンド更新を開始します...")
    try:
        train_troubledata.main()
    except Exception:
        print("電車情報の更新スレッドでエラーが発生しました。")
    
    root.after(0, after_manual_train_scraping)

def after_manual_train_scraping():
    global train_refresh_btn_ref
    read_traindata()
    update_train_ui()
    print("バックグラウンド更新完了")
    if train_refresh_btn_ref:
        train_refresh_btn_ref.configure(text="↻ 更新", state="normal")

# --- 自動更新ループ ---

def run_train_auto_update_loop():
    try:
        train_troubledata.main()
    except Exception:
        pass
    root.after(0, lambda: [read_traindata(), update_train_ui()])
    root.after(600000, start_train_update_cycle_bg)

def start_train_update_cycle_bg():
    thread = threading.Thread(target=run_train_auto_update_loop)
    thread.daemon = True
    thread.start()

def run_event_auto_update_loop():
    try:
        tokyodome_eventdata.fetch_event_data()
    except Exception:
        pass
    root.after(0, lambda: [read_eventdata(), update_event_ui()])
    root.after(3600000, start_event_update_cycle_bg)

def start_event_update_cycle_bg():
    thread = threading.Thread(target=run_event_auto_update_loop)
    thread.daemon = True
    thread.start()

# --- メイン処理 ---

root = ctk.CTk()
root.title("Tokyo Dome Info Board")
root.geometry("1280x720")
root.resizable(False, False)

setup_gui_layout()

create_statusbar()
create_datetime_frame()

read_eventdata()
update_event_ui()
read_traindata()
update_train_ui()

update_time_and_status_logic()

# バックグラウンド更新の開始
root.after(1000, start_event_update_cycle_bg)
root.after(1000, start_train_update_cycle_bg)

root.mainloop()