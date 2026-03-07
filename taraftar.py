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
    # Yedek arama (herhangi bir /live/ linki)
    pattern_fallback = r'https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z0-9-]+)+/live/'
    match_fallback = re.search(pattern_fallback, html_icerik)
    return match_fallback.group(0) if match_fallback else "https://dga1op10s1u3leo.7af32068d38fdf.click/live/"

def maclari_kaydet():
    # Cloudflare engellerini aşmak için scraper
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    # JSON kayıt yolu
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "yayinlar.json")
    
    # Hedef site
    target_site = "https://www.xsportv-44fc2b2514.xyz/"
    
    try:
        print(f"📡 Futbol maçları taranıyor: {target_site}")
        response = scraper.get(target_site, timeout=30)
        
        if response.status_code == 200:
            # 1. Yayın sunucusunu otomatik bul
            base_url = js_sunucu_bul(response.text)
            print(f"🔗 Sunucu Adresi: {base_url}")

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Sadece 'item' ve 'football' class'ına sahip divleri bul
            # Bu sayede basketbol vb. diğer branşlar en baştan elenir
            items = soup.find_all("div", class_="item football")
            
            yayin_listesi = []
            
            for item in items:
                # İçerideki data-url barındıran div'e ulaş
                icerik_div = item.find("div", attrs={"data-url": True})
                
                if icerik_div:
                    data_url = icerik_div.get('data-url', '').strip()
                    baslik = icerik_div.get('title', '').strip()
                    
                    # ID ayıkla
                    parsed_query = parse_qs(urlparse(data_url).query)
                    stream_id = parsed_query.get('id', [''])[0]
                    
                    if stream_id and baslik:
                        # Saati çek
                        saat_tag = icerik_div.find("span", class_="time")
                        saat = saat_tag.get_text(strip=True) if saat_tag else "CANLI"
                        
                        # Listeye ekle
                        yayin_listesi.append({
                            "saat": saat,
                            "baslik": baslik,
                            "m3u8": f"{base_url}{stream_id}/playlist.m3u8"
                        })
                        print(f"⚽ Futbol Yakalandı: [{saat}] {baslik}")

            # 3. Sadece futbol maçlarını içeren JSON'u kaydet
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(yayin_listesi, f, ensure_ascii=False, indent=4)
            
            print(f"\n🚀 Tamamlandı: {len(yayin_listesi)} adet futbol maçı kaydedildi.")
            
        else:
            print(f"❌ Siteye erişilemedi: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Hata oluştu: {e}")

if __name__ == "__main__":
    maclari_kaydet()
