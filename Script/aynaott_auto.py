import requests
import re
import json
from datetime import datetime

def get_all_channels():
    """aynaott.com থেকে সব চ্যানেলের নাম এবং স্লাগ সংগ্রহের জন্য সবচেয়ে শক্তিশালী প্যাটার্ন"""
    url = "https://aynaott.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"🔎 Scanning {url} for all available channels...")
        response = requests.get(url, headers=headers, timeout=15)
        
        # এই প্যাটার্নটি /live/ এর পরের অংশ এবং ট্যাগের ভেতরে থাকা নাম খুঁজে নেবে
        # এটি আরও নমনীয়ভাবে তৈরি করা হয়েছে
        matches = re.findall(r'href=["\'](?:https://aynaott\.com)?/live/([a-zA-Z0-9_-]+)["\'][^>]*>(.*?)<', response.text, re.DOTALL)
        
        channels = []
        unique_slugs = set()
        
        for slug, title in matches:
            # HTML ট্যাগ এবং অতিরিক্ত স্পেস পরিষ্কার করা
            clean_name = re.sub('<[^<]+?>', '', title).strip()
            
            # যদি নাম না পাওয়া যায়, তবে স্লাগ থেকে নাম তৈরি করবে
            if not clean_name:
                clean_name = slug.replace('-', ' ').title()
            
            if slug not in unique_slugs and len(slug) > 2:
                channels.append({"name": clean_name, "slug": slug})
                unique_slugs.add(slug)
        
        if not channels:
            print("⚠️ Automatic scan failed, using fallback list.")
            channels = [
                {"name": "Somoy TV", "slug": "somoy-tv"},
                {"name": "T Sports", "slug": "t-sports"},
                {"name": "Jamuna TV", "slug": "jamuna-tv"},
                {"name": "Ekattor TV", "slug": "ekattor-tv"}
            ]
        
        print(f"✅ Found {len(channels)} channels.")
        return channels
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def fetch_ayna_info(slug):
    """টোকেন এবং সার্ভার ইউআরএল খুঁজে বের করা"""
    base_url = f"https://aynaott.com/live/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=15)
        source = response.text
        
        # সার্ভার ডিটেকশন (tvsen5, tvsen7 ইত্যাদি)
        stream_match = re.search(r'(https?://[a-z0-9.]+\.aynascope\.net/[a-zA-Z0-9_-]+/)?index\.m3u8', source)
        if not stream_match:
            # অল্টারনেট প্যাটার্ন যদি সোর্স সরাসরি থাকে
            stream_match = re.search(r'["\'](https?://[a-z0-9.]+\.aynascope\.net/.*?/index\.m3u8.*?)["\']', source)
            if stream_match:
                return stream_match.group(1)
            return None
        
        # প্যারামিটার এক্সট্রাকশন
        token = re.search(r'token=([a-zA-Z0-9]+)', source).group(1)
        expiry = re.search(r'e=(\d+)', source).group(1)
        uid = re.search(r'u=([a-z0-9-]+)', source).group(1)
        
        final_url = f"{stream_match.group(1)}index.m3u8?e={expiry}&u={uid}&token={token}"
        return final_url
    except:
        return None

def main():
    channels = get_all_channels()
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    internal_data = {"status": "active", "updated": True, "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": []}
    m3u_content = "#EXTM3U\n"

    for ch in channels:
        url = fetch_ayna_info(ch['slug'])
        if url:
            internal_data["payload"].append({"name": ch['name'], "src": url, "type": "LiveTV"})
            m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{url}{vlc_headers}\n\n'
            print(f"✔️ Added: {ch['name']}")

    with open("internal_data.json", "w", encoding="utf-8") as jf:
        json.dump(internal_data, jf, indent=4)
    with open("AynaOTT.m3u", "w", encoding="utf-8") as mf:
        mf.write(m3u_content)
    print("\n✅ Success!")

if __name__ == "__main__":
    main()
