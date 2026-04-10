import requests
import re
import json
from datetime import datetime

def get_all_channels():
    """aynaott.com থেকে সব চ্যানেলের নাম এবং স্লাগ সংগ্রহ করার ফাংশন"""
    url = "https://aynaott.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"🔎 Scanning {url} for all available channels...")
        response = requests.get(url, headers=headers, timeout=15)
        # নতুন ডোমেইন অনুযায়ী লিঙ্কের প্যাটার্ন
        matches = re.findall(r'href="https://aynaott\.com/live/([a-zA-Z0-9_-]+)".*?title="(.*?)"', response.text)
        
        channels = []
        unique_slugs = set()
        
        for slug, title in matches:
            if slug not in unique_slugs:
                channels.append({"name": title, "slug": slug})
                unique_slugs.add(slug)
        
        print(f"✅ Found {len(channels)} channels automatically.")
        return channels
    except Exception as e:
        print(f"❌ Could not scrape channel list: {e}")
        return []

def fetch_ayna_info(slug):
    """সঠিক সার্ভার এবং টোকেন খুঁজে বের করা"""
    base_url = f"https://aynaott.com/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        source = response.text
        
        # সার্ভার ইউআরএল প্যাটার্ন (tvsen5/7 ইত্যাদি)
        stream_match = re.search(r'(https?://[a-z0-9.]+\.aynascope\.net/([a-zA-Z0-9_-]+)/)index\.m3u8', source)
        if not stream_match: return None
        
        main_stream_url = stream_match.group(1) + "index.m3u8"
        
        # টোকেন প্যারামিটার এক্সট্রাকশন
        token = re.search(r'token=([a-zA-Z0-9]+)', source).group(1)
        expiry = re.search(r'e=(\d+)', source).group(1)
        uid = re.search(r'u=([a-z0-9-]+)', source).group(1)
        
        return f"{main_stream_url}?e={expiry}&u={uid}&token={token}"
    except:
        return None

def main():
    channels_to_track = get_all_channels()
    
    if not channels_to_track:
        # যদি অটো না পায় তবে অন্তত গুরুত্বপূর্ণ দুটি চ্যানেল ট্রাই করবে
        channels_to_track = [
            {"name": "Somoy TV", "slug": "somoy-tv"},
            {"name": "T Sports", "slug": "t-sports"}
        ]

    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    internal_data = {"status": "active", "payload": []}
    m3u_content = "#EXTM3U\n"

    for ch in channels_to_track:
        live_link = fetch_ayna_info(ch['slug'])
        if live_link:
            internal_data["payload"].append({"name": ch['name'], "src": live_link})
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{live_link}{vlc_headers}\n\n'
            print(f"✔️ Added: {ch['name']}")

    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)

if __name__ == "__main__":
    main()
