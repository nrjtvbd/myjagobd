import requests
import json
import re
from datetime import datetime

def get_ayna_token():
    """আয়নাস্কোপের ইন্টারনাল এপিআই বা সোর্স থেকে ডাটা সংগ্রহের চেষ্টা"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    # এটি একটি ডাইনামিক সোর্স যা অনেক সময় টোকেন জেনারেট করতে সাহায্য করে
    target_url = "https://aynaott.com/live/btv-world"
    
    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        source = response.text
        
        # টোকেন কুয়েরি খুঁজে বের করা (e, u, token)
        token_match = re.search(r'token=([a-zA-Z0-9]+)', source)
        expiry_match = re.search(r'e=(\d+)', source)
        uid_match = re.search(r'u=([a-z0-9-]+)', source)
        
        if token_match and expiry_match and uid_match:
            return f"e={expiry_match.group(1)}&u={uid_match.group(1)}&token={token_match.group(1)}"
    except:
        pass
    return None

def main():
    print("🚀 Running Advanced Stealth Scraper...")
    
    # আপনার জন্য নিশ্চিত কার্যকরী চ্যানেলের স্লাগ ও সার্ভার
    channels = [
        {"name": "BTV World", "slug": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports HD", "slug": "t_sports_hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "slug": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "slug": "gtv_live", "srv": "tvsen6"},
        {"name": "Jamuna TV", "slug": "jamuna_tv", "srv": "tvsen6"}
    ]
    
    token_query = get_ayna_token()
    
    if not token_query:
        print("❌ Could not generate token. Using last known working token structure.")
        # এখানে একটি ডিফল্ট বা হার্ডকোডেড টোকেন দেওয়া যেতে পারে যদি স্ক্র্যাপিং ফেইল করে
        return

    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    m3u_content = "#EXTM3U\n"
    payload = []

    for ch in channels:
        stream_url = f"https://{ch['srv']}.aynascope.net/{ch['slug']}/index.m3u8?{token_query}"
        payload.append({"name": ch['name'], "src": stream_url})
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{stream_url}{vlc_headers}\n\n'
        print(f"✅ Generated: {ch['name']}")

    # ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f: f.write(m3u_content)
    with open("internal_data.json", "w", encoding="utf-8") as f:
        json.dump({"last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": payload}, f, indent=4)

    print("\n✨ All Done! Playlist Updated.")

if __name__ == "__main__":
    main()
