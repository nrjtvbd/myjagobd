import requests
import re
import json
from datetime import datetime

def get_all_channels():
    # যেহেতু ডোমেইন রেজোলিউশন এরর দিচ্ছে, আমরা একটি সলিড ফলব্যাক লিস্ট রাখব
    # যাতে স্ক্র্যাপার ফেইল করলেও আপনার কাজ বন্ধ না হয়।
    fallback_list = [
        {"name": "Somoy TV", "slug": "somoy-tv"},
        {"name": "T Sports HD", "slug": "t-sports-hd"},
        {"name": "GTV Live", "slug": "gtv-live"},
        {"name": "Jamuna TV", "slug": "jamuna-tv"},
        {"name": "Ekattor TV", "slug": "ekattor-tv"},
        {"name": "Independent TV", "slug": "independent-tv"},
        {"name": "Channel 24", "slug": "channel-24"},
        {"name": "RTV", "slug": "rtv-live"},
        {"name": "NTV", "slug": "ntv-live"},
        {"name": "News 24", "slug": "news-24"}
    ]

    urls_to_try = ["https://aynaott.com/", "https://aynascope.net/"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    for url in urls_to_try:
        try:
            print(f"🔎 Scanning {url}...")
            response = requests.get(url, headers=headers, timeout=10)
            matches = re.findall(r'/live/([a-zA-Z0-9_-]+)', response.text)
            unique_slugs = list(set([s for s in slugs if len(s) > 2]))
            
            if unique_slugs:
                channels = [{"name": s.replace('-', ' ').title(), "slug": s} for s in unique_slugs]
                print(f"✅ Found {len(channels)} channels from {url}")
                return channels
        except Exception as e:
            print(f"⚠️ Could not reach {url}: {e}")
            continue
            
    print("📢 Using fallback list due to connection issues.")
    return fallback_list

def fetch_ayna_info(slug):
    # এখানে আমরা সরাসরি আয়নাস্কোপের সাবডোমেইনগুলো হিট করার চেষ্টা করব
    # কারণ অনেক সময় মেইন ডোমেইন ব্লক থাকলেও সাবডোমেইন কাজ করে।
    base_url = f"https://aynaott.com/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        source = response.text
        
        # সরাসরি টোকেনসহ লিঙ্ক খোঁজা
        token_url = re.search(r'https?://[a-z0-9.]+\.aynascope\.net/.*?/index\.m3u8\?e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+', source)
        if token_url:
            return token_url.group(0)
            
        # প্যারামিটার আলাদাভাবে খোঁজা
        server = re.search(r'(https?://[a-z0-9.]+\.aynascope\.net/.*?/)index\.m3u8', source)
        token = re.search(r'token=([a-zA-Z0-9]+)', source)
        if server and token:
            e = re.search(r'e=(\d+)', source).group(1)
            u = re.search(r'u=([a-z0-9-]+)', source).group(1)
            return f"{server.group(1)}index.m3u8?e={e}&u={u}&token={token.group(1)}"
    except:
        return None

def main():
    channels = get_all_channels()
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    internal_data = {"status": "active", "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": []}
    m3u_content = "#EXTM3U\n"

    for ch in channels:
        live_link = fetch_ayna_info(ch['slug'])
        if live_link:
            internal_data["payload"].append({"name": ch['name'], "src": live_link, "type": "LiveTV"})
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{live_link}{vlc_headers}\n\n'
            print(f"✔️ Added: {ch['name']}")

    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)
    print("✅ All Done!")

if __name__ == "__main__":
    main()
