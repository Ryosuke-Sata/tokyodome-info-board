import json
import os
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

def main():
    print("--- 電車運行情報の取得を開始します ---")
    all_train_data = []
    driver = None

    try:
        # ブラウザを起動
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu") # エラー回避用
        options.add_argument("--no-sandbox")
        
        # ログ出力を抑制
        options.add_argument("--log-level=3")
        
        driver = webdriver.Chrome(options=options) 

        # Yahoo!路線情報の関東エリアのページを開く
        driver.get("https://transit.yahoo.co.jp/diainfo/area/4")
        
        # 待機時間を設定
        wait = WebDriverWait(driver, 10)
        
        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.elmTblLstLine.trouble tr")))
            print("運行情報テーブルが見つかりました。データを取得します。")

            elements = driver.find_elements(By.CSS_SELECTOR, "div.elmTblLstLine.trouble tr")[1:]
            
            if elements:
                for row in elements:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) == 3:
                        line_name = cells[0].text
                        status = cells[1].text
                        detail = cells[2].text
                        
                        train_info = {
                            "路線": line_name,
                            "状況": status,
                            "詳細": detail
                        }
                        all_train_data.append(train_info)
        except TimeoutException:
            print("運行情報のテーブルが見つかりませんでした（平常運転の可能性）。")

    except Exception:
        print("エラー: 運行情報の取得中に予期せぬエラーが発生しました。")
        traceback.print_exc()

    finally:
        # ブラウザを確実に閉じる
        if driver:
            try:
                driver.quit()
                print("ブラウザを終了しました。")
            except Exception:
                pass

    # --- Atomic Write (安全な書き込み) ---
    try:
        temp_file = "train_data.json.tmp"
        final_file = "train_data.json"

        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(all_train_data, f, ensure_ascii=False, indent=4)
        
        os.replace(temp_file, final_file)
        print("電車運行情報の保存が完了しました。")
        
    except Exception:
        print("エラー: ファイルの保存に失敗しました。")
        traceback.print_exc()

if __name__ == "__main__":
    main()