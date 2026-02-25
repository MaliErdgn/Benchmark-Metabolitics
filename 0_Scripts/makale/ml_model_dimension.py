import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import os

# =============================================================================
# 1. VERİ YÜKLEME
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_exhaustive_model_audit():
    if not os.path.exists(INPUT_FILE):
        print(f"HATA: {INPUT_FILE} bulunamadı.")
        return

    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    models = df['ML_Model'].unique()
    metrics = ['F1_Mean', 'AUC_Mean', 'Acc_Mean']
    
    print("="*100)
    print("      ULTIMATE ML MODEL DIMENSION AUDIT: ROBUSTNESS & EFFICIENCY")
    print("="*100)

    # -------------------------------------------------------------------------
    # ANALİZ 1: GLOBAL MODEL SIRALAMASI
    # -------------------------------------------------------------------------
    print("\n[1] GLOBAL PERFORMANCE RANKING (Mean F1 & Stability)")
    model_stats = df.groupby('ML_Model')[metrics].agg(['mean', 'std', 'median'])
    print(model_stats.sort_values(by=('F1_Mean', 'mean'), ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 2: DENSITY RESILIENCE (En Kritik Analiz: Model x Density)
    # -------------------------------------------------------------------------
    print("\n[2] DENSITY RESILIENCE: HOW MODELS HANDLE FEATURE OVERLOAD (Mean F1)")
    # Sıralı density listesi
    density_order = ['10', '20', 'p05', '50', 'Full']
    dens_pivot = df.pivot_table(index='ML_Model', columns='ML_Density', values='F1_Mean', aggfunc='mean')
    
    # Mevcut sütunları sırala
    existing_dens = [d for d in density_order if d in dens_pivot.columns]
    dens_pivot = dens_pivot[existing_dens]
    
    # Düşüş Analizi: %10'dan Full'e geçişteki performans kaybı
    if '10' in dens_pivot.columns and 'Full' in dens_pivot.columns:
        dens_pivot['Noise_Sensitivity_Delta'] = dens_pivot['Full'] - dens_pivot['10']
    
    print(dens_pivot)

    # -------------------------------------------------------------------------
    # ANALİZ 3: RESOLUTION ADAPTABILITY (Reaction vs. Pathway)
    # -------------------------------------------------------------------------
    print("\n[3] RESOLUTION ADAPTABILITY: REACTION VS. PATHWAY_MIN")
    res_pivot = df.pivot_table(index='ML_Model', columns='Resolution', values='F1_Mean', aggfunc='mean')
    if 'Reaction' in res_pivot.columns and 'Pathway_min' in res_pivot.columns:
        res_pivot['Res_Advantage'] = res_pivot['Pathway_min'] - res_pivot['Reaction']
    print(res_pivot[['Reaction', 'Pathway_min', 'Res_Advantage']])

    # -------------------------------------------------------------------------
    # ANALİZ 4: İSTATİSTİKSEL ANLAMLILIK (Pairwise Wilcoxon)
    # -------------------------------------------------------------------------
    print("\n[4] PAIRWISE SIGNIFICANCE MATRIX (P-Values)")
    group_cols = ['Dataset', 'Obj_Method', 'Resolution', 'Input_Type', 'ML_Selector', 'ML_Density']
    pivot_w = df.pivot_table(index=group_cols, columns='ML_Model', values='F1_Mean').dropna()
    
    p_matrix = pd.DataFrame(index=models, columns=models)
    for m1 in models:
        for m2 in models:
            if m1 == m2: p_matrix.loc[m1, m2] = 1.0
            else:
                _, p = wilcoxon(pivot_w[m1], pivot_w[m2])
                p_matrix.loc[m1, m2] = p
    print(p_matrix.applymap(lambda x: f"{x:.2e}"))

    # -------------------------------------------------------------------------
    # ANALİZ 5: HESAPLAMA MALİYETİ (ML Training Time)
    # -------------------------------------------------------------------------
    print("\n[5] COMPUTATIONAL COST: MEAN TRAINING TIME (CV Duration Sec)")
    time_stats = df.groupby('ML_Model')['ML_Duration_CV_Sec'].agg(['mean', 'std', 'max']).sort_values('mean')
    print(time_stats)

    print("\n" + "="*100)

if __name__ == "__main__":
    run_exhaustive_model_audit()