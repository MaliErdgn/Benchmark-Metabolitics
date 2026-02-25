import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# =============================================================================
# YOLLAR VE AYARLAR
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"
OUTPUT_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures"

COLORS = {'Statistical': '#27ae60', 'Topological': '#e74c3c', 'Global': '#3498db', 'Biological': '#f39c12'}

def get_family(method):
    if 'local' in method: return 'Topological'
    if 'robust' in method: return 'Statistical'
    if 'atp' in method or 'bio' in method: return 'Biological'
    return 'Global'

def generate_separated_method_plots():
    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    sns.set_theme(style="whitegrid")

    # 1. DATA PREP: RAW
    raw_stats = df.groupby('Obj_Method')['F1_Mean'].mean().sort_values(ascending=False)
    raw_rank_map = {m: i + 1 for i, m in enumerate(raw_stats.index)}

    # 2. DATA PREP: CLEANED (Excluding SVM and Full Density)
    clean_df = df[(df['ML_Model'] != 'SVM') & (df['ML_Density'] != 'Full')].copy()
    clean_stats = clean_df.groupby('Obj_Method')['F1_Mean'].mean().sort_values(ascending=False)

    # -------------------------------------------------------------------------
    # PLOT A: RAW RANKING (The Baseline State)
    # -------------------------------------------------------------------------
    plt.figure(figsize=(12, 10))
    raw_df = raw_stats.reset_index()
    raw_df['Family'] = raw_df['Obj_Method'].apply(get_family)
    
    ax1 = sns.barplot(data=raw_df, x='F1_Mean', y='Obj_Method', hue='Family', palette=COLORS, dodge=False)
    ax1.set_yticklabels([f"{i+1}. {m}" for i, m in enumerate(raw_stats.index)])
    
    plt.title("Figure 6a: Global Objective Function Ranking\n(All 57,600 experiments included)", fontsize=15, fontweight='bold')
    plt.xlabel("Mean F1-Score", fontweight='bold')
    plt.ylabel("Methodology", fontweight='bold')
    plt.xlim(raw_stats.min() - 0.01, raw_stats.max() + 0.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "6a_Method_Ranking_Raw.png"), dpi=300)
    plt.close()

    # -------------------------------------------------------------------------
    # PLOT B: CLEANED RANKING (The Latent Signal)
    # -------------------------------------------------------------------------
    plt.figure(figsize=(12, 10))
    clean_df_plot = clean_stats.reset_index()
    clean_df_plot['Family'] = clean_df_plot['Obj_Method'].apply(get_family)
    
    ax2 = sns.barplot(data=clean_df_plot, x='F1_Mean', y='Obj_Method', hue='Family', palette=COLORS, dodge=False)
    
    # Y-ekseni etiketleri ve Rank Shift anonsu
    new_labels = []
    for i, (method, score) in enumerate(clean_stats.items()):
        new_rank = i + 1
        old_rank = raw_rank_map[method]
        shift = old_rank - new_rank
        
        new_labels.append(f"{new_rank}. {method}")
        
        # Barın sonuna +11 gibi shift değerlerini yazalım
        if shift != 0:
            shift_text = f"{shift:+d}"
            color = 'green' if shift > 0 else 'red'
            plt.text(score + 0.001, i, shift_text, va='center', ha='left', 
                     fontweight='bold', color=color, fontsize=11)

    ax2.set_yticklabels(new_labels)
    plt.title("Figure 6b: Denoised Objective Function Ranking\n(Excluding Dimensions: SVM & Full Density)", fontsize=15, fontweight='bold')
    plt.xlabel("Mean F1-Score", fontweight='bold')
    plt.ylabel("Methodology", fontweight='bold')
    plt.xlim(clean_stats.min() - 0.01, clean_stats.max() + 0.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "6b_Method_Ranking_Cleaned.png"), dpi=300)
    plt.close()

    print(f"✅ İki ayrı grafik üretildi: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_separated_method_plots()