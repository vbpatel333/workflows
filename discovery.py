import requests
import re
import os
import json

# --- CONFIG ---
PERCENT_TARGET = 80 
DOLLAR_TARGET = 40 
HISTORY_FILE = "whale_history.json"

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def send_alert(msg):
    if TELE_TOKEN and TELE_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": TELE_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def discover_whales():
    urls = [
        "https://www.rakuten.com/shop/surfshark",
        "https://www.rakuten.com/shop/sofibanking",
        "https://www.rakuten.com/f/big-give-week",
        "https://www.rakuten.com/dtc-stores"
    ]
    
    history = load_history()
    found_today = {} # Format: {"StoreName": {"rate": 100, "is_dollar": False}}

    print(f"--- STARTING SURGICAL WHALE HUNT ---")

    for url in urls:
        print(f"\nScanning: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            
            # 1. Scrape all percentages and dollars
            percents = re.findall(r'(\d+)%\s*Cash Back', res.text)
            dollars = re.findall(r'\$(\d+)\s*Cash Back', res.text)

            # Determine Store Name
            name_match = re.search(r'<title>(.*?) (?:Coupons|Promo)', res.text)
            store_name = name_match.group(1) if name_match else url.split('/')[-1].replace('sofibanking', 'SoFi').capitalize()

            # 2. Update found_today with ONLY the highest values
            if percents:
                max_p = max(int(p) for p in percents)
                if store_name not in found_today or max_p > found_today[store_name].get('rate', 0):
                    found_today[store_name] = {'rate': max_p, 'is_dollar': False}

            if dollars:
                max_d = max(int(d) for d in dollars)
                # Group banking/dollars under a specific key if needed
                d_key = f"{store_name} (Bonus)"
                if d_key not in found_today or max_d > found_today[d_key].get('rate', 0):
                    found_today[d_key] = {'rate': max_d, 'is_dollar': True}

        except Exception as e:
            print(f"  ! Error: {e}")

    # 3. COMPARE AGAINST HISTORY & ALERT
    for name, data in found_today.items():
        rate = data['rate']
        is_dollar = data['is_dollar']
        
        # Check if it meets the Whale Threshold
        meets_threshold = (not is_dollar and rate >= PERCENT_TARGET) or (is_dollar and rate >= DOLLAR_TARGET)
        
        if meets_threshold:
            prev_best = history.get(name, 0)
            
            # ONLY alert if current is strictly HIGHER than history
            if rate > prev_best:
                symbol = "$" if is_dollar else ""
                suffix = "" if is_dollar else "%"
                msg = f"🚀 *NEW WHALE RECORD:* {name} jumped from {symbol}{prev_best}{suffix} to *{symbol}{rate}{suffix}*!"
                
                print(f"!!! TELEGRAM SENT: {name} @ {symbol}{rate}{suffix}")
                send_alert(msg)
                history[name] = rate # Update history with new record
            else:
                print(f"  > {name} is at {rate}, but we've seen {prev_best} before. Skipping alert.")

    save_history(history)
    print("\n--- HUNT COMPLETE ---")

if __name__ == "__main__":
    discover_whales()if __name__ == "__main__":
    discover_whales()
