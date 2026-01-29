from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time
import re
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- BROWSER SETUP ---
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Render Path
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(options=chrome_options)
    
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver

# --- MAIN LOGIC ---
def scrape_hubcloud(url):
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        
        # 1. Cloudflare Bypass
        time.sleep(5)
        
        # 2. Find & Click Button
        try:
            download_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "download"))
            )
            driver.execute_script("arguments[0].click();", download_btn)
        except:
            return {"success": False, "error": "Download button not found"}
        
        # 3. Wait for Redirect
        time.sleep(10)
        
        # 4. Scrape Links
        page_source = driver.page_source
        
        # Whitelist (Jo links chahiye)
        whitelist = [r'r2\.dev', r'fsl-lover\.buzz', r'fsl-cdn-1\.sbs', r'fukggl\.buzz']
        # Blacklist (Jo nahi chahiye)
        blacklist = [r'pixeldrain', r'hubcdn', r'workers\.dev', r'\.zip$']
        
        all_links = re.findall(r'https?://[^\s"\'<>]+', page_source)
        final_links = []
        
        for link in all_links:
            if any(re.search(p, link) for p in whitelist) and not any(re.search(p, link) for p in blacklist):
                if link not in final_links:
                    final_links.append(link)
                    
        return {"success": True, "total": len(final_links), "links": final_links}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if driver:
            driver.quit()

# --- ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return "API is Running! Use /solve-cloud?url=YOUR_LINK"

@app.route('/solve-cloud', methods=['GET'])
def solve_cloud():
    url = request.args.get('url')
    if not url: return jsonify({"error": "Missing URL"}), 400
    
    return jsonify(scrape_hubcloud(url))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
