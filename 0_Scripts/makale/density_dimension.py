import pandas as pd
import numpy as np

# PATH
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_density_ultimate_audit():
    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    # Sort order for density
    d_order = ['10', '20', 'p05', '50', 'Full']
    
    print("="*110)
    print("      ULTIMATE DENSITY STRESS TEST: DIMENSION 7 VS. THE WORLD")
    print("="*110)

    # 1. THE GLOBAL DECAY CURVE
    # Is the paradox a linear decline or a cliff?
    global_dens = df.groupby('ML_Density')['F1_Mean'].agg(['mean', 'std', 'min']).reindex(d_order)
    global_dens['CV_Percent'] = (global_dens['std'] / global_dens['mean']) * 100
    
    print("\n[1] GLOBAL DENSITY DECAY & VOLATILITY")
    print(global_dens)

    # 2. MODEL-SPECIFIC NOISE TOLERANCE (D7 x D5)
    # Measuring the 'Slope' of failure for each architecture
    model_dens = df.pivot_table(index='ML_Model', columns='ML_Density', values='F1_Mean', aggfunc='mean')[d_order]
    model_dens['Total_Decay'] = model_dens['Full'] - model_dens['10']
    
    print("\n[2] ARCHITECTURAL NOISE TOLERANCE (The Failure Slopes)")
    print(model_dens.sort_values('Total_Decay'))

    # 3. THE RESOLUTION SCALE-INVARIANCE TEST (D7 x D3)
    # Does Sparsity matter when you only have 106 features?
    # This distinguishes 'Dimensionality Reduction' from 'Biological Denoising'.
    res_dens = df.pivot_table(index='Resolution', columns='ML_Density', values='F1_Mean', aggfunc='mean')[d_order]
    res_dens['Decay_at_Scale'] = res_dens['Full'] - res_dens['10']
    
    print("\n[3] SCALE-INVARIANCE: IS SPARSITY NECESSARY AT PATHWAY LEVEL?")
    print(res_dens.sort_values('Decay_at_Scale'))

    # 4. METHOD ROBUSTNESS UNDER NOISE (D7 x D2)
    # Which objective functions survive 'Full Density' best?
    # Identifying 'Noise-Resistant' vs 'Noise-Sensitive' Methods
    method_dens = df.pivot_table(index='Obj_Method', columns='ML_Density', values='F1_Mean', aggfunc='mean')[d_order]
    # Filter for top methods to keep output clean
    top_methods = df.groupby('Obj_Method')['F1_Mean'].mean().nlargest(5).index
    
    print("\n[4] METHOD ROBUSTNESS (Top 5 Methods vs Density)")
    print(method_dens.loc[top_methods])

    # 5. INFORMATION RECOVERY CHECK (D7 x D4)
    # Does Cr (Coefficients) help mitigate the noise of Full Density?
    input_dens = df.pivot_table(index='Input_Type', columns='ML_Density', values='F1_Mean', aggfunc='mean')[d_order]
    
    print("\n[5] INPUT COMPOSITION VS. NOISE")
    print(input_dens)

    # 6. THE SELECTOR STABILITY TEST (D7 x D6)
    # Does ANOVA or Wilcoxon handle 'Full Density' better?
    sel_dens = df.pivot_table(index='ML_Selector', columns='ML_Density', values='F1_Mean', aggfunc='mean')[d_order]
    
    print("\n[6] SELECTOR PERFORMANCE UNDER SATURATION")
    print(sel_dens)

if __name__ == "__main__":
    run_density_ultimate_audit()