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
    # The 'Promotion' page is the most accurate source for the April 2026 Triple Cash event
    url = "https://www.rakuten.com/f/promotion"
    print(f"Scanning for deals >= {DISCOVERY_TARGET}%...")
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        
        # This Regex captures: Store Name + . + Percentage
        # It handles the 2026 'Big Deal' format: "AliExpress. 30% Cash Back"
        pattern = r'([A-Z][A-Za-z0-9\s&\'\-]+?)\.\s+(\d+(?:\.\d+)?)%'
        matches = re.findall(pattern, res.text)
        
        seen_stores = set()

        for name, rate_str in matches:
            rate = float(rate_str)
            raw_name = name.strip()
            
            # SURGICAL CLEANUP: Remove "Up to", "was", and leading junk
            clean_name = re.sub(r'^(Up to|was|Get|Shop)\s+', '', raw_name, flags=re.IGNORECASE).strip()
            
            if rate >= DISCOVERY_TARGET and len(clean_name) > 2:
                if clean_name not in seen_stores and "Cash Back" not in clean_name:
                    msg = f"🔥 *HIGH CASH BACK:* {clean_name} is at *{rate}%*!"
                    print(msg)
                    send_alert(msg)
                    seen_stores.add(clean_name)
                    
    except Exception as e:
        print(f"Discovery Error: {e}")

if __name__ == "__main__":
    discover_deals()
