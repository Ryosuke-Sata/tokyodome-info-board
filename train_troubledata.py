import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

def main():
    # --- 1. データを保存するための空のリストを準備 ---
    all_train_data = []

    # ブラウザを起動
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options = options) 

    # Yahoo!路線情報の関東エリアのページを開く
    driver.get("https://transit.yahoo.co.jp/diainfo/area/4")

    print("ページを開きました。運行情報の読み込みを待機します...")

    try:
        # 最大10秒間、指定した要素が表示されるまで待機する設定
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.elmTblLstLine.trouble tr")))
        
        print("運行情報テーブルが見つかりました。データを取得します。")

        # ヘッダー行を除いた、全てのデータ行（tr）を取得
        elements = driver.find_elements(By.CSS_SELECTOR, "div.elmTblLstLine.trouble tr")[1:]
        
        if elements:
            print(f"--- 関東エリアの運行情報 ({len(elements)}件) ---")
            for row in elements:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 3:
                    line_name = cells[0].text
                    status = cells[1].text
                    detail = cells[2].text
                    
                    print(f"路線: {line_name}, 状況: {status}")

                    # --- 2. 取得したデータを辞書としてリストに追加 ---
                    train_info = {
                        "路線": line_name,
                        "状況": status,
                        "詳細": detail
                    }
                    all_train_data.append(train_info)
        else:
            print("運行情報テーブルはありますが、具体的な遅延情報はありませんでした。")

    except TimeoutException:
        print("運行情報のテーブルが見つかりませんでした。全路線が平常運転の可能性があります。")

    finally:
        # ブラウザを閉じる
        print("ブラウザを閉じます。")
        driver.quit()

    # --- 3. リストにデータがあれば、JSONファイルに保存 ---
    if all_train_data:
        # ファイル名を設定
        file_path = "train_data.json"
        print(f"取得したデータを {file_path} に保存します...")

        # with openでファイルを開き、json.dumpで書き込む
        with open(file_path, 'w', encoding='utf-8') as f:
            # ensure_ascii=False で日本語が文字化けしないようにする
            # indent=4 で見やすいようにインデントを付ける
            json.dump(all_train_data, f, ensure_ascii=False, indent=4)
        
        print("データの保存が完了しました。")
    else:
        file_path = "train_data.json"
        all_train_data = []
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_train_data, f, ensure_ascii=False, indent=4)
        print("保存するデータがなかったため、空ファイルを保存します")
    return

if __name__ == "__main__":
    main()