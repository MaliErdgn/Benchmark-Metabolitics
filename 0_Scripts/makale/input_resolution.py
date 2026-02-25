import pandas as pd
import numpy as np
import os

# =============================================================================
# YOLLAR
# =============================================================================
FEAT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"
BENCHMARK_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_dual_level_input_audit():
    print("🔬 Dual-Level Input Composition Audit Starting...")
    
    df_feat = pd.read_csv(FEAT_FILE, low_memory=False)
    df_feat['Is_Cr'] = df_feat['Feat'].str.startswith('Coeff_')
    
    # 1. REACTION LEVEL: NOISE FILTERING (10,600 features)
    # -------------------------------------------------------------------------
    print("\n[1] REACTION LEVEL ANALYSIS (Target: Precision in 10k space)")
    reac_feats = df_feat[df_feat['Res'] == 'Reaction']
    reac_usage = reac_feats.groupby(['Dataset', 'Method'])['Is_Cr'].mean() * 100
    print("Mean Cr Usage % at Reaction Level (Top-100):")
    print(reac_usage.groupby('Dataset').mean())

    # 2. PATHWAY LEVEL: INFORMATION DUALITY (106 features)
    # -------------------------------------------------------------------------
    print("\n[2] PATHWAY LEVEL ANALYSIS (Target: Representational Choice)")
    # Burada 'Top-100' demek zaten 'Tüm Liste' demek. 
    # Bakalım model 106 yol için Flux mı seçti yoksa Cr mi?
    path_feats = df_feat[df_feat['Res'].str.contains('Pathway', na=False)]
    path_usage = path_feats.groupby(['Dataset', 'Method', 'Model'])['Is_Cr'].mean() * 100
    
    print("Mean Cr Preference % at Pathway Level:")
    print(path_usage.groupby('Dataset').mean())

    # 3. KAZANÇ ANALİZİ (Önceki Master Audit'ten Gelen Gerçek Rakamlar)
    # -------------------------------------------------------------------------
    print("\n[3] PERFORMANCE GAIN RECAP (Flux vs Flux+Cr)")
    # Hatırlayalım: Reaction'da gain %0.8 iken, Pathway_median'da %2.29 idi.
    # Bu, 106 özellikli dünyada Cr'nin Flux'tan daha kaliteli bilgi verdiğinin kanıtıdır.
    
    # 4. EN DEĞERLİ "AMAC"LAR (Cr'si Flux'ından daha önemli yollar)
    print("\n[4] TOP PATHWAYS PREFERRED AS COEFFICIENTS (Cr > Flux)")
    path_cr_only = path_feats[path_feats['Is_Cr'] == True]
    print(path_cr_only['Feat'].value_counts().head(10))

if __name__ == "__main__":
    run_dual_level_input_audit()