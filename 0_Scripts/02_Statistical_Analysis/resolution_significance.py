import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import scipy.stats as stats

def run_resolution_significance():
    # 1. YOLLAR VE VERI YUKLEME
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_dir = os.path.join(project_root, "5_Figures/Resolution")
    
    df = pd.read_csv(input_file)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')

    # 2. PIVOT TABLO
    pivot_cols = ['Dataset', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density', 'Obj_Method']
    df_pivot = df.pivot_table(index=pivot_cols, columns='Resolution', values='F1_Mean')
    
    resolutions = df_pivot.columns.tolist()
    n_res = len(resolutions)
    p_matrix = pd.DataFrame(np.ones((n_res, n_res)), index=resolutions, columns=resolutions)

    # 3. TEST DONGUSU (Wilcoxon Signed-Rank)
    for i in range(n_res):
        for j in range(n_res):
            if i != j:
                res1, res2 = resolutions[i], resolutions[j]
                d1, d2 = df_pivot[res1].dropna(), df_pivot[res2].dropna()
                common = d1.index.intersection(d2.index)
                if len(common) > 20:
                    _, p = stats.wilcoxon(d1.loc[common], d2.loc[common])
                    p_matrix.loc[res1, res2] = p

    # ==============================================================================
    # 4. CONSOLE VERIFICATION (SAYISAL RAPOR)
    # ==============================================================================
    print("\n" + "="*90)
    print("      RESOLUTION PAIRWISE SIGNIFICANCE MATRIX (P-VALUES)")
    print("="*90)
    print(p_matrix.applymap(lambda x: f"{x:.2e}"))
    
    print("\n" + "-"*90)
    print("      DETAILED SIGNIFICANCE ANALYSIS (Alpha = 0.05)")
    print("-" * 90)
    
    for res in resolutions:
        # Bu cozunurlugun digerlerinden farkli oldugu durumlari bul
        diff_list = p_matrix.loc[res, p_matrix.loc[res] < 0.05].index.tolist()
        
        # Bu cozunurlugun digerlerinden "daha iyi" oldugu durumlari bul (Mean F1 kontroluyle)
        better_list = []
        res_mean = df[df['Resolution'] == res]['F1_Mean'].mean()
        
        for target in diff_list:
            target_mean = df[df['Resolution'] == target]['F1_Mean'].mean()
            if res_mean > target_mean:
                better_list.append(target)
        
        if better_list:
            print(f"[DOMINANT] {res:<15} is significantly BETTER than: {better_list}")
        else:
            print(f"[STABLE]   {res:<15} has no significant superiority over others.")
            
    print("="*90)

    # ==============================================================================
    # 5. GORSELLESTIRME
    # ==============================================================================
    plt.figure(figsize=(12, 10))
    log_p = np.log10(p_matrix + 1e-50)
    annot_matrix = p_matrix.map(lambda x: f"{x:.1e}" if x < 0.001 else f"{x:.3f}")

    sns.heatmap(
        log_p, 
        annot=annot_matrix.values, 
        fmt="", 
        cmap="YlGnBu_r", 
        cbar_kws={'label': 'Log10(P-Value)'}
    )
    
    plt.title("Statistical Significance Matrix: Biological Resolutions\n(P-values from Wilcoxon Signed-Rank Test)", fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "resolution_significance_heatmap.png"))
    plt.close()

    print(f"\nAnaliz tamamlandi. Grafik: {output_dir}/resolution_significance_heatmap.png")

if __name__ == "__main__":
    run_resolution_significance()