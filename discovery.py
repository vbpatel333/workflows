import requests
import re
import os

# --- CONFIG ---
# We are hunting for 80% and up (The "Whales")
PERCENT_TARGET = 80 
# For flat-rate deals like SoFi or Internet, we want $40+ 
DOLLAR_TARGET = 40 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        # Using GET for better reliability on Mac/Windows local runs
        requests.get(url, params={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_whales():
    # These pages are currently hosting the April 2026 Triple Cash deals
    urls = [
        "https://www.rakuten.com/shop/surfshark", # Direct check for the 100% king
        "https://www.rakuten.com/shop/sofibanking", # Direct check for SoFi
        "https://www.rakuten.com/f/big-give-week",
        "https://www.rakuten.com/dtc-stores"
    ]
    
    seen_deals = set()

    for url in urls:
        print(f"Scanning {url}...")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            
            # 1. Catching "100% Cash Back" or "95% was 20%"
            # This regex looks for the number first, then the store name nearby
            percents = re.findall(r'(\d+)%\s*(?:was\s*\d+%)?\s*Cash Back', res.text)
            
            # 2. Catching the $125 or $400 SoFi style bonuses
            dollars = re.findall(r'\$(\d+)\s*Cash Back', res.text)

            # Check if any of the caught numbers hit our 'Whale' target
            if any(int(p) >= PERCENT_TARGET for p in percents):
                # If we find a 100% on the page, we grab the store name from the Title
                store_title = re.search(r'<title>(.*?) Coupons', res.text)
                name = store_title.group(1) if store_title else "A Mystery Whale"
                
                if name not in seen_deals:
                    msg = f"🚨 *100% ALERT:* {name} is at *MAX CASH BACK* right now!"
                    send_alert(msg)
                    seen_deals.add(name)

            if any(int(d) >= DOLLAR_TARGET for d in dollars):
                # Specific check for SoFi/Banking bonuses
                if "SoFi" in res.text and "SoFi" not in seen_deals:
                    msg = f"💰 *SOFI ALERT:* Big dollar bonus detected (Up to $400)!"
                    send_alert(msg)
                    seen_deals.add("SoFi")

        except Exception as e:
            print(f"Search Error: {e}")

if __name__ == "__main__":
    discover_whales()
