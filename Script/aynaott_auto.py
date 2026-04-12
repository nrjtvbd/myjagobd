import requests
import re
import os
import time
import concurrent.futures

# এটি আপনার রিপোজিটরি থেকে আইডিগুলো পড়ার জন্য
SOURCE_FILE = "Script/aynaott.txt"

def hijack_token(ch_name, ch_id):
    """সরাসরি আয়নাস্কোপের প্লেয়ার থেকে টোকেন বের করার মেথড"""
    # আয়নাস্কোপ এখন রেফারার এবং কুকি ছাড়া টোকেন দেয় না
    session = requests.Session()
    
    # ব্রাউজার ইমুলেশন হেডার
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://aynaott.com/",
        "Origin": "https://aynaott.com",
        "Accept": "*/*"
    }

    try:
        # ধাপ ১: মনিরুলের লিঙ্ক ব্যবহার করে আয়নাস্কোপের ডাইরেক্ট প্লেয়ার লিঙ্কে যাওয়া
        # আমরা সরাসরি মনিরুলের সার্ভার থেকে রিডাইরেক্ট হয়ে টোকেনটি ধরার চেষ্টা করবো
        bridge_url = f"http://sm-monirul.top/AyNa/play.php?id={ch_id}"
        
        # আমরা AllOrigins প্রক্সি ব্যবহার করছি গিটহাবের আইপি ব্লক এড়াতে
        proxy_url = f"https://api.allorigins.win/get?url={bridge_url}"
        
        response = session.get(proxy_url, timeout=15)
        if response.status_code == 200:
            content = response.json().get('contents', '')
            
            # ধাপ ২: কন্টেন্ট থেকে টোকেন প্যারামিটার খুঁজে বের করা (e, u, token)
            match = re.search(r'\?(e=\d+&u=[a-z0-9-]+&token=[a-zA-Z0-9]+)', content)
            
            if match:
                token_string = match.group(1)
                
                # সার্ভার নোড অটো সিলেকশন
                if "tsports" in ch_id.lower() or "sports" in ch_id.lower():
                    srv = "tvsen7"
                elif len(ch_id) > 20 and "-" not in ch_id: # Star Sports type IDs
                    srv = "tvsen5"
                else:
                    srv = "tvsen6"
                
                final_link = f"https://{srv}.aynascope.net/{ch_id}/index.m3u8?{token_string}"
                return f'#EXTINF:-1 group-title="NRJTVBD", {ch_name}\n{final_link}\n\n'
    except Exception:
        pass
    return None

def main():
    print("🔓 Starting Token Hijacking from Aynascope...")
    
    if not os.path.exists(SOURCE_FILE):
        print("❌ aynaott.txt missing!")
        return

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        data = f.read()

    matches = re.findall(r'#EXTINF:.*,(.*)\n.*id=([^&\s]+)', data)
    print(f"📡 Targets Identified: {len(matches)} channels.")

    results = []
    # ৫টি থ্রেড দিয়ে কাজ করছি যাতে আয়নাস্কোপের ফায়ারওয়াল সন্দেহ না করে
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ch = {executor.submit(hijack_token, n.strip(), i.strip()): n for n, i in matches}
        
        for future in concurrent.futures.as_completed(future_to_ch):
            res = future.result()
            if res:
                results.append(res)
                print(f"✅ Captured: {future_to_ch[future]}")
            else:
                print(f"💀 Failed: {future_to_ch[future]}")
            
            # আয়নাস্কোপকে বিভ্রান্ত করতে সামান্য বিরতি
            time.sleep(0.2)

    # প্লেলিস্ট সেভ করা
    with open("AynaOTT.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "".join(results))

    print(f"\n💎 Successfully Hijacked {len(results)}/272 tokens.")

if __name__ == "__main__":
    main()
