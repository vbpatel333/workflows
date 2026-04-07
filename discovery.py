import requests
import re
import os

# --- CONFIG ---
# 12-15% is usually the 'Triple Cash Back' peak. 
# 80% is extremely rare for cash back, but you can set this to whatever you want.
DISCOVERY_TARGET = 12 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_deals():
    # The 'DTC Stores' page is cleaner than the homepage for scraping
    url = "https://www.rakuten.com/dtc-stores"
    print(f"Scanning for high-value deals at {url}...")
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        
        # This Regex looks for "StoreName. XX.X%" pattern found in Rakuten's 2026 code
        # It captures the Store Name and the Percentage separately
        pattern = r'([A-Z][A-Za-z0-9\s&\'\.]+)\.\s+(\d+(?:\.\d+)?)%'
        matches = re.findall(pattern, res.text)
        
        found_stores = set() # To prevent duplicate alerts for the same store
        
        for name, rate_str in matches:
            rate = float(rate_str)
            name = name.strip()
            
            # Filter out junk names (like 'Sign Up' or 'Join Now')
            if rate >= DISCOVERY_TARGET and len(name) > 2 and "Cash Back" not in name:
                if name not in found_stores:
                    msg = f"🔥 *HIGH CASH BACK:* {name} is at *{rate}%*!"
                    print(msg)
                    send_alert(msg)
                    found_stores.add(name)
        
        print(f"Scan complete. Found {len(found_stores)} deals above {DISCOVERY_TARGET}%.")

    except Exception as e:
        print(f"Discovery Error: {e}")

if __name__ == "__main__":
    discover_deals()
