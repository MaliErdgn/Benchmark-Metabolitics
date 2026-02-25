import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import os

# =============================================================================
# YAPILANDIRMA
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
    
    print("="*120)
    print("      ULTIMATE ML MODEL AUDIT: ARCHITECTURAL ROBUSTNESS & EFFICIENCY")
    print("="*120)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)

    # 1. GLOBAL PERFORMANS VE STABİLİTE
    # -------------------------------------------------------------------------
    print("\n[1] GLOBAL MODEL RANKING (Success vs. Reliability)")
    model_stats = df.groupby('ML_Model')[metrics].agg(['mean', 'std', 'median', 'min'])
    model_stats[('F1_Mean', 'CV')] = model_stats[('F1_Mean', 'std')] / model_stats[('F1_Mean', 'mean')]
    print(model_stats.sort_values(by=('F1_Mean', 'mean'), ascending=False))

    # 2. DENSITY RESILIENCE (Gürültü Bağışıklığı Testi)
    # -------------------------------------------------------------------------
    print("\n[2] DENSITY RESILIENCE: HOW MODELS HANDLE FEATURE OVERLOAD (Mean F1)")
    # %10'dan Full'e kadar olan seyreltme etkisi
    density_order = ['10', '20', 'p05', '50', 'Full']
    dens_pivot = df.pivot_table(index='ML_Model', columns='ML_Density', values='F1_Mean', aggfunc='mean')
    
    # Mevcut olanları sırala
    existing_dens = [d for d in density_order if d in dens_pivot.columns]
    dens_pivot = dens_pivot[existing_dens]
    
    # Noise Sensitivity: Full vs 10% farkı (Negatifse model zehirleniyor demektir)
    if '10' in dens_pivot.columns and 'Full' in dens_pivot.columns:
        dens_pivot['Noise_Sensitivity_Delta'] = dens_pivot['Full'] - dens_pivot['10']
    
    print(dens_pivot.sort_values('Noise_Sensitivity_Delta', ascending=False))

    # 3. RESOLUTION SYNERGY (Boyut İndirgeme Tepkisi)
    # -------------------------------------------------------------------------
    print("\n[3] RESOLUTION ADAPTABILITY: REACTION (10k) VS. PATHWAY_MIN (106)")
    res_pivot = df.pivot_table(index='ML_Model', columns='Resolution', values='F1_Mean', aggfunc='mean')
    if 'Reaction' in res_pivot.columns and 'Pathway_min' in res_pivot.columns:
        res_pivot['Pathway_Advantage_Abs'] = res_pivot['Pathway_min'] - res_pivot['Reaction']
        print(res_pivot[['Reaction', 'Pathway_min', 'Pathway_Advantage_Abs']].sort_values('Pathway_Advantage_Abs', ascending=False))

    # 4. PARETO FRONTIER: TRAINING TIME VS PERFORMANCE
    # -------------------------------------------------------------------------
    print("\n[4] ARCHITECTURAL EFFICIENCY (Training Cost vs. F1)")
    time_stats = df.groupby('ML_Model').agg({
        'F1_Mean': 'mean',
        'ML_Duration_CV_Sec': 'mean'
    }).sort_values('F1_Mean', ascending=False)
    print(time_stats)

    # 5. İSTATİSTİKSEL ANLAMLILIK (Modeller Arası Wilcoxon)
    # -------------------------------------------------------------------------
    print("\n[5] PAIRWISE SIGNIFICANCE MATRIX (P-Values)")
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

    print("\n" + "="*120)
    print("      AUDIT COMPLETE: Please provide the results for 3.3 discussion drafting.")
    print("="*120)

if __name__ == "__main__":
    run_exhaustive_model_audit()