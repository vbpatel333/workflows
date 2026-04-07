import requests
import re
import os

# --- CONFIG ---
# We are hunting for 80% and up
PERCENT_TARGET = 80 
# Many 100% deals are flat dollar amounts (e.g. $40 back on a $40 plan)
DOLLAR_TARGET = 40 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_whales():
    # These three pages are where 100% 'Rebate' deals usually hide
    urls = [
        "https://www.rakuten.com/f/seasonalhotdeals",
        "https://www.rakuten.com/f/promotion",
        "https://www.rakuten.com/dtc-stores"
    ]
    
    seen_deals = set()

    for url in urls:
        print(f"Hunting for Whales at {url}...")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            
            # 1. Look for Percentage Deals (e.g., 'Surfshark 100% Cash Back')
            percents = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.\s+(\d+)%', res.text)
            
            # 2. Look for Dollar Deals (e.g., 'SoFi $100 Cash Back')
            dollars = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.\s+\$(\d+)', res.text)

            for name, rate_str in percents:
                rate = int(rate_str)
                name = name.strip()
                if rate >= PERCENT_TARGET and name not in seen_deals:
                    msg = f"🚨 *UNBELIEVABLE DEAL:* {name} is at *{rate}%* Cash Back!"
                    send_alert(msg)
                    seen_deals.add(name)

            for name, amt_str in dollars:
                amt = int(amt_str)
                name = name.strip()
                if amt >= DOLLAR_TARGET and name not in seen_deals:
                    msg = f"💰 *HUGE BONUS:* {name} is offering *${amt}* Cash Back!"
                    send_alert(msg)
                    seen_deals.add(name)

        except Exception as e:
            print(f"Search Error: {e}")

if __name__ == "__main__":
    discover_whales()
