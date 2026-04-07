import requests
import re
import os

# --- CONFIG ---
# I suggest setting this to 12 or 15. 
# 80 is virtually impossible on Rakuten, but 15 is a "Gold Medal" deal.
DISCOVERY_TARGET = 12 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_deals():
    # The 'Promotion' page is the best source for "Extra Cash Back" lists
    url = "https://www.rakuten.com/f/promotion"
    print(f"Scanning for deals >= {DISCOVERY_TARGET}% at {url}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # This Regex finds the "Shop [StoreName]" button text and the "% Cash Back" nearby
        # It's specifically tuned for the 2026 layout
        pattern = r'Shop\.\s+([^.]+?)\.\s+(\d+(?:\.\d+)?)%\s+Cash Back'
        matches = re.findall(pattern, response.text)
        
        found_count = 0
        seen_stores = set()

        for name, rate_str in matches:
            rate = float(rate_str)
            name = name.strip()
            
            if rate >= DISCOVERY_TARGET and name not in seen_stores:
                msg = f"🔥 *RAKUTEN DISCOVERY:* {name} is at *{rate}%*!"
                print(msg)
                send_alert(msg)
                seen_stores.add(name)
                found_count += 1
        
        if found_count == 0:
            print("No high-value deals found with current filters.")
        else:
            print(f"Successfully found and sent {found_count} deals.")

    except Exception as e:
        print(f"Discovery Error: {e}")

if __name__ == "__main__":
    discover_deals()
