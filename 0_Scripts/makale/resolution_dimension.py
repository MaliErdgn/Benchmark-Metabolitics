import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import os

# =============================================================================
# 1. VERİ YÜKLEME VE ÖN İŞLEME
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_exhaustive_resolution_audit():
    if not os.path.exists(INPUT_FILE):
        print(f"HATA: {INPUT_FILE} bulunamadı.")
        return

    df = pd.read_csv(INPUT_FILE)
    # Etiket standardizasyonu
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    resolutions = df['Resolution'].unique()
    metrics = ['F1_Mean', 'AUC_Mean', 'Acc_Mean']
    datasets = df['Dataset'].unique()
    
    print("="*100)
    print("      ULTIMATE RESOLUTION DIMENSION AUDIT: EXHAUSTIVE STATISTICAL REPORT")
    print("="*100)

    # -------------------------------------------------------------------------
    # ANALİZ 1: GLOBAL BETİMSEL İSTATİSTİKLER (Performans ve Stabilite)
    # -------------------------------------------------------------------------
    print("\n[1] GLOBAL DESCRIPTIVE STATISTICS & VOLATILITY")
    desc_stats = df.groupby('Resolution')[metrics].agg(['mean', 'median', 'std', 'min', 'max'])
    # Varyasyon Katsayısı (CV) - Stabilite ölçüsü (Std / Mean)
    for m in metrics:
        desc_stats[(m, 'CV')] = desc_stats[(m, 'std')] / desc_stats[(m, 'mean')]
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(desc_stats.sort_values(by=('F1_Mean', 'mean'), ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 2: HASTALIK BAZLI PERFORMANS MATRİSİ
    # -------------------------------------------------------------------------
    print("\n[2] DISEASE-SPECIFIC MEAN F1 PERFORMANCE")
    ds_pivot = df.pivot_table(index='Resolution', columns='Dataset', values='F1_Mean', aggfunc='mean')
    ds_pivot['Global_Rank'] = ds_pivot.mean(axis=1).rank(ascending=False)
    print(ds_pivot.sort_values('Global_Rank'))

    # -------------------------------------------------------------------------
    # ANALİZ 3: İSTATİSTİKSEL ANLAMLILIK (Pairwise Wilcoxon Signed-Rank)
    # -------------------------------------------------------------------------
    print("\n[3] PAIRWISE SIGNIFICANCE MATRIX (P-Values)")
    # Eşleştirilmiş test için kontrol kolonları
    group_cols = ['Dataset', 'Obj_Method', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density']
    pivot_wilcoxon = df.pivot_table(index=group_cols, columns='Resolution', values='F1_Mean').dropna()
    
    p_matrix = pd.DataFrame(index=resolutions, columns=resolutions)
    for r1 in resolutions:
        for r2 in resolutions:
            if r1 == r2: p_matrix.loc[r1, r2] = 1.0
            else:
                _, p = wilcoxon(pivot_wilcoxon[r1], pivot_wilcoxon[r2])
                p_matrix.loc[r1, r2] = p
    print(p_matrix.applymap(lambda x: f"{x:.2e}"))

    # -------------------------------------------------------------------------
    # ANALİZ 4: MODEL SİNERJİSİ (Hangi çözünürlük hangi modelle devleşiyor?)
    # -------------------------------------------------------------------------
    print("\n[4] INTERACTION: RESOLUTION x ML MODEL (Mean F1)")
    model_pivot = df.pivot_table(index='Resolution', columns='ML_Model', values='F1_Mean', aggfunc='mean')
    # Fark (Max Model - Min Model) - Model hassasiyeti
    model_pivot['Model_Sensitivity'] = model_pivot.max(axis=1) - model_pivot.min(axis=1)
    print(model_pivot)

    # -------------------------------------------------------------------------
    # ANALİZ 5: BİLGİ KAZANCI (Input Type: Flux vs Flux+Coeff)
    # -------------------------------------------------------------------------
    print("\n[5] INPUT COMPOSITION IMPACT (Information Gain %)")
    input_pivot = df.pivot_table(index='Resolution', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    input_pivot['Gain_%'] = ((input_pivot['Flux_plus_Coeff'] - input_pivot['Flux']) / input_pivot['Flux']) * 100
    print(input_pivot)

    # -------------------------------------------------------------------------
    # ANALİZ 6: HESAPLAMA MALİYETİ (HPC ve ML Aşamaları)
    # -------------------------------------------------------------------------
    print("\n[6] COMPUTATIONAL COST AUDIT (Time & Memory)")
    cost_stats = df.groupby('Resolution').agg({
        'P1_Total_Duration_Sec': 'mean',
        'ML_Duration_CV_Sec': 'mean',
        'P1_Memory_Median_MB': 'mean'
    })
    print(cost_stats)

    # -------------------------------------------------------------------------
    # ANALİZ 7: KAZANMA ANALİZİ (Winner Shares)
    # -------------------------------------------------------------------------
    print("\n[7] WINNER SHARES (How often each resolution is #1)")
    # Her bir deney grubunda kazanan çözünürlüğü bul
    idx = df.groupby(group_cols)['F1_Mean'].idxmax()
    winners = df.loc[idx, 'Resolution'].value_counts()
    print("Global Winner Frequency (Out of 9600 configurations):")
    print(winners)

    print("\n" + "="*100)
    print("      AUDIT COMPLETE: Please provide these numbers for deep interpretation.")
    print("="*100)

if __name__ == "__main__":
    run_exhaustive_resolution_audit()