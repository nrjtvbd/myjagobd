import requests
import json
import re
from datetime import datetime

def get_btv_world_token():
    # সরাসরি আয়নাস্কোপের মোবাইল/ওয়েব API সোর্স থেকে ডাটা নেওয়ার চেষ্টা
    url = "https://aynaott.com/live/btv-world"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        source = response.text
        
        # রেজেক্স দিয়ে লিঙ্ক থেকে প্যারামিটার বের করা
        match = re.search(r'index\.m3u8\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', source)
        if match:
            return match.group(1)
            
        # যদি ফুল লিঙ্ক না পায় তবে ভেঙে ভেঙে খোঁজা
        e = re.search(r'e=(\d+)', source)
        u = re.search(r'u=([a-z0-9-]+)', source)
        t = re.search(r'token=([a-zA-Z0-9]+)', source)
        
        if e and u and t:
            return f"e={e.group(1)}&u={u.group(1)}&token={t.group(1)}"
    except:
        pass
    return None

def main():
    print("🚀 Running Independent AynaOTT Scraper...")
    
    token_query = get_btv_world_token()
    
    # যদি গিটহাব আইপি ব্লক থাকে, তবে আমরা একটি স্ট্যাটিক প্যারামিটার দেব 
    # যাতে অন্তত প্লেলিস্ট ফাইলটি তৈরি হয় এবং ফেইল না করে
    if not token_query:
        print("⚠️ GitHub IP might be blocked. Using fallback method.")
        # আপনি ব্রাউজার থেকে পাওয়া লেটেস্ট কুয়েরি এখানে দিতে পারেন সাময়িকভাবে
        token_query = "e=1775936088&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=72b315b564b4c931bebd88d28525a2f8"

    channels = [
        {"name": "BTV World", "id": "btv_world", "srv": "tvsen6"},
        {"name": "T Sports", "id": "t_sports_hd", "srv": "tvsen7"},
        {"name": "Somoy TV", "id": "somoy_tv", "srv": "tvsen6"},
        {"name": "GTV Live", "id": "gtv_live", "srv": "tvsen6"}
    ]
    
    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36&Referer=https://aynaott.com/"
    
    m3u_content = "#EXTM3U\n"
    payload = []

    for ch in channels:
        final_url = f"https://{ch['srv']}.aynascope.net/{ch['id']}/index.m3u8?{token_query}"
        m3u_content += f'#EXTINF:-1 group-title="AynaOTT",{ch["name"]}\n{final_url}{vlc_headers}\n\n'
        payload.append({"name": ch["name"], "url": final_url})
        print(f"✅ Ready: {ch['name']}")

    # ফাইল সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    with open("internal_data.json", "w", encoding="utf-8") as f:
        json.dump({"last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "channels": payload}, f, indent=4)

    print("✨ Process Completed.")

if __name__ == "__main__":
    main()
