from flask import Flask, request, jsonify
import requests
import re
import time
import os

app = Flask(__name__)

# --- HEADER SETTINGS (Fake Browser) ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://hubcloud.foo/'
}

# --- STEP 1: HubDrive -> HubCloud ---
def solve_hubdrive(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        pattern = r'href="(https?://hubcloud\.foo/drive/[^"]+)"'
        match = re.search(pattern, response.text)
        return match.group(1) if match else None
    except: return None

# --- STEP 2: HubCloud -> Generator Link ---
def get_hubcloud_generator(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        # 'var url' dhundo jo generator page ka link hota hai
        match = re.search(r"var\s+url\s*=\s*['\"]([^'\"]+hubcloud\.php[^'\"]+)['\"]", response.text)
        return match.group(1) if match else None
    except: return None

# --- STEP 3: Generator -> Final Link (FSL/Fukggl) ---
def get_final_link(generator_url):
    try:
        # Generator page ko call karo
        response = requests.get(generator_url, headers=HEADERS, timeout=10)
        html = response.text
        
        # Filters: Ye link humein chahiye
        keep = ["fsl-cdn-1.sbs", "fukggl.buzz"]
        
        # HTML mein chhupe saare links nikalo
        all_links = re.findall(r'https?://[^\s"\'<>]+', html)
        
        for link in all_links:
            # Agar link 'keep' list mein hai to return karo
            if any(k in link for k in keep):
                return link
        return None
    except: return None

# --- MAIN API ROUTE (Magic Button) ---
@app.route('/solve', methods=['GET'])
def solve_all():
    input_url = request.args.get('url')
    if not input_url: return jsonify({"status": "error", "message": "Link missing"}), 400

    # Logic: Pehle check karo ye HubDrive hai ya HubCloud
    hubcloud_link = None
    
    if "hubdrive.space" in input_url:
        hubcloud_link = solve_hubdrive(input_url)
    elif "hubcloud.foo" in input_url:
        hubcloud_link = input_url

    if not hubcloud_link:
        return jsonify({"status": "fail", "message": "HubCloud link nahi mila"})

    # Ab HubCloud se Final Link nikalte hain
    gen_link = get_hubcloud_generator(hubcloud_link)
    if gen_link:
        final_link = get_final_link(gen_link)
        if final_link:
            return jsonify({
                "status": "success",
                "final_link": final_link,
                "step_1_hubcloud": hubcloud_link
            })
    
    return jsonify({"status": "fail", "message": "Final Link filter nahi hua (Shayad Javascript required hai)"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
