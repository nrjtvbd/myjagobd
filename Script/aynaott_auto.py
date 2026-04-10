import requests
import re
import json
from datetime import datetime

def get_all_channels():
    """aynascope.net থেকে সব চ্যানেলের নাম এবং স্লাগ সংগ্রহ করার উন্নত ফাংশন"""
    url = "https://aynascope.net/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    try:
        print(f"🔎 Scanning {url} for all available channels...")
        response = requests.get(url, headers=headers, timeout=20)
        
        # aynascope এর নতুন লিঙ্কিং ফরম্যাট অনুযায়ী স্লাগ বের করা
        matches = re.findall(r'href=["\'](?:https://aynascope\.net)?/live/([a-zA-Z0-9_-]+)["\'][^>]*>(.*?)<', response.text, re.DOTALL)
        
        channels = []
        unique_slugs = set()
        
        for slug, title in matches:
            clean_name = re.sub('<[^<]+?>', '', title).strip()
            if not clean_name: clean_name = slug.replace('-', ' ').title()
            
            # অপ্রয়োজনীয় স্লাগ ফিল্টার
            if slug not in unique_slugs and len(slug) > 2:
                channels.append({"name": clean_name, "slug": slug})
                unique_slugs.add(slug)
        
        if not channels:
            print("⚠️ Automatic scan failed on aynascope, using backup list.")
            return [
                {"name": "Somoy TV", "slug": "somoy-tv"},
                {"name": "T Sports", "slug": "t-sports-hd"},
                {"name": "GTV", "slug": "gtv-live"},
                {"name": "Jamuna TV", "slug": "jamuna-tv"}
            ]
        
        print(f"✅ Found {len(channels)} channels on Aynascope.")
        return channels
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        return []

def fetch_aynascope_info(slug):
    """সরাসরি aynascope থেকে টোকেন এবং সার্ভার ইউআরএল খুঁজে বের করা"""
    base_url = f"https://aynascope.net/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://aynascope.net/"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        html = response.text
        
        # উন্নত রেজেক্স: যা সরাসরি ফুল ইউআরএল খুঁজে নেবে
        stream_match = re.search(r'https?://[a-z0-9.]+\.aynascope\.net/[a-zA-Z0-9_-]+/index\.m3u8\?e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+', html)
        
        if stream_match:
            return stream_match.group(0)
            
        # যদি ফুল ইউআরএল না পায়, তবে পার্ট বাই পার্ট খুঁজবে
        server = re.search(r'(https?://[a-z0-9.]+\.aynascope\.net/[a-zA-Z0-9_-]+/)index\.m3u8', html)
        token = re.search(r'token=([a-zA-Z0-9]+)', html)
        expiry = re.search(r'e=(\d+)', html)
        uid = re.search(r'u=([a-z0-9-]+)', html)
        
        if server and token:
            return f"{server.group(1)}index.m3u8?e={expiry.group(1)}&u={uid.group(1)}&token={token.group(1)}"
        return None
    except:
        return None

def main():
    print("🚀 Aynascope Super Auto Update Started...")
    channels = get_all_channels()
    
    # VLC Header (Aynascope Referer সহ)
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36&Referer=https://aynascope.net/"
    
    internal_data = {
        "status": "active",
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "payload": []
    }
    
    m3u_content = "#EXTM3U\n"
    success_count = 0

    for ch in channels:
        live_url = fetch_aynascope_info(ch['slug'])
        if live_url:
            internal_data["payload"].append({
                "name": ch['name'],
                "src": live_url,
                "type": "LiveTV"
            })
            
            m3u_content += f'#EXTINF:-1 group-title="Aynascope",{ch["name"]}\n'
            m3u_content += f"{live_url}{vlc_headers}\n\n"
            success_count += 1
            print(f"✔️ Added: {ch['name']}")

    # ফাইলগুলো সেভ করা
    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
        
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)

    print(f"\n✅ Finished! {success_count} channels updated from Aynascope.")

if __name__ == "__main__":
    main()
