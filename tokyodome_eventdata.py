import requests
from bs4 import BeautifulSoup
import json
import os
import traceback

def fetch_event_data():
    """東京ドームのイベント情報を取得し、data/event_data.jsonに保存する関数"""
    print("--- 東京ドームイベント情報の取得を開始します ---")
    try:
        url = "https://www.tokyo-dome.co.jp/dome/event/schedule.html"
        req = requests.get(url, timeout=10)
        req.encoding = req.apparent_encoding

        bsObj = BeautifulSoup(req.text, "html.parser")

        month_elements = bsObj.find_all("p", class_ = "c-ttl-set-calender")
        month = []
        for i in month_elements:
            month.append(i.text)

        calender_elements = bsObj.find_all(class_ = "c-mod-calender__item")
        calender = []
        for i in calender_elements:
            text_lines = i.text.split("\n")
            cleaned_lines = list(filter(None, text_lines))
            calender.append(cleaned_lines)

        month_count = -1
        if not month:
            print("警告: 月のデータが取得できませんでした。")
            return

        for i in calender:
            if not i:
                continue
            
            if i[0] == "01":
                month_count += 1
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
        
        # --- 修正: データ保存先を data ディレクトリに変更 ---
        DATA_DIR = "data"
        # ディレクトリが存在しない場合は作成
        os.makedirs(DATA_DIR, exist_ok=True)

        temp_file = os.path.join(DATA_DIR, "event_data.json.tmp")
        final_file = os.path.join(DATA_DIR, "event_data.json")
        
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(calender, f, indent=4, ensure_ascii=False)
        
        os.replace(temp_file, final_file)
        print(f"東京ドームイベント情報の更新が完了しました。保存先: {final_file}")

    except Exception:
        print("エラー: 東京ドーム情報の取得中に問題が発生しました。")
        traceback.print_exc()

if __name__ == "__main__":
    fetch_event_data()