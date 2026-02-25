import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_interaction_analysis():
    # 1. SETUP
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_dir = os.path.join(project_root, "5_Figures", "Interaction_Analysis")
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(input_file)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')

    print("\n" + "="*80)
    print("      MULTI-DIMENSIONAL INTERACTION ANALYSIS")
    print("="*80)

    # ==========================================================================
    # ANALİZ 1: ML MODEL x RESOLUTION
    # Soru: Hangi model (XGB, LR...) yüksek boyutu (Reaction) daha iyi yönetiyor?
    # ==========================================================================
    print("\n[1] ML MODEL IMPACT ACROSS RESOLUTIONS:")
    model_pivot = df.pivot_table(index='Resolution', columns='ML_Model', values='F1_Mean', aggfunc='mean')
    
    # Konsol Raporu
    print(model_pivot.round(4))
    
    # Görselleştirme
    plt.figure(figsize=(10, 8))
    sns.heatmap(model_pivot, annot=True, fmt=".3f", cmap="magma_r")
    plt.title("Interaction: Biological Resolution vs. Machine Learning Model", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_Resolution_vs_Model_Heatmap.png"))
    plt.close()

    # ==========================================================================
    # ANALİZ 2: INPUT TYPE x RESOLUTION (Information Gain)
    # Soru: Katsayı eklemek (Flux+Cr) en çok hangi seviyede işe yarıyor?
    # ==========================================================================
    print("\n[2] INPUT COMPOSITION GAIN (%):")
    input_pivot = df.pivot_table(index='Resolution', columns='Input_Type', values='F1_Mean', aggfunc='mean')
    input_pivot['Gain_%'] = ((input_pivot['Flux_plus_Coeff'] - input_pivot['Flux']) / input_pivot['Flux']) * 100
    
    # Kazanç sırasına göre yazdır
    print(input_pivot.sort_values('Gain_%', ascending=False).round(4))

    # Görselleştirme (Bar Plot)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=input_pivot.index, y=input_pivot['Gain_%'], palette="coolwarm")
    plt.axhline(0, color='black', linewidth=1)
    plt.title("Performance Gain by Adding Coefficients ($C_r$) per Resolution", fontsize=14, fontweight='bold')
    plt.ylabel("Relative F1-Score Gain (%)")
    plt.xlabel("Resolution")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_Input_Gain_per_Resolution.png"))
    plt.close()

    # ==========================================================================
    # ANALİZ 3: SELECTOR x RESOLUTION
    # Soru: 10.000 özellikli Reaction seviyesinde Wilcoxon mı ANOVA mı?
    # ==========================================================================
    print("\n[3] FEATURE SELECTOR IMPACT:")
    sel_pivot = df.pivot_table(index='Resolution', columns='ML_Selector', values='F1_Mean', aggfunc='mean')
    sel_pivot['Diff'] = sel_pivot['Wilcoxon'] - sel_pivot['ANOVA']
    print(sel_pivot.round(4))

    # Görselleştirme
    plt.figure(figsize=(10, 6))
    df_melt = df.groupby(['Resolution', 'ML_Selector'])['F1_Mean'].mean().reset_index()
    
    sns.barplot(data=df_melt, x='Resolution', y='F1_Mean', hue='ML_Selector', palette="Paired")
    plt.ylim(0.75, 0.81) # Farkı görmek için zoom
    plt.title("Feature Selector Performance: ANOVA vs Wilcoxon", fontsize=14, fontweight='bold')
    plt.legend(loc='lower right')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_Selector_Comparison.png"))
    plt.close()

    print(f"\n✅ Analiz tamamlandı. Grafikler: {output_dir}")

if __name__ == "__main__":
    run_interaction_analysis()