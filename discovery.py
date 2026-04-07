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
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

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
    found_today = {}

    print(f"--- STARTING SURGICAL WHALE HUNT ---")

    for url in urls:
        print(f"\nScanning: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            percents = [int(p) for p in re.findall(r'(\d+)%\s*Cash Back', res.text)]
            dollars = [int(d) for d in re.findall(r'\$(\d+)\s*Cash Back', res.text)]

            # Get Store Name
            name_match = re.search(r'<title>(.*?) (?:Coupons|Promo|Cash Back)', res.text)
            raw_name = name_match.group(1) if name_match else url.split('/')[-1].capitalize()
            clean_name = raw_name.replace("Banking", "").strip()

            # Track highest unique rates per page
            if percents:
                max_p = max(percents)
                if clean_name not in found_today or max_p > found_today[clean_name]['val']:
                    found_today[clean_name] = {'val': max_p, 'type': '%'}

            if dollars:
                max_d = max(dollars)
                d_key = f"{clean_name} (Bonus)"
                if d_key not in found_today or max_d > found_today[d_key]['val']:
                    found_today[d_key] = {'val': max_d, 'type': '$'}

        except Exception as e:
            print(f"  ! Error: {e}")

    # Process findings against history
    for name, data in found_today.items():
        val = data['val']
        is_dollar = data['type'] == '$'
        meets_threshold = (not is_dollar and val >= PERCENT_TARGET) or (is_dollar and val >= DOLLAR_TARGET)
        
        if meets_threshold:
            prev_best = history.get(name, 0)
            if val > prev_best:
                display = f"${val}" if is_dollar else f"{val}%"
                prev_display = f"${prev_best}" if is_dollar else f"{prev_best}%"
                
                msg = f"🚀 *NEW WHALE RECORD:* {name} jumped from {prev_display} to *{display}*!"
                print(f"!!! TELEGRAM SENT: {name} @ {display}")
                send_alert(msg)
                history[name] = val
            else:
                print(f"  > {name} is at {val}, but we have a record of {prev_best}. Skipping.")

    save_history(history)
    print("\n--- HUNT COMPLETE ---")

if __name__ == "__main__":
    discover_whales()
