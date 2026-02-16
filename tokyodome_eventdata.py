import requests
from bs4 import BeautifulSoup
import json
import os
import traceback

def fetch_event_data():
    """東京ドームのイベント情報を取得し、JSONに保存する関数"""
    print("--- 東京ドームイベント情報の取得を開始します ---")
    try:
        url = "https://www.tokyo-dome.co.jp/dome/event/schedule.html"
        req = requests.get(url, timeout=10) # タイムアウトを設定
        req.encoding = req.apparent_encoding

        bsObj = BeautifulSoup(req.text, "html.parser")

        month_elements = bsObj.find_all("p", class_ = "c-ttl-set-calender")
        month = []
        for i in month_elements:
            month.append(i.text)

        calender_elements = bsObj.find_all(class_ = "c-mod-calender__item")
        calender = []
        # リスト内包表記のエラーを防ぐため、安全に処理
        for i in calender_elements:
            text_lines = i.text.split("\n")
            cleaned_lines = list(filter(None, text_lines))
            calender.append(cleaned_lines)

        month_count = -1
        # インデックスエラー対策：monthリストが空でないか確認
        if not month:
            print("警告: 月のデータが取得できませんでした。")
            return

        for i in calender:
            # 安全策: i が空でないことを確認
            if not i:
                continue
            
            if i[0] == "01":
                month_count += 1
                # monthリストの範囲外アクセスを防ぐ
                if month_count < len(month):
                    i.insert(0, month[month_count])
            else:
                if month_count >= 0 and month_count < len(month):
                    i.insert(0, month[month_count])

        for i in range(len(calender)):
            if len(calender[i]) >= 5:
                if calender[i][4] == "TOKYO DOME TOUR":
                    del calender[i][3:5]
                else:
                    pass
            else:
                pass
        
        # --- Atomic Write (安全な書き込み) ---
        # 書き込み中に読み込みが発生してファイルが壊れるのを防ぐため、
        # 一時ファイルに書いてからリネームする
        temp_file = "event_data.json.tmp"
        final_file = "event_data.json"
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(calender, f, indent=4, ensure_ascii=False)
        
        os.replace(temp_file, final_file)
        print("東京ドームイベント情報の更新が完了しました。")

    except Exception:
        print("エラー: 東京ドーム情報の取得中に問題が発生しました。")
        traceback.print_exc()

if __name__ == "__main__":
    fetch_event_data()