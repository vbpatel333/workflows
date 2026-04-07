import requests
import re
import os

# --- CONFIG ---
# 12-15% is the "Gold Medal" tier for 2026. 
# Anything higher is likely a Wednesday "Big Deal Reveal" event.
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
    # This URL is a massive list of every store and its current rate.
    url = "https://www.rakuten.com/stores/all"
    print(f"Scanning for deals >= {DISCOVERY_TARGET}% at {url}...")
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        
        # This Regex captures the store name and percentage from the directory list.
        # It looks for "Store Name" followed by "X% Cash Back".
        pattern = r'([A-Z][A-Za-z0-9\s&\'\.\-]+?)\s+(\d+)%\s*Cash Back'
        matches = re.findall(pattern, res.text)
        
        found_count = 0
        seen_stores = set()

        for name, rate_str in matches:
            rate = int(rate_str)
            name = name.strip()
            
            # Filter out junk text and generic site labels
            if rate >= DISCOVERY_TARGET and "Cash Back" not in name and len(name) > 2:
                if name not in seen_stores:
                    msg = f"🔥 *HIGH CASH BACK:* {name} is at *{rate}%*!"
                    print(msg)
                    send_alert(msg)
                    seen_stores.add(name)
                    found_count += 1
        
        if found_count == 0:
            print(f"No high-value deals found above {DISCOVERY_TARGET}%.")
        else:
            print(f"Successfully sent {found_count} deals to Telegram.")

    except Exception as e:
        print(f"Discovery Error: {e}")

if __name__ == "__main__":
    discover_deals()
