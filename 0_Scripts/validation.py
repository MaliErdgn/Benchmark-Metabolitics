import json
import pandas as pd
import os
import re

# =============================================================================
# YAPILANDIRMA (KAYNAKLAR DOĞRULANDI)
# =============================================================================
JSON_PATH = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_GLOBAL_DATABASE.json"
MAPPING_PATH = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\new-synonym-mapping.json"
ML_FEATURES = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"
MODEL_PATH = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\Recon3D.json"

OUTPUT_CSV = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\PATHWAY_VALIDATION_RESULTS.csv"

# Hastalık Eşleme Sözlüğü
DISEASE_MAP = {
    "BC": "Breast Cancer", "BRCA": "Breast Cancer",
    "Alzheimer": "Alzheimer", "Diabetes": "Diabetes",
    "PDAC": "Pancreatic", "PRAD": "Prostate"
}

def run_ultimate_pathway_validation():
    print("🧬 Ultimate Pathway Validation Engine Starting...")

    # 1. BIOLOGICAL MAP (RECON3D) YÜKLE
    # -------------------------------------------------------------------------
    with open(MODEL_PATH, 'r') as f:
        model = json.load(f)
    
    # Metabolit ID -> Pathway Kümesi haritası (Recon3D Stokiyometrisi)
    met_to_pathways = {}
    for rxn in model['reactions']:
        pathway = rxn.get('subsystem', 'Unknown')
        for met_id in rxn['metabolites'].keys():
            # Kompartman ekini temizle (glc_c -> glc)
            clean_met = re.sub(r'_[a-z]$', '', met_id)
            if clean_met not in met_to_pathways: met_to_pathways[clean_met] = set()
            met_to_pathways[clean_met].add(pathway)
    print(f"✅ Recon3D yüklendi. {len(met_to_pathways)} metabolit yolaklara bağlandı.")

    # 2. MAPPING VE MARKERDB YÜKLE
    # -------------------------------------------------------------------------
    with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    norm_map = {str(k).lower().strip(): v for k, v in mapping.items()}

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # 3. ML SONUÇLARINI YÜKLE
    # -------------------------------------------------------------------------
    df_ml = pd.read_csv(ML_FEATURES, low_memory=False)
    
    validation_hits = []

    # 4. ÇAPRAZ SORGULAMA DÖNGÜSÜ
    # -------------------------------------------------------------------------
    print("🔎 Validating...")
    for entry in db:
        m_name = str(entry['marker_name']).lower().strip()
        m_hmdb = str(entry['hmdb_id']).lower().strip() if entry['hmdb_id'] else None
        
        # Recon3D ID'sini bul (İsim veya HMDB üzerinden)
        recon_met_id = norm_map.get(m_hmdb) or norm_map.get(m_name)
        if not recon_met_id: continue
        
        # Bu metabolitin temsil ettiği Pathway'ler
        clean_rid = recon_met_id.split('_')[0]
        clinical_pathways = met_to_pathways.get(clean_rid, set())

        # Bu marker hangi hastalıklarla ilişkili?
        for cond in entry.get('associated_conditions', []):
            c_name = cond['condition_name']
            
            # Bizim datasetlerimizden biri mi?
            for ds_key, ds_pattern in DISEASE_MAP.items():
                if ds_pattern.lower() in c_name.lower():
                    
                    # ML sonuçlarımızda (Top-100) bu Pathway'ler var mı?
                    df_ds_ml = df_ml[df_ml['Dataset'] == ds_key]
                    
                    for cp in clinical_pathways:
                        # ML Sonuçlarında (Feat sütunu) tam eşleşme ara
                        match = df_ds_ml[df_ds_ml['Feat'] == cp]
                        
                        if not match.empty:
                            best_m = match.sort_values('Imp', ascending=False).iloc[0]
                            validation_hits.append({
                                "Dataset": ds_key,
                                "Clinical_Marker": entry['marker_name'],
                                "HMDB": entry['hmdb_id'],
                                "Validated_Pathway": cp,
                                "ML_Method": best_m['Method'],
                                "ML_Importance": best_m['Imp']
                            })

    # 5. KAYIT VE RAPOR
    # -------------------------------------------------------------------------
    if validation_hits:
        res_df = pd.DataFrame(validation_hits).drop_duplicates()
        res_df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ BAŞARI! {len(res_df)} klinik-pathway eşleşmesi mühürlendi.")
        print(f"📊 Dataset bazlı Hit sayıları:\n{res_df['Dataset'].value_counts()}")
        print(f"📁 Rapor: {OUTPUT_CSV}")
    else:
        print("\n❌ Hiç eşleşme bulunamadı. Pathway isimlerinin Recon3D ile aynı olduğundan emin olun.")

if __name__ == "__main__":
    run_ultimate_pathway_validation()