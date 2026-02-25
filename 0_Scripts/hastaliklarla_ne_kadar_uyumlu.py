import json
import pandas as pd
import os

# =============================================================================
# DOSYA YOLLARI
# =============================================================================
GLOBAL_DB_PATH = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_GLOBAL_DATABASE.json"
MAPPING_PATH = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\new-synonym-mapping.json"
OUTPUT_REPORT = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_COVERAGE_REPORT.csv"

# Hedef Hastalık Anahtar Kelimeleri (Case-insensitive aranacak)
TARGET_DISEASES = {
    "Alzheimer": ["Alzheimer"],
    "BC_BRCA": ["Breast Cancer", "Malignant neoplasm of breast"],
    "Diabetes": ["Diabetes Mellitus", "Type 2 Diabetes"],
    "PDAC": ["Pancreatic Cancer", "Pancreas"],
    "PRAD": ["Prostate Cancer"]
}

def analyze_coverage():
    print("🚀 Coverage Analysis Started...")
    
    # 1. VERİTABANINI YÜKLE
    try:
        with open(GLOBAL_DB_PATH, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
        print(f"✅ Global DB Yüklendi: {len(db_data)} kayıt.")
    except Exception as e:
        print(f"❌ DB Okuma Hatası: {e}")
        return

    # 2. MAPPING YÜKLE
    try:
        with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        # Normalize et: Küçük harf ve boşluksuz
        norm_map = {str(k).lower().strip(): v for k, v in mapping.items()}
        print(f"✅ Synonym Mapping Yüklendi: {len(norm_map)} anahtar.")
    except Exception as e:
        print(f"❌ Mapping Hatası: {e}")
        return

    # 3. ANALİZ DÖNGÜSÜ
    disease_stats = {k: {"Total_Markers": 0, "Chemicals": 0, "Mapped": 0, "Unmapped": 0} for k in TARGET_DISEASES.keys()}
    unmapped_list = []

    print("\n🔎 Hastalıklar taranıyor ve eşleştiriliyor...")
    
    for entry in db_data:
        # Sadece Kimyasal olanlar bizim işimize yarar (Recon3D metaboliktir)
        is_chemical = entry.get('type') == 'Chemical'
        
        # Hangi hastalığa ait?
        associated_ds = []
        cond_list = entry.get('associated_conditions', [])
        cond_str = " ".join([c['condition_name'] for c in cond_list]).lower()
        
        for ds_key, keywords in TARGET_DISEASES.items():
            for kw in keywords:
                if kw.lower() in cond_str:
                    associated_ds.append(ds_key)
                    break # Bir hastalığa bir kez ekle
        
        if not associated_ds: continue # Bizim hastalıklarla ilgisi yoksa geç

        # Eşleşme Kontrolü (Hibrit)
        hmdb_id = entry.get('hmdb_id')
        name = entry.get('marker_name')
        
        # 1. HMDB ile dene
        rid = None
        if hmdb_id:
            rid = norm_map.get(hmdb_id.lower().strip())
        
        # 2. İsim ile dene (Eğer HMDB yoksa veya eşleşmediyse)
        if not rid and name:
            rid = norm_map.get(name.lower().strip())

        # İstatistikleri Güncelle
        for ds in associated_ds:
            disease_stats[ds]["Total_Markers"] += 1
            if is_chemical:
                disease_stats[ds]["Chemicals"] += 1
                if rid:
                    disease_stats[ds]["Mapped"] += 1
                else:
                    disease_stats[ds]["Unmapped"] += 1
                    # Kayıp listesine ekle (Analiz için)
                    if is_chemical: # Sadece kimyasalları raporla
                        unmapped_list.append({
                            "Disease": ds,
                            "Marker": name,
                            "HMDB": hmdb_id,
                            "Type": entry.get('type')
                        })

    # 4. RAPORLAMA
    print("\n" + "="*80)
    print(f"{'DISEASE':<15} | {'TOTAL':<8} | {'CHEMICAL':<8} | {'MAPPED (Recon3D)':<18} | {'COVERAGE %':<10}")
    print("-" * 80)
    
    for ds, stats in disease_stats.items():
        chem = stats["Chemicals"]
        mapped = stats["Mapped"]
        # Kapsama oranı sadece Kimyasallar üzerinden hesaplanır (Proteinleri mapleyemeyiz)
        coverage = (mapped / chem * 100) if chem > 0 else 0
        
        print(f"{ds:<15} | {stats['Total_Markers']:<8} | {chem:<8} | {mapped:<18} | {coverage:.1f}%")
    print("="*80)

    # Kayıpları kaydet (Belki manuel eklenir)
    if unmapped_list:
        pd.DataFrame(unmapped_list).drop_duplicates().to_csv(r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\UNMAPPED_MARKERS.csv", index=False)
        print(f"\nℹ️ Eşleşmeyen {len(unmapped_list)} marker 'UNMAPPED_MARKERS.csv' dosyasına kaydedildi.")

if __name__ == "__main__":
    analyze_coverage()