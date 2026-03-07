import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse, parse_qs

def js_sunucu_bul(html_icerik):
    """
    Sayfa kaynağındaki JavaScript kodlarından yayın sunucusunu (baseStreamUrl) yakalar.
    """
    # Regex: this.baseStreamUrl = 'https://...' yapısını bulur
    pattern = r"this\.baseStreamUrl\s*=\s*['\"](.*?)['\"]"
    match = re.search(pattern, html_icerik)
    if match:
        return match.group(1)
    
    # Alternatif: Herhangi bir /live/ linkini yakala
    pattern_fallback = r'https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z0-9-]+)+/live/'
    match_fallback = re.search(pattern_fallback, html_icerik)
    return match_fallback.group(0) if match_fallback else "https://dga1op10s1u3leo.7af32068d38fdf.click/live/"

def maclari_kaydet():
    # Tarayıcı gibi davranması için ayarlar
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    # Kayıt yolu (script nerede çalışırsa JSON orada oluşur)
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "yayinlar.json")
    
    # Hedef site adresi
    target_site = "https://www.xsportv-44fc2b2514.xyz/"
    
    try:
        print(f"📡 Site taranıyor: {target_site}")
        response = scraper.get(target_site, timeout=30)
        
        if response.status_code == 200:
            # 1. Sunucu adresini JS içinden çek
            base_url = js_sunucu_bul(response.text)
            print(f"🔗 Bulunan Sunucu: {base_url}")

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. 'item' class'ına sahip tüm maç kutucuklarını bul
            items = soup.find_all("div", class_="item")
            
            yayin_listesi = []
            
            for item in items:
                # data-url'si olmayan (başlık satırları vb.) divleri atla
                data_url = item.get('data-url', '').strip()
                if not data_url:
                    continue
                
                # Başlığı 'title' özniteliğinden al
                baslik = item.get('title', '').strip()
                
                # Link içindeki 'id' parametresini ayıkla (xsmartspor vb.)
                parsed_query = parse_qs(urlparse(data_url).query)
                stream_id = parsed_query.get('id', [''])[0]
                
                if stream_id and baslik:
                    # Saat bilgisini span içinden al (time veya live class'ı)
                    saat_tag = item.find("span", class_=["time", "live"])
                    saat = saat_tag.get_text(strip=True) if saat_tag else "CANLI"
                    
                    # Branş tespiti (football, basketball vb. class'lar)
                    classes = item.get('class', [])
                    brans = "Futbol" if "football" in classes else "Basketbol" if "basketball" in classes else "Spor"
                    
                    # Final veriyi listeye ekle
                    yayin_listesi.append({
                        "saat": saat,
                        "baslik": baslik,
                        "brans": brans,
                        "m3u8": f"{base_url}{stream_id}/playlist.m3u8"
                    })
                    print(f"✅ Yakalandı: [{saat}] {baslik}")

            # 3. Verileri JSON dosyasına kaydet
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(yayin_listesi, f, ensure_ascii=False, indent=4)
            
            print(f"\n🚀 İŞLEM TAMAM: {len(yayin_listesi)} maç 'yayinlar.json' dosyasına yazıldı.")
            
        else:
            print(f"❌ Siteye ulaşılamadı. Hata Kodu: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Kritik Hata: {e}")

if __name__ == "__main__":
    maclari_kaydet()
