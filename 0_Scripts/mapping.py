import requests
import json
import time
import os
import pandas as pd

# =============================================================================
# YAPILANDIRMA
# =============================================================================
API_KEY = "cc69fb7c1a4809bbae7c0701d5188c17"
INPUT_JSON = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_FULL_MAPPING.json"
OUTPUT_FINAL = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_ENRICHED_DATABASE.json"
CHEMICAL_API_URL = "http://markerdb.ca/api/v1/chemicalapi/chemicalrequest"

def enrich_with_hmdb():
    print("🚀 HMDB ID Zenginleştirme Başlatılıyor...")
    
    # 1. Mevcut Mapping Verisini Yükle
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    # Benzersiz MDBID'leri bul (Aynı marker birden fazla hastalıkta olabilir)
    unique_mdbids = list(set([item['mdbid'] for item in master_data if 'mdbid' in item]))
    print(f"📦 Toplam {len(master_data)} kayıtta {len(unique_mdbids)} benzersiz MDBID tespit edildi.")

    # 2. Daha önceden çekilenleri yükle (Checkpoint)
    enriched_results = {}
    if os.path.exists(OUTPUT_FINAL):
        with open(OUTPUT_FINAL, 'r', encoding='utf-8') as f:
            enriched_results = json.load(f)
        print(f"🔄 Checkpoint: {len(enriched_results)} adet HMDB zaten çekilmiş.")

    # 3. API'den Tek Tek HMDB Sorgula
    for i, mdbid in enumerate(unique_mdbids):
        if mdbid in enriched_results: continue # Zaten varsa geç
        
        print(f"🔎 Sorgulanıyor ({i+1}/{len(unique_mdbids)}): {mdbid}...", end="\r")
        
        params = {"api_key": API_KEY, "markerdb_id": mdbid}
        try:
            r = requests.get(CHEMICAL_API_URL, params=params, timeout=20)
            if r.status_code == 200:
                res_data = r.json()
                compound = res_data.get("compound", {})
                
                # Sadece ihtiyacımız olan alanları alalım
                enriched_results[mdbid] = {
                    "hmdb_id": compound.get("hmdb"),
                    "formula": compound.get("moldb_formula"),
                    "smiles": compound.get("moldb_smiles"),
                    "description": compound.get("description")
                }
            
            # API nezaketi (Hızlı istek atıp banlanmamak için)
            time.sleep(0.5)
            
            # Her 50 istekte bir dosyayı güncelle (Güvenlik)
            if i % 50 == 0:
                with open(OUTPUT_FINAL, 'w', encoding='utf-8') as f:
                    json.dump(enriched_results, f, indent=4)
                    
        except Exception as e:
            print(f"\n⚠️ {mdbid} hatası: {e}")
            continue

    # 4. Final Kayıt
    with open(OUTPUT_FINAL, 'w', encoding='utf-8') as f:
        json.dump(enriched_results, f, indent=4)
    
    print(f"\n\n✅ ZENGİNLEŞTİRME TAMAMLANDI.")
    print(f"💾 Veritabanı şurada: {OUTPUT_FINAL}")

if __name__ == "__main__":
    enrich_with_hmdb()