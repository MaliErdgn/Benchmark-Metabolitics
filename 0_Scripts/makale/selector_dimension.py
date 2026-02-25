import pandas as pd
import numpy as np
from scipy.stats import wilcoxon, friedmanchisquare
import itertools
import os

# =============================================================================
# MASTER CONFIGURATION
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"
DENSITIES = ['10', '20', 'p05', '50', 'Full']
SELECTORS = ['ANOVA', 'Wilcoxon']
MODELS = ['RF', 'XGB', 'LR', 'SVM']
METRICS = ['F1_Mean', 'AUC_Mean', 'Acc_Mean', 'Sens_Mean', 'Spec_Mean']

def run_ultimate_feature_selection_audit():
    print("🚀 ULTIMATE INTELLIGENCE ENGINE V5: FEATURE SELECTION STRATEGY AUDIT")
    print("="*130)
    
    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    # -------------------------------------------------------------------------
    # ANALİZ 1: GLOBAL HİYERARŞİ (Selector x Density Matrix)
    # -------------------------------------------------------------------------
    print("\n[1] GLOBAL PERFORMANCE LANDSCAPE (Mean F1-Score)")
    global_matrix = df.pivot_table(index='ML_Selector', columns='ML_Density', values='F1_Mean', aggfunc='mean')[DENSITIES]
    print(global_matrix)
    
    # -------------------------------------------------------------------------
    # ANALİZ 2: STABİLİTE VE RİSK AUDIT (CV & Std Dev)
    # -------------------------------------------------------------------------
    print("\n[2] STABILITY & VOLATILITY AUDIT (Coefficient of Variation %)")
    stability = df.groupby(['ML_Selector', 'ML_Density'])['F1_Mean'].agg(['mean', 'std'])
    stability['CV_%'] = (stability['std'] / stability['mean']) * 100
    print(stability.unstack()[['CV_%']])

    # -------------------------------------------------------------------------
    # ANALİZ 3: MODEL SİNERJİSİ (Model x Selector x Density) - TRIPLE INTERACTION
    # -------------------------------------------------------------------------
    print("\n[3] TRIPLE INTERACTION: MODEL x SELECTOR x DENSITY (The Optimization Sweet Spot)")
    triple_pivot = df.pivot_table(index=['ML_Model', 'ML_Selector'], columns='ML_Density', values='F1_Mean', aggfunc='mean')[DENSITIES]
    # En iyi kombinasyonu bulalım
    best_comb = triple_pivot.stack().idxmax()
    print(triple_pivot)
    print(f"\n🏆 GLOBAL OPTIMIZATION PEAK: Model={best_comb[0]}, Selector={best_comb[1]}, Density={best_comb[2]} (F1: {triple_pivot.stack().max():.4f})")

    # -------------------------------------------------------------------------
    # ANALİZ 4: STATISTICAL DOMINANCE (Wilcoxon Signed-Rank across all subgroups)
    # -------------------------------------------------------------------------
    print("\n[4] PAIRWISE STATISTICAL DOMINANCE (Wilcoxon)")
    group_cols = ['Dataset', 'Obj_Method', 'Resolution', 'Input_Type', 'ML_Model', 'ML_Density']
    pivot_w = df.pivot_table(index=group_cols, columns='ML_Selector', values='F1_Mean').dropna()
    
    stat, p = wilcoxon(pivot_w['Wilcoxon'], pivot_w['ANOVA'])
    w_wins = sum(pivot_w['Wilcoxon'] > pivot_w['ANOVA'])
    a_wins = sum(pivot_w['ANOVA'] > pivot_w['Wilcoxon'])
    
    print(f"   Wilcoxon vs. ANOVA Overall: p-value = {p:.2e}")
    print(f"   Win Count: Wilcoxon ({w_wins}) vs. ANOVA ({a_wins})")

    # -------------------------------------------------------------------------
    # ANALİZ 5: DENSITY DECAY & NOISE TOLERANCE (The Curse of Dimensionality)
    # -------------------------------------------------------------------------
    print("\n[5] NOISE TOLERANCE: PERFORMANCE DROP FROM 10% TO FULL")
    # Her model ve her selector için %10'dan Full'e geçişteki kayıp
    decay_pivot = df.pivot_table(index=['ML_Model', 'ML_Selector'], columns='ML_Density', values='F1_Mean', aggfunc='mean')
    decay_pivot['Decay_10_to_Full'] = decay_pivot['Full'] - decay_pivot['10']
    print(decay_pivot[['10', 'Full', 'Decay_10_to_Full']].sort_values('Decay_10_to_Full'))

    # -------------------------------------------------------------------------
    # ANALİZ 6: BIAS AUDIT (Sensitivity vs. Specificity Trade-off)
    # -------------------------------------------------------------------------
    print("\n[6] BIAS AUDIT: DOES SELECTION STRATEGY PREFER SENSITIVITY OR SPECIFICITY?")
    bias_stats = df.groupby(['ML_Selector', 'ML_Density'])[['Sens_Mean', 'Spec_Mean']].mean()
    bias_stats['Sens_Spec_Gap'] = bias_stats['Sens_Mean'] - bias_stats['Spec_Mean']
    print(bias_stats.unstack()[['Sens_Spec_Gap']])

    # -------------------------------------------------------------------------
    # ANALİZ 7: COMPUTATIONAL PARETO (Hız vs. Başarı Kazancı)
    # -------------------------------------------------------------------------
    print("\n[7] COMPUTATIONAL EFFICIENCY: SPEEDUP VS. ACCURACY")
    efficiency = df.groupby('ML_Density').agg({'F1_Mean': 'mean', 'ML_Duration_CV_Sec': 'mean'})
    full_time = efficiency.loc['Full', 'ML_Duration_CV_Sec']
    efficiency['Speedup_Factor'] = full_time / efficiency['ML_Duration_CV_Sec']
    print(efficiency.reindex(DENSITIES))

    # -------------------------------------------------------------------------
    # ANALİZ 8: RESOLUTION DEPENDENCY (Özellik sayısı azaldıkça Resolution'ın önemi artıyor mu?)
    # -------------------------------------------------------------------------
    print("\n[8] RESOLUTION x DENSITY INTERACTION (Does Sparsity mask Resolution effects?)")
    res_dens_pivot = df.pivot_table(index='Resolution', columns='ML_Density', values='F1_Mean', aggfunc='mean')[DENSITIES]
    print(res_dens_pivot)

    # -------------------------------------------------------------------------
    # ANALİZ 9: DATASET-LEVEL STRATEGY PREFERENCE
    # -------------------------------------------------------------------------
    print("\n[9] DISEASE-SPECIFIC WINNING STRATEGIES (Best Selector+Density per Disease)")
    df['Strategy'] = df['ML_Selector'] + "_" + df['ML_Density']
    ds_strat_pivot = df.pivot_table(index='Strategy', columns='Dataset', values='F1_Mean', aggfunc='mean')
    for ds in ds_strat_pivot.columns:
        best_strat = ds_strat_pivot[ds].idxmax()
        print(f"   * {ds:<12}: Best Strategy -> {best_strat:<15} (F1: {ds_strat_pivot[ds].max():.4f})")

    # -------------------------------------------------------------------------
    # ANALİZ 10: RANKING MIGRATION (Density değiştikçe metot sıralaması değişiyor mu?)
    # -------------------------------------------------------------------------
    print("\n[10] RANKING STABILITY: DO OBJECTIVE FUNCTIONS CHANGE RANKS ACROSS DENSITIES?")
    # %10 Density'deki Top 3 metodun 'Full' Density'deki sıralaması
    top3_methods_10 = df[df['ML_Density'] == '10'].groupby('Obj_Method')['F1_Mean'].mean().nlargest(3).index.tolist()
    full_ranking = df[df['ML_Density'] == 'Full'].groupby('Obj_Method')['F1_Mean'].mean().rank(ascending=False)
    print(f"Ranks of 10% Top-3 Methods when tested at 100% (Full) Density:")
    for m in top3_methods_10:
        print(f"   - {m:<20}: Rank at 100% = {full_ranking[m]:.0f}")

    print("\n" + "="*130)
    print("      AUDIT COMPLETE: All strategic patterns de-noised.")
    print("="*130)

if __name__ == "__main__":
    run_ultimate_feature_selection_audit()