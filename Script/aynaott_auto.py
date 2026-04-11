import requests
import json
from datetime import datetime

def generate_playlist():
    print("🚀 Running AynaOTT Multi-Source Scraper...")

    # বর্তমান কার্যকরী ডাটা সোর্স (এটি সরাসরি JSON ডাটা সরবরাহ করে)
    # যদি একটি ফেইল করে, আমরা অন্যটি ব্যবহার করার মেকানিজম রেখেছি
    sources = [
        "https://raw.githubusercontent.com/m-m-i-n/AynaOTT/main/assets/data.json",
        "https://m-m-i-n.github.io/AynaOTT/internal_data.json"
    ]

    data_json = None
    for url in sources:
        try:
            print(f"📡 Trying source: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data_json = response.json()
                print("✅ Data successfully fetched!")
                break
        except:
            continue

    if not data_json:
        print("❌ All sources failed (404 or Timeout).")
        return

    # ডাটা থেকে চ্যানেলের লিস্ট বের করা (মনিরুল ইসলামের নতুন ফরম্যাট অনুযায়ী)
    channels = data_json.get("payload", []) or data_json.get("channels", [])
    
    if not channels:
        print("⚠️ No channel data found in JSON.")
        return

    vlc_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36&Referer=https://aynaott.com/"

    try:
        with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            count = 0
            for ch in channels:
                # বিভিন্ন সোর্সে কি-এর নাম আলাদা হতে পারে (src অথবা url)
                name = ch.get("name") or ch.get("title", "Unknown")
                url = ch.get("src") or ch.get("url", "").strip()
                logo = ch.get("logo", "")
                
                if url:
                    f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="AynaOTT",{name}\n')
                    f.write(f"{url}{vlc_headers}\n\n")
                    count += 1
        
        # আপনার নিজের ব্যবহারের জন্য JSON কপি সেভ করে রাখা
        with open("internal_data.json", "w", encoding="utf-8") as jf:
            json.dump({"status": "active", "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": channels}, jf, indent=4)

        print(f"✨ Playlist updated with {count} channels.")

    except Exception as e:
        print(f"❌ Error saving files: {e}")

if __name__ == "__main__":
    generate_playlist()
