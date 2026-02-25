import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
import string
import os

# --- 1. FONKSİYON: ÖZEL 3'LÜ (C ORTALANMIŞ) ---
def create_balanced_3panel(image_paths, output_filename):
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig)
    
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :]) # Alt satırı ortalar

    axes = [ax_a, ax_b, ax_c]
    labels = ['A', 'B', 'C']

    for i, ax in enumerate(axes):
        if i < len(image_paths):
            img = mpimg.imread(image_paths[i])
            ax.imshow(img)
            ax.text(-0.02, 1.05, labels[i], transform=ax.transAxes, 
                    fontsize=26, fontweight='bold', va='top', ha='right')
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Kaydedildi: {output_filename}")

# --- 2. FONKSİYON: STANDART 2'Lİ (SIRALAMA) ---
def create_standard_2panel(image_paths, output_filename):
    fig, axes = plt.subplots(1, 2, figsize=(16, 7)) # Yan yana daha şık durması için
    labels = ['A', 'B']

    for i, ax in enumerate(axes):
        if i < len(image_paths):
            img = mpimg.imread(image_paths[i])
            ax.imshow(img)
            ax.text(-0.02, 1.05, labels[i], transform=ax.transAxes, 
                    fontsize=26, fontweight='bold', va='top', ha='right')
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Kaydedildi: {output_filename}")

# --- ÇALIŞTIRMA ---

# 1. FIGUR: Method Rankings (2'li)
rankings_paths = [
    r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\0_Scripts\makale\foto\6a_Method_Ranking_Raw.png", 
    r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\0_Scripts\makale\foto\6b_Method_Ranking_Cleaned.png"
]
create_standard_2panel(rankings_paths, "Method_Rankings.png")

# 2. FIGUR: Heatmap ve Pareto (3'lü Ortalı)
heatmap_paths = [
    r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Discovery_Engine_Outputs\D_ML_Model\2_Interaction_ML_Model_vs_ML_Density.png", 
    r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Discovery_Engine_Outputs\D_Input_Type\2_Interaction_Input_Type_vs_Resolution.png", 
    r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Method_Analysis_Final_v3\3.2b_Method_Pareto_Clustered_Labels.png"
]
create_balanced_3panel(heatmap_paths, "3lu_heatmap_pareto_centered.png")