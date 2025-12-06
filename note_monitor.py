# force refresh
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os

URLS = [
    "https://note.com/reyu4/n/n1bc6f281ac9f",
    # 他もここに追加
]

SHEET_KEY = "1ScTYN7whfVMqkLwfZiZPGwkRVg3iFRNV-ERJDpsk-po"
LINE_TOKEN = os.getenv("LINE_TOKEN")  # GitHub Secretsから取得

def check_bought_status(url):
    """
    Noteの記事に「購入済み」表示があるか判定（Selenium不要）
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 「購入済み」表示を含むか判定
    return ("購入済" in soup.text) or ("購入しました" in soup.text) or ("買われました" in soup.text)

def write_to_sheet(gc, url):
    sh = gc.open_by_key(SHEET_KEY)
    ws = sh.sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([now, url, "買われました"])

def send_line_notify(message):
    if not LINE_TOKEN:
        print("❌ LINE_TOKEN が設定されていません（LINE通知スキップ）")
        return
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

def main():
    # Google認証（ファイルはGitHub Secretsから生成）
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service-account.json", scope)
    gc = gspread.authorize(creds)

    for url in URLS:
        if check_bought_status(url):
            write_to_sheet(gc, url)
            send_line_notify(f"✅ Note購入発生: {url}")
        else:
            print(f"チェック完了: {url} → 買われませんでした")

if __name__ == "__main__":
    main()
