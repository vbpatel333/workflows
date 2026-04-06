import requests
import re
import os

# Your Discord URL (We will set this in GitHub Settings, not the code!)
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_discord_message(msg):
    if DISCORD_WEBHOOK:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    else:
        print("No Webhook found. Message would have been: " + msg)

def check_cashback():
    url = "https://www.rakuten.com/shop/pairofthieves"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        match = re.search(r'(\d+)% Cash Back', response.text)
        
        if match:
            number = int(match.group(1))
            if number > 5:
                send_discord_message(f"🚨 ALERT: Pair of Thieves is at **{number}%** Cash Back! Go! https://www.rakuten.com/shop/pairofthieves")
            else:
                print(f"Current rate is {number}%. No alert needed.")
        else:
            print("Could not find rate. Rakuten might be blocking GitHub.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cashback()
