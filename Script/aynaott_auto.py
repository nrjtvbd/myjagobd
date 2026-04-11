import requests
import re
import os
from datetime import datetime

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Referer": "https://aynaott.com/"
}

def inspect_token(php_url):
    try:
        res = session.get(php_url, headers=headers, timeout=12, allow_redirects=True)
        # URL বা Response Body থেকে টোকেন খোঁজা
        match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', res.url)
        if not match:
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', res.text)
        return match.group(1) if match else None
    except:
        return None

def main():
    print("🚀 Starting Fully Automated Channel Discovery...")
    
    source_file = "Script/aynaott.txt"
    if not os.path.exists(source_file):
        print(f"❌ Error: {source_file} not found!")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    m3u_content = "#EXTM3U\n"
    success_count = 0
    channel_count = 0
    fallback = "e=1775943478&u=78be6644-0a65-48ec-81a4-089ac65a2619&token=ad943974b438c7507cfb7d505f02b373"

    # লাইন বাই লাইন প্রসেসিং যাতে ফরম্যাট একটু আলাদা হলেও কাজ করে
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            # চ্যানেলের নাম বের করা (কমা এর পরের অংশ)
            name_match = re.search(r',([^,]*)$', line)
            channel_name = name_match.group(1).strip() if name_match else "Unknown Channel"
            
            # পরবর্তী লাইনে থাকা লিঙ্ক থেকে আইডি বের করা
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                id_match = re.search(r'id=([^&\s]+)', next_line)
                
                if id_match:
                    channel_id = id_match.group(1)
                    channel_count += 1
                    
                    # সার্ভার ডিটেকশন
                    srv = "tvsen7" if "tsports" in channel_id.lower() else "tvsen6"
                    
                    print(f"🔍 [{channel_count}] Inspecting: {channel_name}...")
                    php_link = f"http://sm-monirul.top/Ayha/play.php?id={channel_id}"
                    token = inspect_token(php_link)
                    
                    if token:
                        print(f"   ✅ Fresh Token Found!")
                        success_count += 1
                    else:
                        print(f"   ⚠️ Using fallback.")
                        token = fallback

                    final_url = f"https://{srv}.aynascope.net/{channel_id}/index.m3u8?{token}"
                    m3u_content += f'#EXTINF:-1 group-title="AynaOTT", {channel_name}\n{final_url}\n\n'

    if channel_count == 0:
        print("❌ No channels found! Please check if aynaott.txt has the correct format.")
        return

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"\n✨ Done! Processed {channel_count} channels.")
    print(f"📈 Success: {success_count} | Fallback: {channel_count - success_count}")

if __name__ == "__main__":
    main()
