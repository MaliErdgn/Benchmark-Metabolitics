import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

# PATH TO YOUR MASTER CSV
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_deep_selector_audit():
    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    print("="*100)
    print("      FORENSIC SELECTOR AUDIT: BEYOND THE MEANS")
    print("="*100)

    # 1. THE "SYNERGY PEAK" LOCATOR
    # Finding the specific model-selector combos that thrive in sparsity vs density
    synergy = df.pivot_table(index=['ML_Model', 'ML_Selector'], 
                            columns='ML_Density', 
                            values='F1_Mean', 
                            aggfunc='mean')
    
    print("\n[1] TRIPLE INTERACTION MATRIX (Model x Selector x Density)")
    print(synergy)

    # 2. THE "SPARSITY RECOVERY" TEST
    # Does Wilcoxon recover the rank of Top Methods better than ANOVA?
    print("\n[2] METHOD RANK RECOVERY (Do Selectors help Objective Functions?)")
    # Rank of 'local_k4' at 10% vs 100% density across different selectors
    for sel in ['ANOVA', 'Wilcoxon']:
        sub = df[df['ML_Selector'] == sel]
        rank_10 = sub[sub['ML_Density'] == '10'].groupby('Obj_Method')['F1_Mean'].mean().rank(ascending=False)['local_k4']
        rank_full = sub[sub['ML_Density'] == 'Full'].groupby('Obj_Method')['F1_Mean'].mean().rank(ascending=False)['local_k4']
        print(f"   Selector: {sel:<10} | local_k4 Rank at 10%: {rank_10:.0f} | Rank at Full: {rank_full:.0f}")

    # 3. BIAS AUDIT (SENSITIVITY VS SPECIFICITY)
    # This tells us if a selector is 'optimistic' or 'pessimistic'
    bias = df.groupby(['ML_Selector', 'ML_Density'])[['Sens_Mean', 'Spec_Mean']].mean()
    bias['Tradeoff_Index'] = bias['Sens_Mean'] / (bias['Spec_Mean'] + 1e-6)
    
    print("\n[3] BIAS AUDIT (Sensitivity/Specificity Ratio)")
    print(bias['Tradeoff_Index'].unstack())

    # 4. DATASET SENSITIVITY
    # Is ANOVA better for Cancer? Is Wilcoxon better for Systemic?
    ds_perf = df.pivot_table(index='Dataset', columns='ML_Selector', values='F1_Mean', aggfunc='mean')
    ds_perf['Wilcoxon_Advantage'] = ds_perf['Wilcoxon'] - ds_perf['ANOVA']
    
    print("\n[4] DISEASE-LEVEL SELECTOR PREFERENCE")
    print(ds_perf.sort_values('Wilcoxon_Advantage', ascending=False))

if __name__ == "__main__":
    run_deep_selector_audit()