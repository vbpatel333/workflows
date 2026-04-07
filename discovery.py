import requests
import re
import os

# --- CONFIG ---
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
    # April 2026 'Flash Sale' and 'DTC' pages are the most reliable right now
    urls = ["https://www.rakuten.com/triple-cash-back", "https://www.rakuten.com/dtc-stores"]
    print(f"Scanning for deals >= {DISCOVERY_TARGET}%...")
    
    seen_stores = set()

    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            # Matches the 2026 pattern: "Store Name. 30% Cash Back"
            matches = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.\s+(\d+(?:\.\d+)?)%', res.text)

            for name, rate_str in matches:
                rate = float(rate_str)
                raw_name = name.strip()
                
                # CLEANUP: This is the "magic" line that fixes the "Up to" issue
                clean_name = re.sub(r'^(Up to|was|Get|Shop|plus|great deal from)\s+', '', raw_name, flags=re.IGNORECASE).strip()
                
                if rate >= DISCOVERY_TARGET and len(clean_name) > 2:
                    if clean_name not in seen_stores and "Cash Back" not in clean_name:
                        msg = f"🔥 *RAKUTEN DISCOVERY:* {clean_name} is at *{rate}%*!"
                        print(msg)
                        send_alert(msg)
                        seen_stores.add(clean_name)
        except Exception as e:
            print(f"Error at {url}: {e}")

if __name__ == "__main__":
    discover_deals()
