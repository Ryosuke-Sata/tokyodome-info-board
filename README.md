# Tokyo Dome Info Board (東京ドーム情報掲示板)

東京ドームのイベントスケジュールと、首都圏の電車運行情報をリアルタイムで表示するアプリケーションです。
利用シーンに合わせて、**モダンなWebブラウザ版**と、**独立したデスクトップ版（GUI）**の2つのインターフェースから選んで利用できます。

## 📸 主な機能 (Features)

- **選べる2つのUI**: レスポンシブで非同期Ajax更新に対応した「Webアプリ版」と、`customtkinter` を用いた「デスクトップ版」を同梱。
- **イベント情報**: 東京ドームの「今日」と「明日」のイベントをバックグラウンドで自動取得。
- **電車運行情報**: 首都圏の主要路線の遅延情報をリアルタイムに取得。
- **シームレスな更新**: データの取得中もUIがフリーズすることなく、システム稼働時間を維持したまま最新情報を反映します。
- **堅牢なデータ保存**: データ保存時に一時ファイルを利用することで、処理が中断されてもファイルの破損を防ぎます。

## 🛠️ 動作環境 (Requirements)

- Windows 10/11 または macOS
- Python 3.10 以上
- Google Chrome (運行情報の取得にSeleniumを使用するため必須)

## 📦 導入方法 (Installation)

1. このリポジトリ（フォルダ）の全ファイルをダウンロードします。
2. コマンドプロンプトまたはターミナルを開き、フォルダのルートディレクトリで以下を実行してライブラリをインストールします。
   ```sh
   pip install -r requirements.txt
   ```
   *(※ Webアプリ版の起動スクリプトを使用する場合は、この手順は自動で行われます)*

## 🚀 実行方法 (Execution)

### パターンA: Webアプリ版として使う場合（おすすめ）
ブラウザ上で動作し、スマートフォンや他のPCからローカルネットワーク経由でアクセスすることも可能です。

- **Windows**: `start_app.bat` をダブルクリックします。（初回は自動で環境構築が行われます）
- **macOS**: `start_app.command` をダブルクリックします。（初回のみターミナルで `chmod +x start_app.command` の実行が必要です）

### パターンB: デスクトップ版(GUI)として使う場合
専用のウィンドウが立ち上がるスタンドアロンアプリとして動作します。

- ターミナルまたはコマンドプロンプトで以下を実行します：
  ```sh
  python desktop_app/desktop_app.py
  ```

## 📂 ファイル構成 (File Structure)

```text
.
├── web_app/                  # Webアプリ版のインターフェース
│   ├── app.py                # Flask WebサーバーとAPI
│   └── templates, static/    # HTMLとCSS
├── desktop_app/              # デスクトップ版のインターフェース
│   └── desktop_app.py        # GUIメインスクリプト (customtkinter)
├── core/                     # 共通のバックグラウンド処理モジュール
│   ├── tokyodome_eventdata.py # イベント情報取得スクリプト
│   └── train_troubledata.py   # 電車運行情報取得スクリプト (Selenium)
├── start_app.bat             # Web版 ワンクリック起動スクリプト (Windows)
├── start_app.command         # Web版 ワンクリック起動スクリプト (macOS)
├── requirements.txt          # 依存ライブラリ一覧
└── data/                     # (自動生成) 取得したデータを保存するディレクトリ
    ├── event_data.json       
    └── train_data.json       
```

## 🖥️ 実行ファイル(EXE)の作成 (Windows / デスクトップ版)

`PyInstaller`を使用して、Python環境がないPCでも動作する単一の実行ファイル（EXE）に変換することが可能です。

```sh
pyinstaller --noconsole --onefile --collect-all customtkinter --collect-all tzdata --name "TokyoDomeInfoBoard" desktop_app/desktop_app.py
```
コマンド実行後、`dist`フォルダ内に `TokyoDomeInfoBoard.exe` が生成されます。

## ⚠️ 注意事項 (Notes)

- 本アプリケーションはWebスクレイピング技術を使用しています。情報取得サイト（東京ドーム公式サイト、Yahoo!路線情報）のウェブサイト構造が変更されると、正しくデータを取得できなくなる可能性があります。
- サーバーに負荷をかけないよう、更新は常識的な頻度（イベント:1時間毎、電車:10分毎）で行っています。手動更新の過度な連打はお控えください。

## Author
佐多良介