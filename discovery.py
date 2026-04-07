import requests
import re
import os

# --- CONFIG ---
PERCENT_TARGET = 80 
DOLLAR_TARGET = 40 

TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

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
    
    seen_deals = set()
    print(f"--- STARTING WHALE HUNT (Targets: {PERCENT_TARGET}% or ${DOLLAR_TARGET}) ---")

    for url in urls:
        print(f"\nScanning: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=15)
            
            # Find UNIQUE percentages and bonuses to clean up the log
            all_percents = sorted(list(set(re.findall(r'(\d+)%\s*Cash Back', res.text))), key=int, reverse=True)
            all_dollars = sorted(list(set(re.findall(r'\$(\d+)\s*Cash Back', res.text))), key=int, reverse=True)

            if all_percents:
                print(f"  > Unique Rates: {', '.join([p+'%' for p in all_percents])}")
            if all_dollars:
                print(f"  > Unique Bonuses: {', '.join(['$'+d for d in all_dollars])}")

            # WHALE ALERTS
            for p in all_percents:
                if int(p) >= PERCENT_TARGET:
                    # Grab store name from title
                    name_match = re.search(r'<title>(.*?) (?:Coupons|Promo)', res.text)
                    name = name_match.group(1) if name_match else url.split('/')[-1].capitalize()
                    if name not in seen_deals:
                        send_alert(f"🚨 *WHALE ALERT:* {name} is at *{p}%*!")
                        print(f"!!! TELEGRAM SENT: {name} @ {p}%")
                        seen_deals.add(name)

for d in all_dollars:
                if int(d) >= DOLLAR_TARGET:
                    # Capture the specific amount in the identifier
                    identifier = f"SoFi/Bank Bonus (${d})" if "sofi" in url or "banking" in res.text.lower() else f"High-Dollar Deal (${d})"
                    if identifier not in seen_deals:
                        send_alert(f"💰 *WHALE ALERT:* {identifier} detected!")
                        print(f"!!! TELEGRAM SENT: {identifier}")
                        seen_deals.add(identifier)

        except Exception as e:
            print(f"  ! Error scanning {url}: {e}")

    print("\n--- HUNT COMPLETE ---")

if __name__ == "__main__":
    discover_whales()
