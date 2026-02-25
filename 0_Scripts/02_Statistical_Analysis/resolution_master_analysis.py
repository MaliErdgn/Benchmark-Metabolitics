import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_resolution_master():
    # 1. SETUP
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_dir = os.path.join(project_root, "5_Figures", "Resolution_Master")
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(input_file)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')

    # --- BOYUT SIRALAMALARINI HESAPLA (PERFORMANSA GÖRE) ---
    
    # ML Model Sıralaması
    model_rank = df.groupby('ML_Model')['F1_Mean'].mean().sort_values(ascending=False).index.tolist()
    
    # ML Density (Feature Selection Strategy) Sıralaması
    density_rank = df.groupby('ML_Density')['F1_Mean'].mean().sort_values(ascending=False).index.tolist()
    
    # Resolution Sıralaması
    res_rank = df.groupby('Resolution')['F1_Mean'].mean().sort_values(ascending=False).index.tolist()
    
    # Dataset Sıralaması (Opsiyonel: Heatmap X ekseni için)
    dataset_rank = df.groupby('Dataset')['F1_Mean'].mean().sort_values(ascending=False).index.tolist()

    # --- CONSOLE VERIFICATION ---
    print("\n" + "="*80)
    print("      PERFORMANS TABANLI SIRALAMALAR (RANKING)")
    print("-" * 80)
    print(f"ML MODELS (Sorted)     : {model_rank}")
    print(f"FS DENSITIES (Sorted)  : {density_rank}")
    print(f"RESOLUTIONS (Sorted)   : {res_rank}")
    print("="*80)

    # Renk Paleti
    color_list = sns.color_palette("viridis", len(res_rank))
    custom_palette = dict(zip(res_rank, color_list))

    # ==========================================================================
    # 1. RESOLUTION x DATASET (Heatmap)
    # ==========================================================================
    print("[1] Plotting Resolution vs Dataset...")
    pivot_ds = df.pivot_table(index='Resolution', columns='Dataset', values='F1_Mean', aggfunc='mean')
    pivot_ds = pivot_ds.reindex(index=res_rank, columns=dataset_rank)

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_ds, annot=True, fmt=".3f", cmap="YlGnBu")
    plt.title("Resolution vs. Dataset (Both Axes Sorted by Performance)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_Resolution_Dataset_Heatmap.png"))
    plt.close()

    # ==========================================================================
    # 2. RESOLUTION x ML MODEL (Heatmap)
    # MODELLER BAŞARI SIRASINA GÖRE DİZİLDİ
    # ==========================================================================
    print("[2] Plotting Resolution vs ML Model...")
    model_pivot = df.pivot_table(index='ML_Model', columns='Resolution', values='F1_Mean', aggfunc='mean')
    # Satırları model_rank, sütunları res_rank sırasına göre diziyoruz
    model_pivot = model_pivot.reindex(index=model_rank, columns=res_rank)

    plt.figure(figsize=(12, 6))
    sns.heatmap(model_pivot, annot=True, fmt=".3f", cmap="RdYlGn", linewidths=.5)
    plt.title("ML Model Performance across Resolutions (Both Axes Sorted)")
    plt.xlabel("Resolution (Best to Worst)")
    plt.ylabel("ML Model (Best to Worst)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_Resolution_Model_Heatmap.png"))
    plt.close()

    # ==========================================================================
    # 3. RESOLUTION x DENSITY (Line Plot)
    # X EKSENİ (STRATEJİLER) BAŞARI SIRASINA GÖRE DİZİLDİ
    # ==========================================================================
    print("[3] Plotting Resolution Trends over Density Strategies...")
    
    plt.figure(figsize=(14, 8))
    # 'order' parametresi lineplot'ta doğrudan X ekseni sırasını belirlemez, 
    # bu yüzden veriyi density_rank sırasına göre kategorize ediyoruz.
    df['ML_Density'] = pd.Categorical(df['ML_Density'], categories=density_rank, ordered=True)
    
    sns.lineplot(
        data=df.sort_values('ML_Density'), 
        x='ML_Density', 
        y='F1_Mean', 
        hue='Resolution', 
        style='Resolution', 
        markers=True, 
        dashes=False, 
        palette=custom_palette, 
        hue_order=res_rank, 
        style_order=res_rank, 
        lw=3
    )
    
    plt.title("Resolution Performance over Feature Selection Strategies\n(X-Axis Sorted by Global Strategy Success)")
    plt.xlabel("Selection Strategy (Best to Worst)")
    plt.ylabel("Mean F1-Score")
    plt.legend(title="Resolution Rank", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_Resolution_Density_Trend.png"))
    plt.close()

    # ==========================================================================
    # 4. RESOLUTION x INPUT TYPE (Bar Plot - Gain)
    # ==========================================================================
    print("[4] Plotting Input Composition Gain...")
    gain_pivot = df.pivot_table(index='Resolution', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    gain_pivot['Gain_%'] = ((gain_pivot['Flux_plus_Coeff'] - gain_pivot['Flux']) / gain_pivot['Flux']) * 100
    gain_pivot = gain_pivot.reindex(res_rank)

    plt.figure(figsize=(12, 6))
    sns.barplot(x=gain_pivot.index, y=gain_pivot['Gain_%'], palette=custom_palette, order=res_rank)
    plt.axhline(0, color='black', linewidth=1)
    plt.title("Information Gain per Resolution (Sorted by Global Resolution Success)")
    plt.ylabel("Performance Gain (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_Resolution_Input_Gain.png"))
    plt.close()

    print(f"\nANALİZ TAMAMLANDI. Çıktılar: {output_dir}")

if __name__ == "__main__":
    run_resolution_master()