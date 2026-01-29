from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

# --- HUBDRIVE SOLVER LOGIC ---
def extract_hubcloud(url):
    try:
        # Hum Browser nahi, Requests use karenge (Fast & Server Friendly)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        # Regex se 'hubcloud.foo' dhoondenge
        pattern = r'href="(https?://hubcloud\.foo/drive/[^"]+)"'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
        return None
    except Exception as e:
        return None

# --- HOME PAGE (Taaki pata chale website chal rahi hai) ---
@app.route('/')
def home():
    return "HubDrive Solver API is Running! 🚀"

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
            "message": "Link nahi mila"
        })

if __name__ == '__main__':
    # Server port automatically uthayega
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
