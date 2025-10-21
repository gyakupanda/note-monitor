from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import requests
import os

URLS = [
    "https://note.com/reyu4/n/n1bc6f281ac9f",
    # ...（他のURLも同様）
]

SHEET_KEY = "1ScTYN7whfVMqkLwfZiZPGwkRVg3iFRNV-ERJDpsk-po"
SERVICE_ACCOUNT_FILE = "/Users/shotasano/Downloads/service-account.json"
LINE_TOKEN = "★LINEトークン★"

def check_bought_status(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 画面を表示しない
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)
    time.sleep(5)  # JavaScriptが動くまで待機（秒）

    html = driver.page_source
    driver.quit()
    return "買われています" in html or "購入されました" in html

def write_to_sheet(gc, url):
    sh = gc.open_by_key(SHEET_KEY)
    ws = sh.sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([now, url, "買われました"])

def send_line_notify(message):
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

def main():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    gc = gspread.authorize(creds)

    for url in URLS:
        if check_bought_status(url):
            write_to_sheet(gc, url)
            send_line_notify(f"✅ Note購入発生: {url}")
        else:
            print(f"チェック完了: {url} → 買われませんでした")

if __name__ == "__main__":
    main()
