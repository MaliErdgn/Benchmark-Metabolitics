import pandas as pd
import numpy as np
from scipy.stats import ttest_rel
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_ranking_analysis():
    # 1. YOLLAR
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_dir = os.path.join(project_root, "5_Figures")
    
    df = pd.read_csv(input_file)

    # 2. NORMALİZASYON (Dataset etkisini silmek için her dataset-model grubunda sıralama yapıyoruz)
    # Her bir deney grubunda metotları 1'den 20'ye kadar sırala (1=En iyi)
    group_cols = ['Dataset', 'Resolution', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density']
    df['Rank'] = df.groupby(group_cols)['F1_Mean'].rank(ascending=False, method='min')

    # 3. İSTATİSTİKSEL TEST (Baseline'a karşı)
    methods = df['Obj_Method'].unique()
    baseline_scores = df[df['Obj_Method'] == 'baseline_base'].sort_values(group_cols)['F1_Mean'].values
    
    stats_list = []
    for m in methods:
        m_data = df[df['Obj_Method'] == m].sort_values(group_cols)
        m_scores = m_data['F1_Mean'].values
        
        # Sayısal kontrol
        if len(m_scores) == len(baseline_scores):
            t_stat, p_val = ttest_rel(m_scores, baseline_scores)
            mean_f1 = np.mean(m_scores)
            mean_rank = df[df['Obj_Method'] == m]['Rank'].mean()
            top1_count = len(df[(df['Obj_Method'] == m) & (df['Rank'] == 1)])
            
            stats_list.append({
                "Method": m,
                "Mean_F1": mean_f1,
                "Mean_Rank": mean_rank,
                "P_Value": p_val,
                "Top1_Count": top1_count
            })

    stats_df = pd.DataFrame(stats_list).sort_values("Mean_Rank")

    # --- CONSOLE VERIFICATION ---
    print("\n" + "="*90)
    print(f"{'Method':<25} | {'Mean F1':<10} | {'Mean Rank':<10} | {'P-Value':<12} | {'Top-1 Count':<10}")
    print("-" * 90)
    for _, row in stats_df.iterrows():
        sig = "***" if row['P_Value'] < 0.001 else "** " if row['P_Value'] < 0.01 else "*  " if row['P_Value'] < 0.05 else "ns "
        print(f"{row['Method']:<25} | {row['Mean_F1']:<10.4f} | {row['Mean_Rank']:<10.2f} | {row['P_Value']:<12.2e} ({sig}) | {row['Top1_Count']:<10}")
    print("="*90)

    # 4. GÖRSELLEŞTİRME (Method Ranking Heatmap)
    # Metotların dataset bazlı ortalama sıralamalarını gösteren bir ısı haritası
    pivot_rank = df.pivot_table(index='Obj_Method', columns='Dataset', values='Rank', aggfunc='mean')
    pivot_rank = pivot_rank.reindex(stats_df['Method']) # En iyi metot en üstte

    plt.figure(figsize=(12, 10))
    sns.heatmap(pivot_rank, annot=True, cmap="RdYlGn_r", fmt=".2f", cbar_kws={'label': 'Average Rank (Lower is Better)'})
    plt.title("Scientific Method Ranking Across Datasets\n(1 = Best, 20 = Worst)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # PDF ve PNG olarak ana klasöre kaydet
    plt.savefig(os.path.join(output_dir, "Analytical_Method_Ranking.png"))
    plt.close()
    
    print(f"\n✅ Analiz bitti. Grafik: {output_dir}/Analytical_Method_Ranking.png")

if __name__ == "__main__":
    run_ranking_analysis()