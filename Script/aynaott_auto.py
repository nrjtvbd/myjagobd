import requests
import re
import os
from datetime import datetime

# Browser fake korar jonno headers
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Referer": "https://aynaott.com/",
    "Origin": "https://aynaott.com"
}

def get_live_token():
    """Aynascope-er main site theke fresh token khuje ber korar method"""
    sources = [
        "https://aynaott.com/live/btv-world",
        "https://aynaott.com/live/t-sports-hd",
        "https://aynaott.com/live/somoy-tv"
    ]
    
    for url in sources:
        try:
            # Proxy ba Direct request
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                # Token pattern khuje ber kora
                match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', response.text)
                if match:
                    return match.group(1)
        except:
            continue
    return None

def main():
    print("🚀 Fetching Fresh Token from Aynascope Main Server...")
    
    # Live Token collect kora
    fresh_token = get_live_token()
    
    if fresh_token:
        print(f"✅ Success! New Token Found: {fresh_token[:20]}...")
    else:
        print("⚠️ Direct Scraping failed. Checking Monirul's Mirror...")
        # Monirul-er PHP theke token extract korar alternative chesta (Proxy diye)
        try:
            r = requests.get("https://api.allorigins.win/get?url=http://sm-monirul.top/Ayha/play.php?id=btv_world")
            content = r.json().get('contents', '')
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', content)
            fresh_token = match.group(1) if match else "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"
        except:
            fresh_token = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    # aynaott.txt file theke channel list load kora
    with open("Script/aynaott.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    matches = re.findall(r'#EXTINF:.*,(.*)\n.*id=([^&\s]+)', content)
    
    m3u_content = "#EXTM3U\n"
    for name, ch_id in matches:
        srv = "tvsen7" if "tsport" in ch_id.lower() else "tvsen6"
        final_url = f"https://{srv}.aynascope.net/{ch_id}/index.m3u8?{fresh_token}"
        m3u_content += f'#EXTINF:-1 group-title="NRJTVBD", {name.strip()}\n{final_url}\n\n'

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print(f"✨ Playlist Updated with {len(matches)} channels at {datetime.now()}")

if __name__ == "__main__":
    main()
