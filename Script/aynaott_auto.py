import requests
import re
import os
import time
import concurrent.futures

# উন্নত হেডার সেটআপ - যা দেখতে একদম আসল অ্যান্ড্রয়েড অ্যাপের মতো
HEADERS = {
    "User-Agent": "AynaOTT/1.0.3 (Linux; Android 10; K) Mobile/1.0.3",
    "Referer": "https://aynaott.com/",
    "X-Requested-With": "com.aynascope.aynaott",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def get_token(ch_id):
    """মনিরুলের লিঙ্ক থেকে সরাসরি টোকেন বের করার জন্য ভিন্ন ভিন্ন ৩টি সোর্স ট্রাই করা"""
    urls = [
        f"http://sm-monirul.top/Ayha/play.php?id={ch_id}",
        f"http://sm-monirul.top/AyNa/play.php?id={ch_id}"
    ]
    
    for url in urls:
        try:
            # সরাসরি রিকোয়েস্ট (কোনো প্রক্সি ছাড়া)
            response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            # টেক্সট বা ফাইনাল ইউআরএল থেকে টোকেন খোঁজা
            source = response.url + response.text
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', source)
            if match:
                return match.group(1)
        except:
            continue
    return None

def process_channel(name, ch_id):
    name = name.strip()
    ch_id = ch_id.strip()
    
    token = get_token(ch_id)
    if token:
        srv = "tvsen7" if "tsport" in ch_id.lower() or "sports" in ch_id.lower() else "tvsen6"
        link = f"https://{srv}.aynascope.net/{ch_id}/index.m3u8?{token}"
        return f'#EXTINF:-1 group-title="NRJTVBD", {name}\n{link}\n\n'
    return None

def main():
    print("🚀 Starting Professional AynaOTT Recovery (272 Channels)...")
    source_path = "Script/aynaott.txt"
    
    if not os.path.exists(source_path):
        print("❌ Source file not found!")
        return

    with open(source_path, "r", encoding="utf-8") as f:
        data = f.read()

    matches = re.findall(r'#EXTINF:.*,(.*)\n.*id=([^&\s]+)', data)
    print(f"📂 Total Channels Found: {len(matches)}")

    results = []
    # থ্রেড সংখ্যা কমিয়ে ৫ করা হয়েছে যাতে সার্ভার থেকে ব্লক না করে
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ch = {executor.submit(process_channel, n, i): n for n, i in matches}
        
        for future in concurrent.futures.as_completed(future_to_ch):
            res = future.result()
            ch_name = future_to_ch[future]
            if res:
                results.append(res)
                print(f"✅ {ch_name} -> Token Hijacked!")
            else:
                print(f"❌ {ch_name} -> Still Blocked")
            
            # সার্ভারকে রেস্ট দিতে সামান্য গ্যাপ (rate limiting bypass)
            time.sleep(0.5)

    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "".join(results))

    print(f"\n📊 Extraction Complete: {len(results)}/272 channels synced.")

if __name__ == "__main__":
    main()
