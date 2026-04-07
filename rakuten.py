import requests
import re
import os

# --- CONFIG ---
DISCOVERY_TARGET = 10  # Dropped to 10% just to TEST if it works. Change back to 15 or 80 later.
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
        print(f"DEBUG (No Telegram): {msg}")

def discover_deals():
    # We are checking the main homepage now - it always has the big deals
    url = "https://www.rakuten.com/"
    print(f"Scanning {url}...")
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        
        # This new Regex is a "Power Hunter". 
        # It looks for ANY number followed by '% Cash Back'
        # It also grabs about 30 characters BEFORE the number (which is usually the store name)
        found_anything = False
        potential_deals = re.findall(r'(.{1,30}?)(\d+)%\s*Cash Back', res.text)
        
        print(f"Found {len(potential_deals)} total stores on the page.")

        for raw_name, rate_str in potential_deals:
            rate = int(rate_str)
            # Clean up the store name (remove HTML junk)
            clean_name = re.sub('<[^<]+?>', '', raw_name).strip().split('\n')[-1]
            
            if rate >= DISCOVERY_TARGET:
                found_anything = True
                msg = f"🔥 *DISCOVERY:* {clean_name} is at *{rate}%*!"
                print(f"MATCH: {msg}")
                send_alert(msg)
        
        if not found_anything:
            print("No stores met the target percentage.")

    except Exception as e:
        print(f"Discovery Error: {e}")

if __name__ == "__main__":
    discover_deals()
