import requests
import re
import os
import time

# --- CONFIG ---
# 12% is a great threshold for the April Flash Sale.
DISCOVERY_TARGET = 12 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Advanced Headers to bypass bot detection
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_deals():
    # We are checking the "Flash Sale" and "All Stores" pages which are most active today
    urls = [
        "https://www.rakuten.com/triple-cash-back",
        "https://www.rakuten.com/stores/all"
    ]
    
    found_stores = {}

    for url in urls:
        print(f"Checking {url}...")
        try:
            # Adding a tiny delay so we don't look like a rapid-fire bot
            time.sleep(2)
            res = requests.get(url, headers=headers, timeout=20)
            
            # This regex is a 'Universal Hunter' for 2026. 
            # It finds a Name, then a dot/space, then a Number%
            matches = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.?\s+(\d+(?:\.\d+)?)%\s*Cash Back', res.text)

            for name, rate_str in matches:
                rate = float(rate_str)
                name = name.strip()
                
                # Cleanup: Remove 'Up to', 'was', and site navigation junk
                clean_name = re.sub(r'^(Up to|was|Get|Shop|plus|Only)\s+', '', name, flags=re.IGNORECASE).strip()
                
                if rate >= DISCOVERY_TARGET and len(clean_name) > 2:
                    if clean_name not in found_stores and "Sign In" not in clean_name:
                        found_stores[clean_name] = rate
                        
        except Exception as e:
            print(f"Error at {url}: {e}")

    if found_stores:
        for name, rate in found_stores.items():
            msg = f"🔥 *RAKUTEN DISCOVERY:* {name} is at *{rate}%*!"
            print(msg)
            send_alert(msg)
    else:
        print(f"No high-value deals found above {DISCOVERY_TARGET}%.")

if __name__ == "__main__":
    discover_deals()
