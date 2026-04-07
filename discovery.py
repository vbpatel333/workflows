import requests
import re
import os

# --- CONFIG ---
DISCOVERY_TARGET = 12 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        # We use 'requests.get' for simpler Telegram delivery in this version
        requests.get(url, params={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_deals():
    # We check the main page and the 'DTC' page where 2026 deals are most visible
    urls = ["https://www.rakuten.com/", "https://www.rakuten.com/dtc-stores"]
    found_stores = {}

    for url in urls:
        print(f"Scanning {url}...")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            
            # This Regex looks for "StoreName" followed by "XX% Cash Back"
            # It handles the 2026 'Triple Cash Back' formatting
            matches = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.?\s+(\d+(?:\.\d+)?)%\s*Cash Back', res.text)

            for name, rate_str in matches:
                rate = float(rate_str)
                name = name.strip()
                
                if rate >= DISCOVERY_TARGET and len(name) > 2:
                    # Avoid duplicates and junk site text
                    if name not in found_stores and "Sign In" not in name:
                        found_stores[name] = rate
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
