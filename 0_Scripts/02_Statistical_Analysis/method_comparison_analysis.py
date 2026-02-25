import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import scipy.stats as stats

def run_method_comparison():
    # --- 1. DOSYA YOLLARI ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_dir = os.path.join(project_root, "5_Figures")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"HATA: {input_file} bulunamadi!")
        return

    df = pd.read_csv(input_file)
    
    group_cols = ['Dataset', 'Resolution', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density']
    methods = df['Obj_Method'].unique()

    # ==============================================================================
    # ANALIZ 1: BASELINE ILE FARK (DELTA)
    # ==============================================================================
    print("\n[ANALYSIS 1] Calculating Difference to Baseline...")
    pivot_f1 = df.pivot_table(index=group_cols, columns='Obj_Method', values='F1_Mean')
    df_delta = pivot_f1.subtract(pivot_f1['baseline_base'], axis=0).drop(columns=['baseline_base'])
    
    print("Top 5 Positive Delta (Mean Improvement):")
    print(df_delta.mean().sort_values(ascending=False).head(5))

    plt.figure(figsize=(12, 7))
    sns.boxplot(data=df_delta, orient="h", palette="coolwarm")
    plt.axvline(0, color='black', linestyle='--', lw=1.5)
    plt.title("Difference to Baseline (F1-Score Delta)")
    plt.xlabel(r"$\Delta$ F1-Score (Method - Baseline)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_Difference_To_Baseline.png"))
    plt.close()

    # ==============================================================================
    # ANALIZ 2: KAZANMA OLASILIGI (WINNING PROBABILITY)
    # ==============================================================================
    print("\n[ANALYSIS 2] Calculating Winning Probability Curves...")
    df_ratios = pivot_f1.divide(pivot_f1.max(axis=1), axis=0) 
    
    plt.figure(figsize=(10, 6))
    for col in df_ratios.columns:
        sorted_ratios = np.sort(df_ratios[col])
        prob_y = np.arange(len(sorted_ratios)) / float(len(sorted_ratios))
        plt.step(sorted_ratios, prob_y, label=col, alpha=0.7)

    plt.xlim(0.9, 1.0)
    plt.title("Probability of Being Near-Best Performance")
    plt.xlabel("Performance Ratio (1.0 = Best)")
    plt.ylabel("Probability")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='x-small', ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_Winning_Probability_Curves.png"))
    plt.close()

    # ==============================================================================
    # ANALIZ 3: IKILI KAZANMA SAYISI (PAIRWISE WINS)
    # ==============================================================================
    print("\n[ANALYSIS 3] Calculating Pairwise Win Counts...")
    df_wins = pd.DataFrame(index=methods, columns=methods, data=0)
    
    for m1 in methods:
        for m2 in methods:
            if m1 == m2: continue
            win_count = (pivot_f1[m1] > pivot_f1[m2]).sum()
            df_wins.loc[m1, m2] = win_count

    print("Total Win Counts (Top 5):")
    print(df_wins.sum(axis=1).sort_values(ascending=False).head(5))

    plt.figure(figsize=(14, 11))
    sns.heatmap(df_wins.astype(int), annot=True, fmt="d", cmap="Blues")
    plt.title("Pairwise Comparison: Total Win Counts")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_Pairwise_Win_Counts.png"))
    plt.close()

    # ==============================================================================
    # ANALIZ 4: SIRALAMA ISTIKRARI (RANK CONSISTENCY)
    # ==============================================================================
    print("\n[ANALYSIS 4] Calculating Rank Consistency Across Datasets...")
    df['Rank'] = df.groupby(group_cols)['F1_Mean'].rank(ascending=False, method='min')
    df_ranks = df.groupby(['Obj_Method', 'Dataset'])['Rank'].mean().unstack()
    
    plt.figure(figsize=(12, 6))
    for m in df_ranks.index:
        plt.plot(df_ranks.columns, df_ranks.loc[m], marker='o', alpha=0.4, label=m)
    
    plt.gca().invert_yaxis()
    plt.title("Method Rank Consistency Across Datasets")
    plt.ylabel("Average Rank (1 = Best)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2, fontsize='x-small')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_Rank_Consistency.png"))
    plt.close()

    # ==============================================================================
    # ANALIZ 5: GENEL SIRALAMA OZETI (AVERAGE RANKS)
    # ==============================================================================
    print("\n[ANALYSIS 5] Running Friedman Global Ranking Test...")
    friedman_data = [pivot_f1[m].values for m in methods]
    
    # Dogru fonksiyon ismi: friedmanchisquare
    stat, p = stats.friedmanchisquare(*friedman_data)
    print(f"Friedman Stat: {stat:.2f}, P-Value: {p:.2e}")
    
    avg_ranks = df_ranks.mean(axis=1).sort_values()
    
    plt.figure(figsize=(10, 8))
    sns.barplot(x=avg_ranks.values, y=avg_ranks.index, palette="RdYlGn_r")
    plt.title("Global Ranking Summary (Mean Rank)")
    plt.xlabel("Mean Rank (Lower is Better)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "5_Global_Ranking_Summary.png"))
    plt.close()

    print(f"\nAnaliz tamamlandi. Grafiklerin konumu: {output_dir}")

if __name__ == "__main__":
    run_method_comparison()