import requests
import re
import os

# --- CONFIG ---
PERCENT_TARGET = 80 
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
    urls = [
        "https://www.rakuten.com/shop/surfshark",
        "https://www.rakuten.com/shop/sofibanking",
        "https://www.rakuten.com/f/big-give-week",
        "https://www.rakuten.com/dtc-stores"
    ]
    
    seen_deals = set()
    print(f"--- STARTING WHALE HUNT (Targets: {PERCENT_TARGET}% or ${DOLLAR_TARGET}) ---")

    for url in urls:
        print(f"Checking: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            
            # Find all percentages on the page for the log
            all_percents = re.findall(r'(\d+)%\s*Cash Back', res.text)
            # Find all dollar amounts for the log
            all_dollars = re.findall(r'\$(\d+)\s*Cash Back', res.text)

            # Log everything found to the console so you can see it in GitHub
            if all_percents:
                print(f"  > Found rates: {', '.join([p+'%' for p in all_percents])}")
            if all_dollars:
                print(f"  > Found bonuses: {', '.join(['$'+d for d in all_dollars])}")

            # WHALE LOGIC
            for p in all_percents:
                rate = int(p)
                if rate >= PERCENT_TARGET:
                    store_title = re.search(r'<title>(.*?) Coupons', res.text)
                    name = store_title.group(1) if store_title else "High Value Store"
                    if name not in seen_deals:
                        msg = f"🚨 *{rate}% ALERT:* {name} is at a WHALE rate!"
                        send_alert(msg)
                        print(f"!!! MATCH SENT TO TELEGRAM: {name} @ {rate}%")
                        seen_deals.add(name)

            for d in all_dollars:
                amt = int(d)
                if amt >= DOLLAR_TARGET:
                    if "SoFi" in res.text and "SoFi" not in seen_deals:
                        msg = f"💰 *SOFI ALERT:* ${amt} Bonus Found!"
                        send_alert(msg)
                        print(f"!!! MATCH SENT TO TELEGRAM: SoFi @ ${amt}")
                        seen_deals.add("SoFi")

        except Exception as e:
            print(f"  ! Error: {e}")

    print("--- HUNT COMPLETE ---")

if __name__ == "__main__":
    discover_whales()
