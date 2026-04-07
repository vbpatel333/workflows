import requests
import re
import os

# --- CONFIG ---
# I've set this to 12% so you can see the "Big Winners" today.
DISCOVERY_TARGET = 12 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_deals():
    # We're checking the Flash Sale and DTC pages specifically for April 2026
    urls = [
        "https://www.rakuten.com/april-flash-sale",
        "https://www.rakuten.com/dtc-stores"
    ]
    
    seen_stores = set()

    for url in urls:
        print(f"Scanning {url}...")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            # This regex captures: Store Name + . + Percentage
            # Matches the 2026 pattern: "AliExpress. 30% Cash Back"
            matches = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.\s+(\d+(?:\.\d+)?)%', res.text)

            for name, rate_str in matches:
                rate = float(rate_str)
                name = name.strip()
                
                if rate >= DISCOVERY_TARGET and name not in seen_stores:
                    # Clean up common junk text
                    if len(name) > 2 and "Cash Back" not in name:
                        msg = f"🔥 *RAKUTEN DISCOVERY:* {name} is at *{rate}%*!"
                        print(msg)
                        send_alert(msg)
                        seen_stores.add(name)
        except Exception as e:
            print(f"Error scanning {url}: {e}")

    if not seen_stores:
        print(f"No high-value deals found above {DISCOVERY_TARGET}%.")

if __name__ == "__main__":
    discover_deals()
