import requests
import re
import os

# --- CONFIG ---
# Set to 12% to catch the "Moroccanoil" and "Blue Apron" deals today.
DISCOVERY_TARGET = 12 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_deals():
    # Today, the best data is on the main 'Promotion' and 'Triple Cash' pages
    urls = ["https://www.rakuten.com/f/promotion", "https://www.rakuten.com/triple-cash-back"]
    print(f"Scanning for April 7th deals >= {DISCOVERY_TARGET}%...")
    
    seen_stores = set()

    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            # Looks for: Name. Number%
            matches = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.\s+(\d+(?:\.\d+)?)%', res.text)

            for name, rate_str in matches:
                rate = float(rate_str)
                raw_name = name.strip()
                
                # SURGICAL CLEANUP: Strips the junk from today's Blue Apron and Magazine deals
                clean_name = re.sub(r'^(Up to|was|Get|Shop|plus|a great deal from)\s+', '', raw_name, flags=re.IGNORECASE).strip()
                
                if rate >= DISCOVERY_TARGET and len(clean_name) > 2:
                    if clean_name not in seen_stores and "Cash Back" not in clean_name:
                        msg = f"🔥 *RAKUTEN DISCOVERY:* {clean_name} is at *{rate}%*!"
                        print(msg)
                        send_alert(msg)
                        seen_stores.add(clean_name)
        except Exception as e:
            print(f"Error scanning {url}: {e}")

if __name__ == "__main__":
    discover_deals()
