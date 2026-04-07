import requests
import re
import os

# --- CONFIG ---
# Setting this to 10% for a "Win" today. 
# You can bump it to 15% later for true "Gold Medal" deals.
DISCOVERY_TARGET = 10 

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
    # Targeting the 2026 'Hot Deals' and 'All Stores' paths
    urls = [
        "https://www.rakuten.com/dtc-stores",
        "https://www.rakuten.com/f/seasonalhotdeals"
    ]
    
    seen_stores = set()

    for url in urls:
        print(f"Scanning {url}...")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            # This regex looks for: Store Name + . + Percentage
            # Matches the 2026 pattern: "Groupon. 17% Cash Back"
            matches = re.findall(r'([A-Z][A-Za-z0-9\s&\'\.]+?)\.\s+(\d+(?:\.\d+)?)%', res.text)

            for name, rate_str in matches:
                rate = float(rate_str)
                name = name.strip()
                
                if rate >= DISCOVERY_TARGET and name not in seen_stores:
                    # Filter out site navigation text
                    if len(name) > 2 and "Cash Back" not in name and "Sign In" not in name:
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
