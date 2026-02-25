import pandas as pd
from bs4 import BeautifulSoup
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# =============================================================================
# YAPILANDIRMA
# =============================================================================
TARGET_ID = 444  # Breast Cancer
TARGET_NAME = "BC"
DATA_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\Targeted_Markers"
os.makedirs(DATA_DIR, exist_ok=True)

class SeleniumMiner:
    def __init__(self):
        print("🔧 Tarayıcı yapılandırılıyor...")
        chrome_options = Options()
        # Arka planda çalışsın isterseniz alttaki satırı açın (ama görerek takip etmek daha iyi)
        # chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("✅ Tarayıcı Hazır.")

    def find_hmdb_robust(self, soup_row):
        """
        Satırın HTML içeriğinde HMDB kodunu arar (Resim alt text, link, düz yazı fark etmez).
        """
        # 1. Önce Resim Alt Etiketine Bak (En güvenilir yer)
        img = soup_row.find('img')
        if img and img.get('alt'):
            match = re.search(r'Hmdb\d+', img['alt'], re.IGNORECASE)
            if match: return match.group(0).upper()
            
        # 2. Bulamazsa tüm satırın metnini tara
        text = str(soup_row)
        match = re.search(r'HMDB\d{5,7}', text, re.IGNORECASE)
        return match.group(0).upper() if match else None

    def scrape(self):
        print(f"\n🚀 SELENIUM MINER: {TARGET_NAME} (ID: {TARGET_ID})")
        
        csv_path = os.path.join(DATA_DIR, f"{TARGET_NAME}_Selenium.csv")
        # Dosya yoksa oluştur
        if not os.path.exists(csv_path):
            pd.DataFrame(columns=['name', 'mdbid', 'hmdb_id', 'biofluid', 'auc', 'page']).to_csv(csv_path, index=False)

        page = 1
        previous_names = [] # Sayfa tekrarını kontrol etmek için

        try:
            while True:
                url = f"https://markerdb.ca/conditions/{TARGET_ID}?page={page}"
                print(f"🌍 Sayfa {page} yükleniyor...", end="")
                
                self.driver.get(url)
                
                # Sayfanın ve JS'in yüklenmesi için bekle (İnternet hızına göre artırılabilir)
                time.sleep(3) 
                
                # HTML'i al ve Parse et
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Sadece Chemical Tablosunu Bul
                chem_div = soup.find('div', id='Chemical_Biomarkers')
                
                if not chem_div:
                    print(" -> Kimyasal sekmesi yok. (Veri bitti veya Genetik sayfalarına geçildi).")
                    # Eğer sayfa 1'de bile yoksa hata vardır, ama sayfa 50'de yoksa bitmiştir.
                    if page == 1: print("❌ HATA: İlk sayfada tablo bulunamadı.")
                    break

                rows = chem_div.find_all('tr')
                batch_data = []
                
                for row in rows:
                    # İçerik satırı mı?
                    info_td = row.find('td', class_='right')
                    if not info_td: continue
                    
                    # İsim ve MDBID
                    h3 = info_td.find('h3')
                    if not h3: continue
                    
                    raw_text = h3.get_text().strip()
                    m_name = raw_text.split('(')[0].strip()
                    m_mdbid_match = re.search(r'MDB\d+', raw_text)
                    m_mdbid = m_mdbid_match.group(0) if m_mdbid_match else "N/A"
                    
                    # HMDB ID (Robust Arama)
                    m_hmdb = self.find_hmdb_robust(row)
                    
                    # Detaylar (Biofluid / AUC)
                    biofluid, auc = "N/A", "N/A"
                    row_str = str(row)
                    
                    if "Biofluid" in row_str:
                        try: biofluid = row_str.split("Biofluid")[1].split("</td>")[0].split(">")[-1].strip()
                        except: pass
                    if "AUC" in row_str:
                        try: 
                            auc_match = re.search(r'AUC[:\s]+([\d\.]+)', row_str)
                            if auc_match: auc = auc_match.group(1)
                        except: pass

                    batch_data.append({
                        'name': m_name, 'mdbid': m_mdbid, 'hmdb_id': m_hmdb,
                        'biofluid': biofluid, 'auc': auc, 'page': page
                    })

                # --- KONTROLLER ---
                if not batch_data:
                    print(" -> Tabloda veri yok.")
                    break
                
                # Sayfa tekrarı kontrolü (Sitenin sonsuz döngü bug'ına karşı)
                current_names = [x['name'] for x in batch_data]
                if current_names == previous_names:
                    print("\n🛑 DUR: Sayfa içeriği bir öncekiyle aynı. Pagination bitti.")
                    break
                previous_names = current_names

                # KAYDET
                df = pd.DataFrame(batch_data)
                df.to_csv(csv_path, mode='a', header=False, index=False)
                
                hmdb_count = df['hmdb_id'].notna().sum()
                print(f" -> ✅ Alındı: {len(df)} kayıt. (HMDB: {hmdb_count}) | İlk: {batch_data[0]['name']}")

                # Next butonu kontrolü
                # Selenium ile de kontrol edebiliriz ama Soup daha hızlı
                next_btn = soup.find('a', string=re.compile(r'Next', re.I))
                if not next_btn:
                    print(f"\n🏁 'Next' butonu yok. Tarama tamamlandı.")
                    break
                
                page += 1

        except Exception as e:
            print(f"\n❌ Kritik Hata: {e}")
        finally:
            self.driver.quit()
            print("🔌 Tarayıcı kapatıldı.")

if __name__ == "__main__":
    miner = SeleniumMiner()
    miner.scrape()