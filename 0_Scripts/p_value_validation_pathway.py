import pandas as pd
import json
import os
import re
import numpy as np
from scipy.stats import fisher_exact

# =============================================================================
# 1. KONFİGÜRASYON VE DOSYA YOLLARI
# =============================================================================
BASE_DATA_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data"
JSON_DB_PATH  = os.path.join(BASE_DATA_DIR, "MARKERDB_GLOBAL_DATABASE.json")
MODEL_PATH    = os.path.join(BASE_DATA_DIR, "Recon3D.json")
MAPPING_PATH  = os.path.join(BASE_DATA_DIR, "new-synonym-mapping.json")
ML_FEATURES   = os.path.join(BASE_DATA_DIR, "MASTER_FEATURES_TOP100.csv")

OUTPUT_DIR    = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Statistical_Validation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Filtrelenecek "Currency" Metabolitler (Gürültü önleyici)
# Kaynak: Thiele & Palsson (2010), Recon3D Hub Metabolites
CURRENCY_METS = {
    'atp', 'adp', 'h2o', 'h', 'nad', 'nadh', 'nadp', 'nadph', 
    'pi', 'ppi', 'coa', 'co2', 'o2', 'nh4', 'na1', 'k', 'cl'
}

# Hastalık Eşleşmeleri
DISEASE_MAP = {
    "Alzheimer": ["Alzheimer"],
    "Diabetes": ["Diabetes"],
    "BC": ["Breast Cancer", "Malignant neoplasm of breast"],
    "BRCA": ["Breast Cancer", "BRCA"],
    "PDAC": ["Pancreatic"],
    "PRAD": ["Prostate"]
}

class StatisticalValidationEngine:
    def __init__(self):
        print("🧬 Building Biological Knowledge Base from Recon3D...")
        with open(MODEL_PATH, 'r') as f:
            self.model = json.load(f)
        
        # 1. Recon3D Evrenini İnşa Et (N ve n)
        self.pathway_to_mets = {} # Pathway -> {metabolites}
        self.all_universe_mets = set()
        
        for rxn in self.model['reactions']:
            pathway = rxn.get('subsystem', 'Unknown')
            if pathway not in self.pathway_to_mets:
                self.pathway_to_mets[pathway] = set()
            
            for met_id in rxn['metabolites'].keys():
                # Kompartman ekini temizle ve küçük harf yap
                clean_met = re.sub(r'_[a-z]$', '', met_id).lower().strip()
                
                # Currency Filtresi Uygula
                if clean_met not in CURRENCY_METS:
                    self.pathway_to_mets[pathway].add(clean_met)
                    self.all_universe_mets.add(clean_met)

        self.N = len(self.all_universe_mets)
        print(f"✅ Recon3D Universe: {self.N} unique metabolites (currency filtered) in {len(self.pathway_to_mets)} pathways.")

        # 2. MarkerDB & Mapping Yükle
        with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        self.norm_map = {str(k).lower().strip(): v for k, v in mapping.items()}

        with open(JSON_DB_PATH, 'r', encoding='utf-8') as f:
            self.db = json.load(f)
        
        self.df_ml = pd.read_csv(ML_FEATURES, low_memory=False)

    def run_ora(self):
        print("🧪 Performing Pathway Over-Representation Analysis (ORA)...")
        final_results = []

        for ds_key, patterns in DISEASE_MAP.items():
            print(f"   🔎 Analyzing: {ds_key}")
            
            # 1. Bu hastalık için Klinik Metabolit Setini Kur (K)
            k_clinical_mets = set()
            for entry in self.db:
                cond_names = " ".join([c['condition_name'] for c in entry.get('associated_conditions', [])]).lower()
                if any(p.lower() in cond_names for p in patterns):
                    m_name = str(entry['marker_name']).lower().strip()
                    m_hmdb = str(entry['hmdb_id']).lower().strip() if entry['hmdb_id'] else None
                    
                    rid = self.norm_map.get(m_hmdb) or self.norm_map.get(m_name)
                    if rid:
                        clean_rid = rid.split('_')[0].lower().strip()
                        if clean_rid not in CURRENCY_METS:
                            k_clinical_mets.add(clean_rid)
            
            K_size = len(k_clinical_mets)
            if K_size == 0: continue

            # 2. Her Pathway için Fisher's Exact Test Uygula
            for pathway, path_mets in self.pathway_to_mets.items():
                n_size = len(path_mets)
                if n_size < 3: continue # Çok küçük yolları istatistiksel güven için atla
                
                # Ortak metabolitler (k)
                k_overlap = path_mets.intersection(k_clinical_mets)
                k_count = len(k_overlap)
                
                # Contingency Table:
                # [[k, n-k], [K-k, N-n-K+k]]
                table = [[k_count, n_size - k_count], 
                         [K_size - k_count, self.N - n_size - K_size + k_count]]
                
                odds, p_val = fisher_exact(table, alternative='greater')

                # 3. İstatistiksel Olarak Anlamlıysa, ML Hit Kontrolü Yap
                if p_val < 0.05:
                    # Bu yolu bizim ML modellerimiz bulmuş mu? (Top-100)
                    ml_match = self.df_ml[(self.df_ml['Dataset'] == ds_key) & (self.df_ml['Feat'] == pathway)]
                    
                    is_ml_validated = not ml_match.empty
                    best_imp = ml_match['Imp'].max() if is_ml_validated else 0
                    
                    final_results.append({
                        "Dataset": ds_key,
                        "Pathway": pathway,
                        "P_Value": p_val,
                        "Clinical_Mets_Count": k_count,
                        "Pathway_Size": n_size,
                        "Clinical_Markers": list(k_overlap)[:5], # Örnekler
                        "ML_Validated": is_ml_validated,
                        "Max_ML_Importance": best_imp
                    })

        # 4. RAPORLAMA
        df_res = pd.DataFrame(final_results)
        df_res.to_csv(os.path.join(OUTPUT_DIR, "PATHWAY_ORA_RESULTS.csv"), index=False)
        
        with open(os.path.join(OUTPUT_DIR, "ORA_SUMMARY_REPORT.txt"), "w", encoding="utf-8") as f:
            f.write("=== STATISTICAL PATHWAY VALIDATION (ORA) ===\n\n")
            f.write(f"Parameters: Fisher's Exact Test, Alpha=0.05, Currency Filtered=Yes\n\n")
            
            for ds in df_res['Dataset'].unique():
                f.write(f"--- {ds} ANALYSIS ---\n")
                sub = df_res[df_res['Dataset'] == ds].sort_values('P_Value')
                f.write(f"Total Statistically Significant Pathways: {len(sub)}\n")
                f.write(f"ML Validated (Top-100) Pathways: {sub['ML_Validated'].sum()}\n")
                f.write(f"Top Pathway: {sub.iloc[0]['Pathway']} (p={sub.iloc[0]['P_Value']:.2e})\n")
                f.write("-" * 50 + "\n\n")

        print(f"\n✅ Kapsamlı ORA Analizi Tamamlandı!")
        print(f"📊 Raporlar: {OUTPUT_DIR}")

if __name__ == "__main__":
    engine = StatisticalValidationEngine()
    engine.run_ora()