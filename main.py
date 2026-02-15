from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
def get_scraper():
    return cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )

def solve_hubdrive(url):
    print(f"\n⚡ Processing HubDrive: {url}")
    scraper = get_scraper()
    
    try:
        # 1. Page Load
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        }
        
        response = scraper.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return {"status": "error", "message": f"Page Load Failed: {response.status_code}"}

        # 2. HTML Parse (BeautifulSoup)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_link = None
        
        # LOGIC: Saare links check karo, jisme 'hubcloud' likha ho wo utha lo
        all_links = soup.find_all('a', href=True)
        
        print(f"🔍 Scanning {len(all_links)} links on HubDrive page...")
        
        for link in all_links:
            href = link['href']
            
            # Agar link me 'hubcloud' hai, to yahi hai wo!
            if "hubcloud" in href:
                print(f"✅ HubCloud Link Found: {href}")
                found_link = href
                break
        
        # Fallback: Agar BS4 se nahi mila, to Regex try karo
        if not found_link:
            print("⚠️ BS4 failed, trying Regex...")
            match = re.search(r'href=["\'](https?://[^"\']*hubcloud[^"\']+)["\']', response.text)
            if match:
                found_link = match.group(1)
                print(f"✅ Regex Found Link: {found_link}")

        # --- RESULT ---
        if found_link:
            return {
                "status": "success",
                "original_url": url,
                "hubcloud_link": found_link
            }
        else:
            print("❌ Link nahi mila")
            return {
                "status": "fail", 
                "message": "HubCloud link not found on this page."
            }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"status": "error", "message": str(e)}

# --- SERVER ---
@app.route('/', methods=['GET'])
def home():
    return "HubDrive Solver API is Live! 🚀"

@app.route('/solve', methods=['GET'])
def api_handler():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"})
    return jsonify(solve_hubdrive(url))

if __name__ == '__main__':
    # Render ke liye Port Environment Variable se uthana zaroori hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
