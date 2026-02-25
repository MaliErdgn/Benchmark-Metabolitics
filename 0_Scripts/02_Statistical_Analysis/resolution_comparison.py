import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_resolution_comparison():
    # 1. PATHS AND DATA LOADING
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_dir = os.path.join(project_root, "5_Figures/Resolution")
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(input_file)
    # Pathway ve Pathway_mean aynı şey olduğu için birleştiriyoruz
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')

    # 2. STATISTICAL CALCULATION (DETAILED)
    # Tüm hiyerarşiyi hesaplayalım
    res_stats = df.groupby('Resolution')['F1_Mean'].agg([
        'count', 'mean', 'median', 'std', 'min', 'max'
    ]).sort_values(by='mean', ascending=False)
    
    # Median ve Mean farkını hesapla (Senin 'başarısızlık' teorin için kritik)
    res_stats['Med_Mean_Diff'] = res_stats['median'] - res_stats['mean']
    
    # --- CONSOLE VERIFICATION (ARTIK BASILIYOR) ---
    print("\n" + "="*100)
    print("      RESOLUTION PERFORMANCE AUDIT: FULL STATISTICAL BREAKDOWN")
    print("="*100)
    # Pandas ayarıyla tablonun tamamını görelim
    pd.options.display.max_columns = None
    pd.options.display.width = 1000
    print(res_stats.to_string())
    print("-" * 100)
    
    # Kararlılık yorumu için en yüksek riskli (Std) olanı bulalım
    most_volatile = res_stats['std'].idxmax()
    print(f"Hafıza Notu: En yüksek varyans (risk): {most_volatile}")
    print("="*100 + "\n")

    # 3. VISUALIZATION PREP
    res_order = res_stats.index.tolist()
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'serif'

    # --- FIG 1: BAR PLOT (Mean vs Median) ---
    plt.figure(figsize=(14, 8))
    plot_data_bar = res_stats[['mean', 'median']].reset_index().melt(id_vars='Resolution', var_name='Metric', value_name='F1_Score')
    ax1 = sns.barplot(
        data=plot_data_bar, 
        x="Resolution", 
        y="F1_Score", 
        hue="Metric", 
        palette={"mean": "#2c3e50", "median": "#e74c3c"}
    )
    plt.ylim(0.70, 0.82) 
    for p in ax1.patches:
        height = p.get_height()
        if height > 0:
            ax1.annotate(format(height, '.4f'), (p.get_x() + p.get_width() / 2., height), 
                         ha='center', va='center', xytext=(0, 9), textcoords='offset points',
                         fontsize=8, fontweight='bold')
    plt.title("F1-Score Analysis: Mean vs. Median Comparison (Sorted by Mean)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "resolution_comparison_bar.png"))
    plt.close()

    # --- FIG 2: BOX PLOT (Distribution & Whiskers) ---
    plt.figure(figsize=(14, 8))
    sns.boxplot(
        data=df,
        x="Resolution",
        y="F1_Mean",
        order=res_order,
        palette="viridis",
        showmeans=True,
        meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black", "markersize":"8"}
    )
    plt.title("F1-Score Distribution: Stability and Outlier Analysis", fontsize=14)
    plt.ylabel("F1-Score")
    plt.xlabel("Resolution Strategy")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "resolution_distribution_box.png"))
    plt.close()

    print(f"Analiz tamamlandı. Grafikler '{output_dir}' içine kaydedildi.")

if __name__ == "__main__":
    run_resolution_comparison()