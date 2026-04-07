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

            # 1. WHALE PERCENTAGE ALERTS
            for p in all_percents:
                if int(p) >= PERCENT_TARGET:
                    name_match = re.search(r'<title>(.*?) (?:Coupons|Promo)', res.text)
                    name = name_match.group(1) if name_match else url.split('/')[-1].capitalize()
                    alert_key = f"{name}_{p}%" # Unique key to prevent spam
                    if alert_key not in seen_deals:
                        send_alert(f"🚨 *WHALE ALERT:* {name} is at *{p}%*!")
                        print(f"!!! TELEGRAM SENT: {name} @ {p}%")
                        seen_deals.add(alert_key)

            # 2. WHALE DOLLAR ALERTS
            for d in all_dollars:
                if int(d) >= DOLLAR_TARGET:
                    # Specific naming for SoFi or generic high-dollar deals
                    is_sofi = "sofi" in url.lower() or "sofi" in res.text.lower()
                    label = f"SoFi/Bank Bonus (${d})" if is_sofi else f"High-Dollar Deal (${d})"
                    
                    if label not in seen_deals:
                        send_alert(f"💰 *WHALE ALERT:* {label} detected!")
                        print(f"!!! TELEGRAM SENT: {label}")
                        seen_deals.add(label)

        except Exception as e:
            print(f"  ! Error scanning {url}: {e}")

    print("\n--- HUNT COMPLETE ---")

if __name__ == "__main__":
    discover_whales()
