import requests
import re
import os
import time

# --- CONFIGURATION ---
# 1. Your specific target stores
PRIORITY_STORES = {
    "Pair of Thieves": "pairofthieves"
}
PRIORITY_TARGET = 5 # Alert if > 5%

# 2. General Discovery
DISCOVERY_TARGET = 15  # Alert for ANY store > 15% (80% is extremely rare on Rakuten, usually 10-15% is the "Big Sale" tier)

# Telegram Setup
TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    else:
        print(f"TELEGRAM LOG: {msg}")

def check_priority_stores():
    """Checks your specific must-have stores."""
    for name, slug in PRIORITY_STORES.items():
        url = f"https://www.rakuten.com/shop/{slug}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            match = re.search(r'(\d+)% Cash Back', res.text)
            if match:
                rate = int(match.group(1))
                if rate > PRIORITY_TARGET:
                    send_alert(f"💎 *PRIORITY ALERT:* {name} is at *{rate}%*!\n[Shop Now]({url})")
        except Exception as e:
            print(f"Error checking {name}: {e}")

def discover_hot_deals():
    """Scans the 'Hot Deals' page for anything massive."""
    url = "https://www.rakuten.com/f/promotion" # This page lists current boosted rates
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # Find all patterns like "StoreName. 15% Cash Back"
        # This regex looks for names followed by a percentage
        deals = re.findall(r'([A-Za-z0-9\s&]+)\.\s(\d+)% Cash Back', res.text)
        
        for store_name, rate_str in deals:
            rate = int(rate_str)
            if rate >= DISCOVERY_TARGET:
                send_alert(f"🔥 *HOT DEAL FOUND:* {store_name.strip()} is at *{rate}%*!")
    except Exception as e:
        print(f"Discovery Error: {e}")

if __name__ == "__main__":
    print("Starting Priority Check...")
    check_priority_stores()
    
    print("Starting Discovery Scan...")
    discover_hot_deals()
