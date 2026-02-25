import pandas as pd
import os
import numpy as np

# =============================================================================
# YAPILANDIRMA
# =============================================================================
FEAT_CSV = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"
OUT_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Biomarker_Reports"
os.makedirs(OUT_DIR, exist_ok=True)

def run_ultimate_discovery():
    print("🧬 Ultimate Biomarker & Pathway Discovery Engine Started...")
    
    # Veriyi yükle
    df = pd.read_csv(FEAT_CSV, low_memory=False)
    
    # Kolon eşleme (Feat, Res, Imp, Model, Dataset, Method)
    feat_col = 'Feat' if 'Feat' in df.columns else 'Feature'
    res_col = 'Res' if 'Res' in df.columns else 'Resolution'
    imp_col = 'Imp' if 'Imp' in df.columns else 'Importance'
    method_col = 'Method'
    model_col = 'Model'
    ds_col = 'Dataset'

    # Pathway ve Reaction gruplarını ayır
    # Pathway etiketleri 'Pathway_min', 'Pathway_mean' vb. şeklinde olabileceği için 'Pathway' içerenleri alıyoruz
    df['Level_Group'] = df[res_col].apply(lambda x: 'Pathway' if 'Pathway' in str(x) else 'Reaction')
    
    levels = ['Reaction', 'Pathway']
    
    # -------------------------------------------------------------------------
    # ANALİZ 1: GLOBAL CONSENSUS (REACTION & PATHWAY)
    # -------------------------------------------------------------------------
    print("🔎 Analyzing Global Consensus...")
    with open(os.path.join(OUT_DIR, "1_GLOBAL_CONSENSUS_DETAILED.txt"), "w", encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("      GLOBAL METABOLIC CONSENSUS: REACTION & PATHWAY LEVELS\n")
        f.write("      (Top features ranked by Mean Importance and Selection Frequency)\n")
        f.write("================================================================================\n\n")

        for lvl in levels:
            f.write(f"\n>>>> LEVEL: {lvl.upper()} <<<<\n")
            f.write("="*40 + "\n")
            
            sub_lvl = df[df['Level_Group'] == lvl]
            
            for ds in sub_lvl[ds_col].unique():
                f.write(f"\n--- DISEASE DATASET: {ds} ---\n")
                f.write(f"{'Feature Name':<55} | {'Avg Imp':<10} | {'Selection Count'}\n")
                f.write(f"{'-'*85}\n")
                
                # Consensus Hesabı: Imp ortalaması ve Count (Seçilme sıklığı)
                consensus = sub_lvl[sub_lvl[ds_col] == ds].groupby(feat_col)[imp_col].agg(['mean', 'count'])
                consensus = consensus.sort_values(by=['mean', 'count'], ascending=False).head(20)
                
                for feat, row in consensus.iterrows():
                    f.write(f"{str(feat):<55} | {row['mean']:.4f}    | {int(row['count'])}\n")
                f.write("\n")

    # -------------------------------------------------------------------------
    # ANALİZ 2: METHOD NOVELTY (BASELINE VS ALL OTHERS)
    # -------------------------------------------------------------------------
    print("🔎 Analyzing Method-Specific Novelty...")
    with open(os.path.join(OUT_DIR, "2_METHOD_NOVELTY_COMPREHENSIVE.txt"), "w", encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("      METHOD NOVELTY: WHAT DOES THE BASELINE MISS?\n")
        f.write("      (Features uniquely identified by your new objective functions)\n")
        f.write("================================================================================\n\n")

        for lvl in levels:
            f.write(f"\n>>>> LEVEL: {lvl.upper()} <<<<\n")
            sub_lvl = df[df['Level_Group'] == lvl]
            
            for ds in sub_lvl[ds_col].unique():
                f.write(f"\n>> DATASET: {ds}\n")
                
                # Baseline Seti
                baseline_feats = set(sub_lvl[(sub_lvl[ds_col] == ds) & (sub_lvl[method_col] == 'baseline_base')][feat_col].unique())
                
                for m in sub_lvl[method_col].unique():
                    if 'baseline' in str(m).lower(): continue
                    
                    method_feats = set(sub_lvl[(sub_lvl[ds_col] == ds) & (sub_lvl[method_col] == m)][feat_col].unique())
                    unique_signals = method_feats - baseline_feats
                    
                    if unique_signals:
                        f.write(f"   * Method {str(m):<15}: Found {len(unique_signals)} unique biomarkers.\n")
                        # Bu unique sinyaller içinden en önemli 5 tanesini göster
                        m_top = sub_lvl[(sub_lvl[ds_col] == ds) & (sub_lvl[method_col] == m) & (sub_lvl[feat_col].isin(unique_signals))]
                        m_top_list = m_top.groupby(feat_col)[imp_col].mean().sort_values(ascending=False).head(5).index.tolist()
                        f.write(f"     Key Discoveries: {m_top_list}\n")
                f.write("-" * 50 + "\n")

    # -------------------------------------------------------------------------
    # ANALİZ 3: MODEL STABILITY INDEX
    # -------------------------------------------------------------------------
    print("🔎 Analyzing Model Stability...")
    with open(os.path.join(OUT_DIR, "3_MODEL_STABILITY_INDEX.txt"), "w", encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("      MODEL STABILITY: FEATURE OVERLAP (JACCARD INDEX)\n")
        f.write("================================================================================\n\n")

        models = df[model_col].unique()
        for lvl in levels:
            f.write(f"\n>>>> LEVEL: {lvl.upper()} <<<<\n")
            sub_lvl = df[df['Level_Group'] == lvl]
            
            for ds in sub_lvl[ds_col].unique():
                f.write(f"\n>> Dataset: {ds}\n")
                for i, m1 in enumerate(models):
                    for m2 in models[i+1:]:
                        set1 = set(sub_lvl[(sub_lvl[ds_col] == ds) & (sub_lvl[model_col] == m1)][feat_col].unique())
                        set2 = set(sub_lvl[(sub_lvl[ds_col] == ds) & (sub_lvl[model_col] == m2)][feat_col].unique())
                        
                        if set1 or set2:
                            jaccard = len(set1.intersection(set2)) / len(set1.union(set2))
                            f.write(f"   Stability {m1:<4} <-> {m2:<4}: {jaccard*100:.2f}%\n")
                f.write("\n")

    print(f"\n✅ COMPREHENSIVE DISCOVERY FINISHED. Reports in: {OUT_DIR}")

if __name__ == "__main__":
    run_ultimate_discovery()