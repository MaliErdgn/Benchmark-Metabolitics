import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

def draw_professional_tree():
    # 1. SETUP
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, "5_Figures/Resolution")
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(18, 12)) # Figür boyutunu biraz daha büyüttük
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    plt.rcParams['font.family'] = 'sans-serif'

    # 2. BOYUT VE İÇERİK TANIMLARI
    root = {"name": "Benchmarking\nFramework", "pos": (1, 5), "color": "#2c3e50"}
    
    dims = [
        {"name": "Datasets (6)", "list": "BC, PRAD, BRCA\nPDAC, Alzheimer, Diabetes"},
        {"name": "Objectives (20)", "list": "Baseline, Topology\nLocal (k1-6)\nRobust (4 params)\nATP (4 params)\nBiomass (4 params)"},
        {"name": "Resolution (6)", "list": "Reaction\nPathway (Min, Max, Sum,\nMean, Median)"},
        {"name": "Input Type (2)", "list": "Flux Only\nFlux + Coefficients (Cr)"},
        {"name": "Selectors (2)", "list": "ANOVA (F-test)\nWilcoxon Rank-Sum"},
        {"name": "Density (5)", "list": "10%, 20%, 50%\np < 0.05, Full (100%)"},
        {"name": "ML Models (4)", "list": "Logistic Regression, Random Forest\nSVM (Linear), XGBoost"}
    ]

    # 3. ÇİZİM PARAMETRELERİ (Genişletilmiş)
    x_title = 4.2    # Başlık kutularının merkezi
    x_detail = 8.5   # Detay kutularının merkezi
    y_positions = np.linspace(9, 1, len(dims))
    
    # --- ROOT ÇİZİMİ ---
    root_w, root_h = 1.8, 1.2
    ax.add_patch(patches.FancyBboxPatch((root["pos"][0]-root_w/2, root["pos"][1]-root_h/2), 
                 root_w, root_h, boxstyle="round,pad=0.2", fc=root["color"], ec="black", lw=2))
    ax.text(root["pos"][0], root["pos"][1], root["name"], color='white', 
            ha='center', va='center', fontweight='bold', fontsize=13)

    # --- DALLARIN ÇİZİMİ ---
    print("\n" + "="*50)
    print("      TREE STRUCTURE GENERATION REPORT")
    print("="*50)

    for i, dim in enumerate(dims):
        y = y_positions[i]
        
        # --- A) Boyut Başlık Kutusu (Mavi) ---
        title_w, title_h = 2.4, 0.9 # Boyutlar büyütüldü
        ax.add_patch(patches.FancyBboxPatch((x_title-title_w/2, y-title_h/2), 
                     title_w, title_h, boxstyle="round,pad=0.1", fc="#34495e", ec="black", lw=1.5))
        ax.text(x_title, y, dim["name"], color='white', ha='center', va='center', 
                fontweight='bold', fontsize=11)
        
        # --- B) İçerik Detay Kutusu (Gri) ---
        detail_w, detail_h = 4.2, 1.0 # Genişlik ve yükseklik artırıldı
        ax.add_patch(patches.FancyBboxPatch((x_detail-detail_w/2, y-detail_h/2), 
                     detail_w, detail_h, boxstyle="round,pad=0.1", fc="#f8f9fa", ec="#7f8c8d", lw=1))
        ax.text(x_detail, y, dim["list"], color='#2c3e50', ha='center', va='center', 
                fontsize=10, fontstyle='italic', linespacing=1.3)

        # --- C) Bağlantı Çizgileri ---
        # Kavis ayarı
        curvature = (5 - y) * 0.06
        
        # Root'un sağ kenarından, Başlık kutusunun sol kenarına
        path = patches.ConnectionPatch(xyA=(root["pos"][0] + root_w/2 + 0.2, root["pos"][1]), 
                                     xyB=(x_title - title_w/2, y), 
                                     coordsA="data", coordsB="data",
                                     axesA=ax, axesB=ax, 
                                     arrowstyle="-|>", 
                                     connectionstyle=f"arc3,rad={curvature}",
                                     color="#2c3e50", lw=1.8, mutation_scale=15)
        ax.add_artist(path)
        
        # Başlık kutusunun sağından, Detay kutusunun soluna (Düz çizgi)
        ax.annotate("", xy=(x_detail - detail_w/2, y), xytext=(x_title + title_w/2, y),
                    arrowprops=dict(arrowstyle="->", color="#7f8c8d", lw=1, ls='--'))
        
        print(f"Node Created: {dim['name']:<25} | Position: y={y:.2f}")

    # 4. BİLGİ NOTU
    total_exp = "Total Combinations: 6 x 20 x 6 x 2 x 2 x 5 x 4 = 57,600 Independent Models"
    ax.text(6, 0.2, total_exp, ha='center', va='center', fontsize=12, 
            fontweight='bold', color="#c0392b", bbox=dict(facecolor='yellow', alpha=0.1, boxstyle="round,pad=0.5"))

    plt.title("Hierarchical Overview of the Benchmarking Framework Dimensions", 
              fontsize=18, fontweight='bold', pad=40)
    
    # Kaydet
    output_path = os.path.join(output_dir, "Dimension_Tree_Final.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print("-" * 50)
    print(f"✅ Tree Diagram saved: {output_path}")
    print("="*50 + "\n")

if __name__ == "__main__":
    draw_professional_tree()