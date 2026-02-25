import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import os

# =============================================================================
# 1. VERİ YÜKLEME VE ÖN İŞLEME
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_exhaustive_method_audit():
    if not os.path.exists(INPUT_FILE):
        print(f"HATA: {INPUT_FILE} bulunamadı.")
        return

    df = pd.read_csv(INPUT_FILE)
    # Etiket standardizasyonu
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    methods = df['Obj_Method'].unique()
    metrics = ['F1_Mean', 'AUC_Mean', 'Acc_Mean']
    baseline = 'baseline_base'
    
    print("="*120)
    print("      ULTIMATE OBJECTIVE FUNCTION AUDIT: 20 METHODS EXHAUSTIVE ANALYSIS")
    print("="*120)

    # -------------------------------------------------------------------------
    # ANALİZ 1: GLOBAL SIRALAMA VE RİSK ANALİZİ
    # -------------------------------------------------------------------------
    print("\n[1] GLOBAL PERFORMANCE & STABILITY (Ranked by Mean F1)")
    stats = df.groupby('Obj_Method')[metrics].agg(['mean', 'std', 'median', 'min', 'max'])
    # CV (Coefficient of Variation) - Düşük olması 'İstikrar' (Robustness) kanıtıdır.
    stats[('F1_Mean', 'CV')] = stats[('F1_Mean', 'std')] / stats[('F1_Mean', 'mean')]
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats.sort_values(by=('F1_Mean', 'mean'), ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 2: RESOLUTION SYNERGY (Hangi metot hangi seviyede devleşiyor?)
    # -------------------------------------------------------------------------
    print("\n[2] RESOLUTION SYNERGY: REACTION VS. PATHWAY_MIN (Mean F1)")
    res_pivot = df.pivot_table(index='Obj_Method', columns='Resolution', values='F1_Mean', aggfunc='mean')
    # Reaction ve Pathway_min arasındaki fark (Sinyal toplulaştırma kazancı)
    if 'Reaction' in res_pivot.columns and 'Pathway_min' in res_pivot.columns:
        res_pivot['Agg_Gain_Abs'] = res_pivot['Pathway_min'] - res_pivot['Reaction']
    print(res_pivot[['Reaction', 'Pathway_min', 'Agg_Gain_Abs']].sort_values('Pathway_min', ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 3: İSTATİSTİKSEL ÜSTÜNLÜK (Her Metot vs. Baseline)
    # -------------------------------------------------------------------------
    print("\n[3] STATISTICAL SIGNIFICANCE VS. BASELINE (Wilcoxon Signed-Rank)")
    group_cols = ['Dataset', 'Resolution', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density']
    pivot_w = df.pivot_table(index=group_cols, columns='Obj_Method', values='F1_Mean').dropna()
    
    sig_results = []
    for m in methods:
        if m == baseline: continue
        stat, p = wilcoxon(pivot_w[m], pivot_w[baseline])
        # Cohen's d benzeri etki büyüklüğü (W / n_pairs)
        mean_diff = (pivot_w[m] - pivot_w[baseline]).mean()
        sig_results.append({
            "Method": m, 
            "P-Value": p, 
            "Mean_Delta_vs_Base": mean_diff,
            "Significant": "YES" if p < 0.05 else "NO"
        })
    
    print(pd.DataFrame(sig_results).sort_values("P-Value"))

    # -------------------------------------------------------------------------
    # ANALİZ 4: MODEL AGNOSTICISM (Model bağımlılığı analizi)
    # -------------------------------------------------------------------------
    print("\n[4] ARCHITECTURAL SENSITIVITY: F1 ACROSS ML MODELS")
    model_pivot = df.pivot_table(index='Obj_Method', columns='ML_Model', values='F1_Mean', aggfunc='mean')
    # Standart Sapma: Düşük olması, metodun modelden bağımsız (robust) olduğunu gösterir.
    model_pivot['Model_Dependency_Std'] = model_pivot.std(axis=1)
    print(model_pivot.sort_values('Model_Dependency_Std'))

    # -------------------------------------------------------------------------
    # ANALİZ 5: DATASET SPECIALIZATION (Cancer vs. Systemic Specialists)
    # -------------------------------------------------------------------------
    print("\n[5] DISEASE SPECIALISTS: TOP METHOD PER DATASET")
    ds_pivot = df.pivot_table(index='Obj_Method', columns='Dataset', values='F1_Mean', aggfunc='mean')
    for ds in ds_pivot.columns:
        winner = ds_pivot[ds].idxmax()
        val = ds_pivot[ds].max()
        base_val = ds_pivot.loc[baseline, ds]
        print(f"   * {ds:<12}: Winner -> {winner:<20} | F1: {val:.4f} | Improvement vs Base: {val-base_val:+.4f}")

    # -------------------------------------------------------------------------
    # ANALİZ 6: COMPOSITION GAIN (Flux vs. Flux+Coeff etkisi)
    # -------------------------------------------------------------------------
    print("\n[6] INPUT COMPOSITION GAIN per METHOD (Flux vs. Flux+Cr)")
    input_pivot = df.pivot_table(index='Obj_Method', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    input_pivot['Cr_Gain_%'] = ((input_pivot['Flux_plus_Coeff'] - input_pivot['Flux']) / input_pivot['Flux']) * 100
    print(input_pivot.sort_values('Cr_Gain_%', ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 7: COMPUTATIONAL EFFICIENCY FRONTIER
    # -------------------------------------------------------------------------
    print("\n[7] COMPUTATIONAL OVERHEAD AUDIT (Simulation vs. ML Cost)")
    cost_stats = df.groupby('Obj_Method').agg({
        'F1_Mean': 'mean',
        'P1_Total_Duration_Sec': 'mean',
        'P1_Memory_Median_MB': 'mean'
    }).sort_values('P1_Total_Duration_Sec')
    print(cost_stats)

    # -------------------------------------------------------------------------
    # ANALİZ 8: WINNER SHARES (Frequency Analysis)
    # -------------------------------------------------------------------------
    print("\n[8] WINNER SHARES (Frequency of being #1 in individual configurations)")
    idx = df.groupby(group_cols)['F1_Mean'].idxmax()
    winners = df.loc[idx, 'Obj_Method'].value_counts()
    print(winners)

    print("\n" + "="*120)
    print("      AUDIT COMPLETE: Please provide the results for comprehensive discussion drafting.")
    print("="*120)

if __name__ == "__main__":
    run_exhaustive_method_audit()