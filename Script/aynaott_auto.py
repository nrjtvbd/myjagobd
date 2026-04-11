import requests
import re
import json
from datetime import datetime

def fetch_btv_world():
    """আপনার দেওয়া স্পেসিফিক হেডার এবং ইউআরএল ব্যবহার করে টোকেন সংগ্রহের মেথড"""
    
    # মূল পেজ যেখানে টোকেন জেনারেট হয় (আপনার দেওয়া স্লাগ অনুযায়ী)
    page_url = "https://aynaott.com/live/btv-world" 
    
    # আপনার ইনস্পেক্ট করা ডাটা থেকে নেওয়া নিখুঁত হেডার
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://aynaott.com/",
        "Sec-CH-UA": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        print(f"📡 Fetching BTV World from aynaott...")
        response = requests.get(page_url, headers=headers, timeout=15)
        source = response.text

        # আপনার দেওয়া ইউআরএল স্ট্রাকচার অনুযায়ী রেজেক্স (tvsen6.aynascope.net)
        # এটি সরাসরি e, u, এবং token প্যারামিটারগুলো খুঁজে বের করবে
        match = re.search(r'["\'](https?://tvsen6\.aynascope\.net/btv_world/index\.m3u8\?e=(\d+)&u=([a-z0-9-]+)&token=([a-zA-Z0-9]+))["\']', source)
        
        if match:
            full_url = match.group(1)
            print(f"✅ Successfully extracted link!")
            return full_url
        
        # ব্যাকআপ প্যাটার্ন: যদি ডাইনামিকলি প্যারামিটারগুলো আলাদা থাকে
        server = "https://tvsen6.aynascope.net/btv_world/index.m3u8"
        token = re.search(r'token=([a-zA-Z0-9]+)', source)
        expiry = re.search(r'e=(\d+)', source)
        uid = re.search(r'u=([a-z0-9-]+)', source)

        if token and expiry and uid:
            final_link = f"{server}?e={expiry.group(1)}&u={uid.group(1)}&token={token.group(1)}"
            print(f"✅ Extracted link using backup pattern.")
            return final_link

    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    live_link = fetch_btv_world()
    
    # VLC বা OTT অ্যাপে প্লে করার জন্য হেডার স্ট্রিং (আপনার দেওয়া UA সহ)
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynaott.com/"

    if live_link:
        # JSON ফাইল তৈরি
        data = {
            "status": "active",
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "payload": [{"name": "BTV World", "src": live_link}]
        }
        
        # M3U ফাইল তৈরি
        m3u = f'#EXTM3U\n#EXTINF:-1 group-title="AynaOTT",BTV World\n{live_link}{vlc_headers}'
        
        with open("internal_data.json", "w", encoding="utf-8") as jf:
            json.dump(data, jf, indent=4)
        with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
            mf.write(m3u)
            
        print("🚀 Files updated successfully!")
    else:
        print("❌ Could not get live link. Check if the site is down or blocking GitHub.")

if __name__ == "__main__":
    main()
