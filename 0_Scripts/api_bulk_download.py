import requests
import json
import time
import os

API_KEY = "cc69fb7c1a4809bbae7c0701d5188c17"
BASE_URL = "http://markerdb.ca/api/v1/generalapi/generalrequest"
OUTPUT_FILE = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_MASTER_MAP.json"

def download_markerdb_bulk():
    print("🚀 MarkerDB Bulk Downloader Başlatıldı...")
    
    all_extracted_markers = []
    current_page = 1
    total_pages = 999 # Geçici başlangıç değeri
    
    headers = {"Content-type": "application/json"}

    while current_page <= total_pages:
        print(f"📥 Sayfa {current_page}/{total_pages if total_pages != 999 else '?'} indiriliyor...", end="\r")
        
        params = {
            "api_key": API_KEY,
            "category": "Diagnostic",
            "biomarker_type": "Chemical",
            "page": current_page
        }

        try:
            r = requests.get(BASE_URL, params=params, headers=headers, timeout=20)
            if r.status_code == 200:
                data = r.json()
                
                # Toplam sayfa sayısını ilk sayfada öğreniyoruz
                if current_page == 1:
                    total_pages = data.get("total_page", 1)
                
                # Karmaşık JSON yapısını düzleştir (Flatten)
                # API 'biomarkers' altında garip string keyler döndürüyor, onları temizleyip alıyoruz
                biomarkers_dict = data.get("biomarkers", {})
                for _, marker_list in biomarkers_dict.items():
                    for entry in marker_list:
                        all_extracted_markers.append(entry)
                
                current_page += 1
                time.sleep(1) # API nezaketi (Abuse koruması)
            else:
                print(f"\n❌ Sayfa {current_page} hatası: {r.status_code}")
                break
        except Exception as e:
            print(f"\n❌ Bağlantı hatası: {e}")
            break

    # Locale Kaydet
    if all_extracted_markers:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_extracted_markers, f, indent=4, ensure_ascii=False)
        print(f"\n\n✅ İŞLEM TAMAMLANDI!")
        print(f"📁 Toplam {len(all_extracted_markers)} marker-hastalık eşleşmesi kaydedildi.")
        print(f"📍 Dosya: {OUTPUT_FILE}")
    else:
        print("\n❌ Hiç veri çekilemedi.")

if __name__ == "__main__":
    download_markerdb_bulk()