import pandas as pd
import numpy as np
import os

# =============================================================================
# 1. VERİ YÜKLEME VE HAZIRLIK
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_global_failure_audit():
    if not os.path.exists(INPUT_FILE):
        print(f"HATA: {INPUT_FILE} bulunamadı.")
        return

    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    methods = df['Obj_Method'].unique()
    # Analiz edilecek boyutlar
    audit_dims = ['Resolution', 'ML_Model', 'Input_Type', 'ML_Selector', 'ML_Density']
    
    print("="*130)
    print("      GLOBAL METHOD RELIABILITY & FAILURE MODE AUDIT (FMEA): ALL 20 OBJECTIVE FUNCTIONS")
    print("="*130)

    master_audit_results = []

    for m in methods:
        m_df = df[df['Obj_Method'] == m].copy()
        m_mean = m_df['F1_Mean'].mean()
        m_std = m_df['F1_Mean'].std()
        m_min = m_df['F1_Mean'].min()
        
        # --- Her Metot İçin Boyut Bazlı Zayıflık Analizi ---
        dim_report = {}
        for d in audit_dims:
            dim_stats = m_df.groupby(d)['F1_Mean'].mean().sort_values()
            worst_level = dim_stats.index[0]
            best_level = dim_stats.index[-1]
            
            # Bu boyuttaki düşüş (Hassasiyet)
            drop_impact = m_mean - dim_stats.iloc[0]
            
            dim_report[d] = {
                "Worst": worst_level,
                "Best": best_level,
                "Drop": drop_impact
            }

        # --- En Kritik Zayıflığı Bul (Aşil Topuğu) ---
        toxic_dim = max(dim_report, key=lambda x: dim_report[x]['Drop'])
        
        master_audit_results.append({
            "Method": m,
            "Global_Mean": m_mean,
            "Stability_Std": m_std,
            "Worst_Case_F1": m_min,
            "Toxic_Dimension": toxic_dim,
            "Toxic_Level": dim_report[toxic_dim]['Worst'],
            "Strongest_Level": dim_report[toxic_dim]['Best'],
            "Max_Drop_Impact": dim_report[toxic_dim]['Drop']
        })

    # -------------------------------------------------------------------------
    # 2. RAPORLAMA VE ANALİZ
    # -------------------------------------------------------------------------
    audit_df = pd.DataFrame(master_audit_results).sort_values('Global_Mean', ascending=False)
    
    print(f"\n[1] RELIABILITY SCORECARD (Sorted by Global Mean)")
    print("-" * 130)
    print(audit_df[['Method', 'Global_Mean', 'Stability_Std', 'Worst_Case_F1', 'Toxic_Dimension', 'Toxic_Level']].to_string(index=False))
    
    print(f"\n[2] CROSS-METHOD FAILURE SYNDROMES (Hangi boyut kimleri yakıyor?)")
    print("-" * 130)
    print(audit_df['Toxic_Dimension'].value_counts())

    # --- SENSITIVITY GROUPING ---
    print(f"\n[3] MODEL-DEPENDENCY ANALYSIS (Linear vs. Non-Linear Sensitivity)")
    model_sens = df.pivot_table(index='Obj_Method', columns='ML_Model', values='F1_Mean', aggfunc='mean')
    # Doğrusal (LR) ile En Güçlü (XGB/RF) arasındaki fark
    model_sens['Architectural_Gap'] = model_sens[['RF', 'XGB']].max(axis=1) - model_sens['LR']
    print(model_sens[['LR', 'RF', 'XGB', 'Architectural_Gap']].sort_values('Architectural_Gap', ascending=False))

    # --- RESOLUTION CONFLICTS ---
    print(f"\n[4] RESOLUTION CONFLICT ANALYSIS (Reaction vs. Pathway_min Gap)")
    res_gap = df.pivot_table(index='Obj_Method', columns='Resolution', values='F1_Mean', aggfunc='mean')
    if 'Reaction' in res_gap.columns and 'Pathway_min' in res_gap.columns:
        res_gap['Resolution_Gap'] = res_gap['Pathway_min'] - res_gap['Reaction']
        print(res_gap[['Reaction', 'Pathway_min', 'Resolution_Gap']].sort_values('Resolution_Gap'))

    print("\n" + "="*130)
    print("      AUDIT COMPLETE: All methods analyzed for structural failure modes.")
    print("="*130)

if __name__ == "__main__":
    run_global_failure_audit()