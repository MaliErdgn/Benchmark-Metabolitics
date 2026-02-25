import pandas as pd
import numpy as np
import cobra
import os
import glob
import warnings
import difflib

try:
    import mygene
except ImportError:
    print("Hata: mygene kutuphanesi eksik. 'pip install mygene' komutunu calistirin.")
    exit()

warnings.filterwarnings("ignore")

# =============================================================================
# AYARLAR VE DOSYA YOLLARI
# =============================================================================
FEATURES_DIR = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\2_Features"
DEG_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\GSE37751_DEG_Results.csv"
MODEL_PATH = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\Recon3D.json"

TARGET_DATASETS = ["BC", "BRCA", "BRCA-ATLAS"]
TOP_N = 15
FDR_THRESHOLD = 0.05

def normalize_string(s):
    return str(s).lower().strip()

def run_final_pathway_validation():
    print("BASLADI: Pathway-Gene-DEG Validation (Recon3D ID Fix)")
    print("-" * 80)

    # -------------------------------------------------------------------------
    # ADIM 1: RECON3D MODELINI YUKLE
    # -------------------------------------------------------------------------
    print("1. Recon3D Modeli yukleniyor...")
    try:
        model = cobra.io.load_json_model(MODEL_PATH)
    except Exception as e:
        print(f"Hata: Model yuklenemedi: {e}")
        return

    model_pathways = {}
    recon_id_to_entrez = {} 
    
    for r in model.reactions:
        sub = str(r.subsystem)
        if not sub or sub == 'nan' or sub == '': 
            continue
        
        norm_key = normalize_string(sub)
        
        if norm_key not in model_pathways:
            model_pathways[norm_key] = {'original_name': sub, 'recon_ids': set()}
            
        for g in r.genes:
            rid = str(g.id)
            model_pathways[norm_key]['recon_ids'].add(rid)
            # 3081_AT1 veya 3081.1 formatini 3081'e indirger
            entrez = rid.split('_')[0].split('.')[0]
            if entrez.isdigit():
                recon_id_to_entrez[rid] = entrez

    print(f"   -> Modelde {len(model_pathways)} yolak ve {len(recon_id_to_entrez)} gecerli gen ID'si bulundu.")

    # -------------------------------------------------------------------------
    # ADIM 2: MYGENE ILE TOPLU ID DONUSUMU
    # -------------------------------------------------------------------------
    print("\n2. Gen ID donusumu (Entrez -> Symbol)...")
    unique_entrez = list(set(recon_id_to_entrez.values()))
    
    mg = mygene.MyGeneInfo()
    entrez_to_symbol = {}
    
    try:
        query_res = mg.querymany(unique_entrez, scopes='entrezgene', fields='symbol', species='human', as_dataframe=True)
        
        if query_res is not None:
            for idx, row in query_res.iterrows():
                entrez_id = str(idx)
                if 'symbol' in row and pd.notna(row['symbol']):
                    entrez_to_symbol[entrez_id] = str(row['symbol']).upper().strip()
    except Exception as e:
        print(f"   API Hatasi: {e}")

    recon_to_symbol = {}
    for rid, entrez in recon_id_to_entrez.items():
        if entrez in entrez_to_symbol:
            recon_to_symbol[rid] = entrez_to_symbol[entrez]

    print(f"   -> {len(recon_to_symbol)} adet Recon3D geni sembole donusturuldu.")

    # -------------------------------------------------------------------------
    # ADIM 3: FEATURE DOSYALARINI ISLE
    # -------------------------------------------------------------------------
    print("\n3. Feature dosyalari taraniyor...")
    
    try:
        deg_df = pd.read_csv(DEG_FILE)
        deg_df['gene_symbol_upper'] = deg_df['gene_symbol'].astype(str).str.upper().str.strip()
        measured_genes_set = set(deg_df['gene_symbol_upper'])
        sig_genes_set = set(deg_df[deg_df['FDR'] < FDR_THRESHOLD]['gene_symbol_upper'])
    except Exception as e:
        print(f"   DEG Dosya Hatasi: {e}")
        return
    
    all_files = glob.glob(os.path.join(FEATURES_DIR, "FEATURES_*.csv"))
    validation_results = []
    model_subsystems = list(model_pathways.keys())

    for f_path in all_files:
        dataset_name = os.path.basename(f_path).replace("FEATURES_", "").replace(".csv", "")
        if dataset_name not in TARGET_DATASETS: 
            continue
        
        try:
            df = pd.read_csv(f_path, low_memory=False)
            if 'Res' in df.columns:
                # Sadece Pathway sonuclarini al
                df = df[df['Res'].astype(str).str.contains('Pathway', case=False, na=False)]
            if df.empty: 
                continue
            
            df['Imp_Abs'] = df['Imp'].abs()
            
            # Konfigurasyon bazli grupla
            groups = df.groupby(['Method', 'Res', 'Input', 'Sel', 'Dens', 'Model'])
            
            for group_name, group_data in groups:
                # En önemli 15 Yolak
                top_feats = group_data.sort_values('Imp_Abs', ascending=False)['Feat'].unique()[:TOP_N]
                
                exp_symbols = set()
                for feat in top_feats:
                    norm_feat = normalize_string(feat)
                    target_sub = None
                    
                    if norm_feat in model_pathways:
                        target_sub = norm_feat
                    else:
                        match = difflib.get_close_matches(norm_feat, model_subsystems, n=1, cutoff=0.8)
                        if match: 
                            target_sub = match[0]
                    
                    if target_sub:
                        # HATA BURADAYDI, DUZELTILDI:
                        for rid in model_pathways[target_sub]['recon_ids']:
                            if rid in recon_to_symbol:
                                exp_symbols.add(recon_to_symbol[rid])
                
                if not exp_symbols: 
                    continue

                mapped = exp_symbols.intersection(measured_genes_set)
                if not mapped: 
                    continue
                
                sig_hits = mapped.intersection(sig_genes_set)
                overlap_pct = (len(sig_hits) / len(mapped)) * 100
                
                res_entry = {'Dataset': dataset_name}
                # Mevcut gruplama anahtarlarini sozluk yap
                res_entry.update(dict(zip(['Method', 'Res', 'Input', 'Sel', 'Dens', 'Model'], group_name)))
                res_entry.update({
                    'Measured_Genes': len(mapped),
                    'Significant_Genes': len(sig_hits),
                    'Overlap_Percent': round(overlap_pct, 2)
                })
                validation_results.append(res_entry)

        except Exception as e:
            print(f"   Hata ({dataset_name}): {e}")

    # -------------------------------------------------------------------------
    # ADIM 4: RAPORLAMA
    # -------------------------------------------------------------------------
    if validation_results:
        final_df = pd.DataFrame(validation_results).sort_values('Overlap_Percent', ascending=False)
        print("\n" + "="*90)
        print(" TRANSKRIPTOMIK VALIDASYON (MADDE 1a) - TOP 20 CONFIGURATIONS")
        print("="*90)
        
        disp_cols = ['Dataset', 'Method', 'Res', 'Model', 'Overlap_Percent', 'Significant_Genes']
        print(final_df[disp_cols].head(20).to_string(index=False))
        
        final_df.to_csv("Final_Transcriptomic_Validation_Results.csv", index=False)
        print(f"\n✅ Sonuclar 'Final_Transcriptomic_Validation_Results.csv' dosyasina kaydedildi.")
    else:
        print("❌ Sonuç üretilemedi. Eşleşme hatası.")

if __name__ == "__main__":
    run_final_pathway_validation()