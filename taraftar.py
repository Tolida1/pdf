import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse, parse_qs

def js_sunucu_bul(html_icerik):
    pattern = r"this\.baseStreamUrl\s*=\s*['\"](.*?)['\"]"
    match = re.search(pattern, html_icerik)
    if match: return match.group(1)
    pattern_fallback = r'https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z0-9-]+)+/live/'
    match_fallback = re.search(pattern_fallback, html_icerik)
    return match_fallback.group(0) if match_fallback else "https://dga1op10s1u3leo.7af32068d38fdf.click/live/"

def maclari_kaydet():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    # JSON dosyasını her zaman scriptin yanına oluştur
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "yayinlar.json")
    
    target_site = "https://www.xsportv-44fc2b2514.xyz/"
    
    try:
        response = scraper.get(target_site, timeout=30)
        if response.status_code == 200:
            base_url = js_sunucu_bul(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all("div", attrs={"data-url": True})
            
            yayin_listesi = []
            for item in items:
                baslik = item.get('title', '').strip()
                data_url = item.get('data-url', '').strip()
                stream_id = parse_qs(urlparse(data_url).query).get('id', [''])[0]
                
                if stream_id and baslik:
                    saat_tag = item.find("span", class_=["time", "live"])
                    saat = saat_tag.get_text(strip=True) if saat_tag else "CANLI"
                    yayin_listesi.append({"saat": saat, "baslik": baslik, "m3u8": f"{base_url}{stream_id}/playlist.m3u8"})

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(yayin_listesi, f, ensure_ascii=False, indent=4)
            print(f"✅ Başarılı: {len(yayin_listesi)} maç kaydedildi.")
    except Exception as e:
        print(f"⚠️ Hata: {e}")

if __name__ == "__main__":
    maclari_kaydet()
