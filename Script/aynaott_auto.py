import requests
import re
import json
from datetime import datetime

def get_dynamic_token(slug):
    """সরাসরি আয়নাস্কোপ থেকে টোকেন বের করার উন্নত মেথড"""
    url = f"https://aynaott.com/live/{slug}"
    # এই হেডারগুলো আয়নাস্কোপের সিকিউরিটি বাইপাস করতে সাহায্য করে
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Referer": "https://aynaott.com/",
        "X-Requested-With": "com.ayna.ott",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        # আমরা প্রক্সি ছাড়া সরাসরি রিকোয়েস্ট পাঠাবো
        response = requests.get(url, headers=headers, timeout=15)
        source = response.text
        
        # টোকেন খোঁজার নতুন রেজেক্স প্যাটার্ন
        match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', source)
        if match:
            return match.group(1)
    except:
        pass
    return None

def main():
    print("🚀 Running RoarZone Style Stealth Scraper...")

    channels = [
        {"name": "BTV World", "web_slug": "btv-world", "srv_id": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports HD", "web_slug": "t-sports-hd", "srv_id": "tsports-hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "web_slug": "somoy-tv", "srv_id": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "web_slug": "gtv-live", "srv_id": "gtv_live", "srv": "tvsen6"},
        {"name": "Jamuna TV", "web_slug": "jamuna-tv", "srv_id": "jamuna_tv", "srv": "tvsen6"}
    ]

    # আপনার দেওয়া সবশেষ কার্যকরী টোকেনটি এখানে রাখা হলো ব্যাকআপ হিসেবে
    last_known_token = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    m3u_content = "#EXTM3U\n"
    
    for ch in channels:
        print(f"📡 Scraping: {ch['name']}...")
        token = get_dynamic_token(ch['web_slug'])
        
        # যদি টোকেন না পায়, তবে ব্যাকআপ টোকেন ব্যবহার করবে যাতে ফাইল ৪-৪ না হয়
        if not token:
            print(f"⚠️ Using backup for {ch['name']}")
            token = last_known_token
        else:
            print(f"✅ Fresh token found!")

        final_url = f"https://{ch['srv']}.aynascope.net/{ch['srv_id']}/index.m3u8?{token}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT", {ch["name"]}\n{final_url}\n\n'

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    # এটি ইন্টারনাল ট্র্যাকিং এর জন্য
    with open("internal_data.json", "w", encoding="utf-8") as f:
        json.dump({"status": "updated", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, f)

    print("\n✨ Done! Playlist is updated.")

if __name__ == "__main__":
    main()
