import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urlparse, parse_qs

print("🚀 Akıllı Sunucu Tespiti ve Yayın Çekici Başlatıldı...")

def dinamik_sunucu_yakala(html_icerik):
    """
    Paylaştığın 'this.baseStreamUrl = ...' yapısını 
    HTML içindeki binlerce satır arasından bulur.
    """
    # Regex: this.baseStreamUrl = 'URL' kalıbını yakalar
    patterns = [
        r"this\.baseStreamUrl\s*=\s*['\"](.*?)['\"]",
        r"baseUrl\s*:\s*this\.baseStreamUrl",
        r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z0-9-]+/live/"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_icerik)
        if match:
            # Eğer ilk pattern (this.baseStreamUrl) eşleşirse linki grup 1'den al
            url = match.group(1) if match.lastindex else match.group(0)
            if url.startswith('http'):
                print(f"📡 OTOMATİK TESPİT EDİLDİ: {url}")
                return url
    return None

def maclari_kaydet():
    # Cloudflare bypass edici
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    current_folder = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_folder, "yayinlar.json")
    
    # Maç listesinin olduğu ana sayfa
    ana_sayfa_url = "https://www.xsportv-44fc2b2514.xyz/"
    
    try:
        print(f"🌐 Ana site taranıyor: {ana_sayfa_url}")
        response = scraper.get(ana_sayfa_url, timeout=30)
        
        if response.status_code == 200:
            # 1. ADIM: Dinamik Sunucuyu Bul
            # Not: Sunucu adresi bazen ana sayfada, bazen iframe içindedir. 
            # Bu kod ana sayfada bulamazsa listedeki ilk maçın sayfasına gidip oradan çeker.
            base_url = dinamik_sunucu_yakala(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all("div", attrs={"data-url": True})
            
            # Eğer ana sayfada sunucu yoksa, ilk maçı örneklem alalım
            if not base_url and items:
                print("🔍 Sunucu ana sayfada yok, detay sayfasından çekiliyor...")
                ornek_mac_url = items[0].get('data-url')
                ornek_res = scraper.get(ornek_mac_url, timeout=15)
                base_url = dinamik_sunucu_yakala(ornek_res.text)

            if not base_url:
                print("❌ HATA: Sunucu adresi bulunamadı!")
                return

            # 2. ADIM: Maçları İşle
            yayin_listesi = []
            for item in items:
                baslik = item.get('title', '').strip()
                data_url = item.get('data-url', '').strip()
                
                # ID Ayıkla (id=xsmartspor gibi)
                params = parse_qs(urlparse(data_url).query)
                stream_id = params.get('id', [''])[0]
                
                if stream_id and baslik:
                    # m3u8 Linkini Oluştur
                    final_m3u8 = f"{base_url}{stream_id}/playlist.m3u8"
                    
                    saat_tag = item.find("span", class_=["time", "live"])
                    saat = saat_tag.get_text(strip=True) if saat_tag else "CANLI"
                    
                    yayin_listesi.append({
                        "saat": saat,
                        "baslik": baslik,
                        "m3u8": final_m3u8
                    })
                    print(f"✅ Yakalandı: {baslik}")

            # 3. ADIM: Kaydet
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(yayin_listesi, f, ensure_ascii=False, indent=4)
            
            print(f"\n✨ BİTTİ! {len(yayin_listesi)} yayın güncel sunucuyla kaydedildi.")
            
    except Exception as e:
        print(f"⚠️ Hata: {e}")

if __name__ == "__main__":
    maclari_kaydet()
    input("\nKapatmak için Enter'a basın...")
