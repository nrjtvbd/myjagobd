import requests
import json
import re
from datetime import datetime

# সেশন হ্যান্ডলার যাতে কুকি বজায় থাকে
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://aynaott.com/"
}

def get_individual_token(slug):
    """প্রতিটি চ্যানেলের জন্য আলাদা টোকেন বের করার ফাংশন"""
    url = f"https://aynaott.com/live/{slug}"
    try:
        # গিটহাব থেকে সরাসরি না হলে এটি 'None' রিটার্ন করবে
        response = session.get(url, headers=headers, timeout=15)
        source = response.text
        match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', source)
        if match:
            return match.group(1)
    except:
        pass
    return None

def main():
    print("🚀 Fetching Individual Tokens for Each Channel...")
    
    # আয়নাস্কোপের ওয়েব স্লাগ এবং সার্ভার আইডি
    channels = [
        {"name": "BTV World", "web_slug": "btv-world", "srv_id": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports", "web_slug": "t-sports-hd", "srv_id": "t_sports_hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "web_slug": "somoy-tv", "srv_id": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "web_slug": "gtv-live", "srv_id": "gtv_live", "srv": "tvsen6"},
        {"name": "Jamuna TV", "web_slug": "jamuna-tv", "srv_id": "jamuna_tv", "srv": "tvsen6"}
    ]
    
    m3u_content = "#EXTM3U\n"
    success_count = 0
    
    # আপনার দেওয়া ডিফল্ট টোকেন (যদি স্ক্র্যাপিং ফেইল করে তবে এটি সবগুলোতে বসবে)
    fallback_token = "e=1775940669&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=195bd93f51092339fd1d166017efd6b3"

    for ch in channels:
        print(f"📡 Requesting token for: {ch['name']}...")
        token = get_individual_token(ch['web_slug'])
        
        if not token:
            print(f"⚠️ Failed for {ch['name']}, using fallback.")
            token = fallback_token
        else:
            success_count += 1
            print(f"✅ Success!")

        # সঠিক লিঙ্ক তৈরি
        final_url = f"https://{ch['srv']}.aynascope.net/{ch['srv_id']}/index.m3u8?{token}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{final_url}\n\n'

    # ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n✨ Completed! Successfully scraped {success_count} fresh tokens.")

if __name__ == "__main__":
    main()
