import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse, parse_qs

def js_sunucu_bul(html_icerik):
    # Sayfa kaynağındaki baseStreamUrl değişkenini yakalar
    pattern = r"this\.baseStreamUrl\s*=\s*['\"](.*?)['\"]"
    match = re.search(pattern, html_icerik)
    if match:
        return match.group(1)
    # Yedek arama
    pattern_fallback = r'https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z0-9-]+)+/live/'
    match_fallback = re.search(pattern_fallback, html_icerik)
    return match_fallback.group(0) if match_fallback else "https://dga1op10s1u3leo.7af32068d38fdf.click/live/"

def maclari_kaydet():
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "yayinlar.json")
    
    # Sabit Referer ve Origin Adresi
    sabit_adres = "https://www.xsportv-44fc2b2514.xyz/"
    
    try:
        response = scraper.get(sabit_adres, timeout=30)
        if response.status_code == 200:
            # Güncel yayın sunucusunu çek (m3u8 linki için)
            base_url = js_sunucu_bul(response.text)

            soup = BeautifulSoup(response.text, 'html.parser')
            # Sadece futbol olanları çek
            items = soup.find_all("div", class_="item football")
            
            yayin_items = []
            
            for item in items:
                icerik_div = item.find("div", attrs={"data-url": True})
                if icerik_div:
                    data_url = icerik_div.get('data-url', '').strip()
                    baslik = icerik_div.get('title', '').strip()
                    
                    # ID ayıkla
                    stream_id = parse_qs(urlparse(data_url).query).get('id', [''])[0]
                    
                    if stream_id and baslik:
                        saat_tag = icerik_div.find("span", class_="time")
                        saat = saat_tag.get_text(strip=True) if saat_tag else "CANLI"
                        
                        final_m3u8 = f"{base_url}{stream_id}/playlist.m3u8"
                        
                        # --- ÖZEL JSON YAPISI (Referer Sabitlendi) ---
                        yayin_items.append({
                            "service": "iptv",
                            "title": baslik,
                            "playlistURL": "",
                            "media_url": final_m3u8,
                            "url": final_m3u8,
                            "h1Key": "accept",
                            "h1Val": "*/*",
                            "h2Key": "referer",
                            "h2Val": sabit_adres,
                            "h3Key": "origin",
                            "h3Val": sabit_adres,
                            "h4Key": "0",
                            "h4Val": "0",
                            "h5Key": "0",
                            "h5Val": "0",
                            "thumb_square": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Football_Pictogram.svg/1200px-Football_Pictogram.svg.png",
                            "group": saat
                        })

            final_data = {
                "list": {
                    "service": "iptv",
                    "title": "Canli Futbol",
                    "item": yayin_items
                }
            }

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ {len(yayin_items)} futbol maçı JSON formatına (sabıt referer ile) çevrildi.")
            
    except Exception as e:
        print(f"⚠️ Hata: {e}")

if __name__ == "__main__":
    maclari_kaydet()
