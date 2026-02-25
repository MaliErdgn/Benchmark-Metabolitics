import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
import os

# =============================================================================
# YAPILANDIRMA
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_exhaustive_input_composition_audit():
    if not os.path.exists(INPUT_FILE):
        print(f"HATA: {INPUT_FILE} bulunamadı.")
        return

    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    input_types = df['Input_Type'].unique()
    metrics = ['F1_Mean', 'AUC_Mean', 'Acc_Mean']
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    
    print("="*120)
    print("      ULTIMATE INPUT COMPOSITION AUDIT: FLUX vs. FLUX + COEFFICIENTS (Cr)")
    print("="*120)

    # -------------------------------------------------------------------------
    # ANALİZ 1: GLOBAL BİLGİ KAZANCI (OVERALL INFORMATION GAIN)
    # -------------------------------------------------------------------------
    print("\n[1] GLOBAL PERFORMANCE COMPARISON")
    global_stats = df.groupby('Input_Type')[metrics].agg(['mean', 'std', 'median'])
    # Kazanç Yüzdesi Hesapla
    f1_gain = ((global_stats.loc['Flux_plus_Coeff', ('F1_Mean', 'mean')] - 
                global_stats.loc['Flux', ('F1_Mean', 'mean')]) / 
               global_stats.loc['Flux', ('F1_Mean', 'mean')]) * 100
    
    print(global_stats)
    print(f"\n🚀 GLOBAL INFORMATION GAIN (F1): {f1_gain:.2f}%")

    # -------------------------------------------------------------------------
    # ANALİZ 2: RESOLUTION-DRIVEN GAIN (Çözünürlük bazlı kazanç analizi)
    # -------------------------------------------------------------------------
    print("\n[2] GAIN BY BIOLOGICAL RESOLUTION (The Aggregation Effect)")
    res_pivot = df.pivot_table(index='Resolution', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    res_pivot['Gain_Abs'] = res_pivot['Flux_plus_Coeff'] - res_pivot['Flux']
    res_pivot['Gain_%'] = (res_pivot['Gain_Abs'] / res_pivot['Flux']) * 100
    print(res_pivot.sort_values('Gain_%', ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 3: MODEL-DRIVEN GAIN (Hangi model Cr katsayısını daha iyi anlıyor?)
    # -------------------------------------------------------------------------
    print("\n[3] GAIN BY ML ARCHITECTURE (Who benefits most from Cr?)")
    model_pivot = df.pivot_table(index='ML_Model', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    model_pivot['Gain_%'] = ((model_pivot['Flux_plus_Coeff'] - model_pivot['Flux']) / model_pivot['Flux']) * 100
    print(model_pivot.sort_values('Gain_%', ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 4: METHOD-DRIVEN GAIN (Hangi metot Cr ile daha uyumlu?)
    # -------------------------------------------------------------------------
    print("\n[4] GAIN BY OBJECTIVE FUNCTION FAMILY")
    # Metotları ailelere bölelim
    def get_family(m):
        if 'local' in m: return 'Topological'
        if 'robust' in m: return 'Statistical'
        if 'atp' in m or 'biomass' in m: return 'Biological'
        return 'Global'
    
    df['Method_Family'] = df['Obj_Method'].apply(get_family)
    method_pivot = df.pivot_table(index='Method_Family', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    method_pivot['Gain_%'] = ((method_pivot['Flux_plus_Coeff'] - method_pivot['Flux']) / method_pivot['Flux']) * 100
    print(method_pivot.sort_values('Gain_%', ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 5: DATASET-SPECIFIC GAIN (Hangi hastalıkta Cr daha kritik?)
    # -------------------------------------------------------------------------
    print("\n[5] GAIN BY DISEASE DATASET")
    ds_pivot = df.pivot_table(index='Dataset', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    ds_pivot['Gain_%'] = ((ds_pivot['Flux_plus_Coeff'] - ds_pivot['Flux']) / ds_pivot['Flux']) * 100
    print(ds_pivot.sort_values('Gain_%', ascending=False))

    # -------------------------------------------------------------------------
    # ANALİZ 6: İSTATİSTİKSEL ANLAMLILIK (Wilcoxon Signed-Rank)
    # -------------------------------------------------------------------------
    print("\n[6] STATISTICAL SIGNIFICANCE (Flux vs. Flux+Cr)")
    group_cols = ['Dataset', 'Obj_Method', 'Resolution', 'ML_Model', 'ML_Selector', 'ML_Density']
    pivot_w = df.pivot_table(index=group_cols, columns='Input_Type', values='F1_Mean').dropna()
    
    stat, p = wilcoxon(pivot_w['Flux_plus_Coeff'], pivot_w['Flux'])
    print(f"Wilcoxon Statistic: {stat:.2f}")
    print(f"P-Value: {p:.2e}")
    print(f"Significant: {'YES' if p < 0.05 else 'NO'}")

    # -------------------------------------------------------------------------
    # ANALİZ 7: WINNER SHARES (Katsayı kaç kez kazandı?)
    # -------------------------------------------------------------------------
    print("\n[7] COMPETITIVE EDGE (Winner Frequency)")
    idx = df.groupby(group_cols)['F1_Mean'].idxmax()
    winners = df.loc[idx, 'Input_Type'].value_counts()
    print(winners)

    print("\n" + "="*120)
    print("      AUDIT COMPLETE: Provide results to finalize Section 3.4 drafting.")
    print("="*120)

if __name__ == "__main__":
    run_exhaustive_input_composition_audit()