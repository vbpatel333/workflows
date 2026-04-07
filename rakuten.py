import requests
import re
import os

# --- CONFIGURATION ---
STORES_TO_CHECK = {
    "Pair of Thieves": "pairofthieves",
    "Nike": "nike"
}
TARGET_PERCENT = 5
# Grab the Telegram info from GitHub Secrets
TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_msg(text):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        data = {"chat_id": TELE_CHAT_ID, "text": text, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    else:
        print(f"Telegram info missing. Message: {text}")

def check_stores():
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    for store, slug in STORES_TO_CHECK.items():
        url = f"https://www.rakuten.com/shop/{slug}"
        response = requests.get(url, headers=headers)
        match = re.search(r'(\d+)% Cash Back', response.text)
        
        if match:
            num = int(match.group(1))
            if num > TARGET_PERCENT:
                # This uses the Telegram function now!
                send_telegram_msg(f"🚨 *{store}* is at *{num}%*!\n[Shop Now]({url})")

if __name__ == "__main__":
    check_stores()
