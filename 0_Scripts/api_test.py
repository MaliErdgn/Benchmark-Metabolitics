import requests
import json
import pandas as pd
import time
import os
import re
from datetime import datetime

# =============================================================================
# 1. YAPILANDIRMA
# =============================================================================
API_KEY = "cc69fb7c1a4809bbae7c0701d5188c17"
MAP_URL = "http://markerdb.ca/api/v1/generalapi/generalrequest"
CHEM_URL = "http://markerdb.ca/api/v1/chemicalapi/chemicalrequest"

# Dosya Yolları
DATA_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data"
OUTPUT_CSV = os.path.join(DATA_DIR, "MARKERDB_ULTIMATE_DATABASE.csv")
LOG_FILE = os.path.join(DATA_DIR, "MINING_LOG_DETAILED.txt")
os.makedirs(DATA_DIR, exist_ok=True)

class UltimateMiningEngine:
    def __init__(self):
        self.headers = {"Content-type": "application/json"}
        self.hmdb_cache = {} # Aynı marker için defalarca API'ye gitmemek için
        self.master_records = []
        self.start_time = time.time()
        self.safety_threshold = 50 # Sizin istediğiniz '50 sayfa boşsa dur' kuralı

    def get_hmdb_details(self, mdbid):
        """MDBID kullanarak o marker'ın HMDB ID'sini Chemical API'den çeker."""
        if mdbid in self.hmdb_cache:
            return self.hmdb_cache[mdbid]
        
        # KAYNAK: API Dokümanı - Chemical Biomarkers section
        params = {"api_key": API_KEY, "markerdb_id": mdbid}
        try:
            r = requests.get(CHEM_URL, params=params, timeout=20)
            if r.status_code == 200:
                compound = r.json().get("compound", {})
                details = {
                    "hmdb": compound.get("hmdb"),
                    "formula": compound.get("moldb_formula"),
                    "smiles": compound.get("moldb_smiles"),
                    "iupac": compound.get("moldb_iupac")
                }
                self.hmdb_cache[mdbid] = details
                return details
        except: pass
        return {"hmdb": None, "formula": None, "smiles": None, "iupac": None}

    def run(self, categories=["Diagnostic", "Prognostic", "Risk", "Exposure"]):
        print(f"⛏️  Mining Operasyonu Başlatıldı (Safety Threshold: {self.safety_threshold} sayfa)")
        
        try:
            for cat in categories:
                print(f"\n--- KATEGORİ: {cat.upper()} ---")
                page = 1
                empty_streak = 0 

                while True:
                    params = {
                        "api_key": API_KEY,
                        "category": cat,
                        "biomarker_type": "Chemical",
                        "page": page
                    }
                    
                    response = requests.get(MAP_URL, params=params, timeout=30)
                    if response.status_code != 200:
                        print(f"\n❌ Sayfa {page} Hatası: {response.status_code}")
                        break
                    
                    data = response.json()
                    biomarkers = data.get("biomarkers", {})

                    # VERİ KONTROLÜ (Boş mu?)
                    if not biomarkers or len(biomarkers) == 0:
                        empty_streak += 1
                        if empty_streak >= self.safety_threshold:
                            print(f"\n🏁 {cat} bitti. {empty_streak} sayfa boşluk görüldü.")
                            break
                        # Boş sayfada sayfa sayısını artırıp devam ediyoruz
                        page += 1
                        continue
                    
                    # Veri geldiyse sayacı sıfırla
                    empty_streak = 0
                    page_new_hits = 0
                    
                    for key, entries in biomarkers.items():
                        for entry in entries:
                            mdbid = entry.get('mdbid')
                            
                            # ANLIK ZENGİNLEŞTİRME: HMDB ID'sini çek
                            details = self.get_hmdb_details(mdbid)
                            
                            full_record = {
                                "Category": cat,
                                "Disease_Name": entry.get('condition_name'),
                                "Disease_ID": entry.get('condition_id'),
                                "Marker_Name": entry.get('biomarker_name'),
                                "MDBID": mdbid,
                                "HMDB_ID": details['hmdb'],
                                "Formula": details['formula'],
                                "SMILES": details['smiles'],
                                "IUPAC": details['iupac'],
                                "Page_Source": page
                            }
                            self.master_records.append(full_record)
                            page_new_hits += 1
                    
                    # KONSOL TAKİBİ
                    print(f"   📄 P:{page} | Streak:{empty_streak} | New:{page_new_hits} | Total:{len(self.master_records)} | Cache:{len(self.hmdb_cache)}", end="\r")
                    
                    # Her 10 sayfada bir CSV güncelle (Checkpoint)
                    if page % 10 == 0:
                        self.save_to_disk()

                    page += 1
                    time.sleep(0.4) # API nazı

            self.save_to_disk()
            self.generate_report()

        except KeyboardInterrupt:
            print("\n\n🛑 Manuel Durdurma! Veriler kurtarılıyor...")
            self.save_to_disk()
            self.generate_report()

    def save_to_disk(self):
        if self.master_records:
            df = pd.DataFrame(self.master_records)
            df.to_csv(OUTPUT_CSV, index=False)

    def generate_report(self):
        df = pd.DataFrame(self.master_records)
        duration = (time.time() - self.start_time) / 60
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"MARKERDB MINING REPORT\n{'='*30}\n")
            f.write(f"Bitiş: {datetime.now()}\n")
            f.write(f"Süre: {duration:.2f} dk\n")
            f.write(f"Toplam Kayıt: {len(df)}\n")
            f.write(f"HMDB Mevcut: {df['HMDB_ID'].notna().sum()}\n")
            f.write(f"HMDB Eksik: {df['HMDB_ID'].isna().sum()}\n\n")
            f.write("HASTALIK DAĞILIMI:\n")
            f.write(df['Disease_Name'].value_counts().to_string())

if __name__ == "__main__":
    engine = UltimateMiningEngine()
    engine.run()