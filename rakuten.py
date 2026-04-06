import requests
import re

# This makes us look like a real MacBook Pro user
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

def check_cashback():
    url = "https://www.rakuten.com/shop/pairofthieves"
    
    try:
        # 1. Get the page data
        response = requests.get(url, headers=headers, timeout=10)
        
        # 2. Check if we actually got in (Status 200 means OK)
        if response.status_code != 200:
            print(f"Rakuten blocked us (Error {response.status_code}). Try again in 5 minutes.")
            return

        # 3. Use "Regex" to hunt for the percentage pattern (e.g., "10% Cash Back")
        # This looks for a number followed by '% Cash Back' anywhere on the page
        match = re.search(r'(\d+)% Cash Back', response.text)
        
        if match:
            number = int(match.group(1))
            print(f"--- SUCCESS! ---")
            print(f"Current Rate: {number}%")
            
            if number > 5:
                print(">>> ALERT: IT IS GREATER THAN 5%! GO SHOP!")
            else:
                print(">>> Status: Not high enough yet. Go back to sleep.")
        else:
            print("Could not find a percentage on the page. Rakuten might be showing a 'Captcha' box.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_cashback()