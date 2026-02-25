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
    stats = df.groupby('Obj_Method')[metrics].agg(['mean', 'std', 'median'])
    stats[('F1_Mean', 'CV')] = stats[('F1_Mean', 'std')] / stats[('F1_Mean', 'mean')]
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats.sort_values(by=('F1_Mean', 'mean'), ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 2: PARETO VERİLERİ (Simulation Cost vs. Performance)
    # -------------------------------------------------------------------------
    print("\n[2] COMPUTATIONAL EFFICIENCY (Pareto Source Data)")
    # P1_Total_Duration_Sec: FVA Süresi | P1_Memory_Median_MB: RAM Kullanımı
    cost_stats = df.groupby('Obj_Method').agg({
        'F1_Mean': 'mean',
        'P1_Total_Duration_Sec': 'mean',
        'P1_Memory_Median_MB': 'mean'
    }).sort_values('P1_Total_Duration_Sec')
    print(cost_stats)

    # -------------------------------------------------------------------------
    # ANALİZ 3: İSTATİSTİKSEL ANLAMLILIK (Her Metot vs. Baseline)
    # -------------------------------------------------------------------------
    print("\n[3] STATISTICAL SIGNIFICANCE VS. BASELINE (P-Values)")
    group_cols = ['Dataset', 'Resolution', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density']
    pivot_w = df.pivot_table(index=group_cols, columns='Obj_Method', values='F1_Mean').dropna()
    
    sig_results = []
    for m in methods:
        if m == baseline: continue
        stat, p = wilcoxon(pivot_w[m], pivot_w[baseline])
        sig_results.append({
            "Method": m, 
            "P-Value": p, 
            "Mean_Delta": (pivot_w[m] - pivot_w[baseline]).mean(),
            "Significant": "YES" if p < 0.05 else "NO"
        })
    print(pd.DataFrame(sig_results).sort_values("P-Value"))

    # -------------------------------------------------------------------------
    # ANALİZ 4: LOCAL k-HOP ANALİZİ (Trend Analizi)
    # -------------------------------------------------------------------------
    print("\n[4] TOPOLOGICAL DEPTH IMPACT (Local k1 to k6)")
    local_methods = [m for m in methods if 'local_k' in m]
    local_stats = stats.loc[sorted(local_methods)]
    print(local_stats[('F1_Mean')])

    print("\n" + "="*120)

if __name__ == "__main__":
    run_exhaustive_method_audit()