from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

# --- HUBDRIVE SOLVER LOGIC ---
def extract_hubcloud(url):
    try:
        # Browser ki identity
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        # Regex se 'hubcloud' dhoondenge (Flexible pattern)
        pattern = r'href=["\'](https?://hubcloud\.(?:foo|club|bar)/drive/[^"\']+)["\']'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# --- HOME PAGE ---
@app.route('/')
def home():
    return "HubDrive Solver API is Running! 🚀 Use /solve?url=..."

# --- API ENDPOINT ---
@app.route('/solve', methods=['GET'])
def solve():
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({"status": "error", "message": "URL missing"}), 400

    extracted = extract_hubcloud(target_url)

    if extracted:
        return jsonify({
            "status": "success",
            "original_url": target_url,
            "hubcloud_link": extracted
        })
    else:
        return jsonify({
            "status": "fail",
            "message": "Link nahi mila (Shayad Cloudflare hai ya Pattern match nahi hua)"
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
