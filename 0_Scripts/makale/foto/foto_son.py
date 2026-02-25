import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from matplotlib.lines import Line2D

# =============================================================================
# YOLLAR VE AYARLAR
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"
OUTPUT_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Q1_Journal_Plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Q1 Dergi Font Ayarları
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
sns.set_theme(style="whitegrid", context="paper")
COLORS = {'Statistical': '#27ae60', 'Topological': '#e74c3c', 'Global': '#3498db', 'Biological': '#f39c12'}

def get_family(method):
    if 'local' in method: return 'Topological'
    if 'robust' in method: return 'Statistical'
    if 'atp' in method or 'bio' in method: return 'Biological'
    return 'Global'

def extract_param_value(method_name, prefix):
    match = re.search(f"{prefix}([0-9\.]+)", method_name)
    if match:
        return float(match.group(1))
    return None

# =============================================================================
# 1. SIRALAMA GRAFİKLERİ (RANKINGS) - RAW & CLEANED
# =============================================================================
def generate_q1_rankings(df):
    print("Generating Rankings Plots...")
    
    raw_stats = df.groupby('Obj_Method')['F1_Mean'].mean().sort_values(ascending=False)
    raw_rank_map = {m: i + 1 for i, m in enumerate(raw_stats.index)}
    raw_df = raw_stats.reset_index()
    raw_df['Family'] = raw_df['Obj_Method'].apply(get_family)

    clean_df = df[(df['ML_Model'] != 'SVM') & (df['ML_Density'] != 'Full')].copy()
    clean_stats = clean_df.groupby('Obj_Method')['F1_Mean'].mean().sort_values(ascending=False)
    clean_df_plot = clean_stats.reset_index()
    clean_df_plot['Family'] = clean_df_plot['Obj_Method'].apply(get_family)

    # --- PLOT A: RAW RANKING ---
    plt.figure(figsize=(12, 10))
    ax1 = sns.barplot(data=raw_df, x='F1_Mean', y='Obj_Method', hue='Family', palette=COLORS, dodge=False)
    ax1.set_yticklabels([f"{i+1}. {m}" for i, m in enumerate(raw_stats.index)], fontsize=14)
    plt.xlabel("Mean F1-Score", fontweight='bold', fontsize=16)
    plt.ylabel("Methodology", fontweight='bold', fontsize=16)
    plt.xticks(fontsize=14)
    plt.xlim(raw_stats.min() - 0.01, raw_stats.max() + 0.01)
    ax1.legend(fontsize=14, title_fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Ranking_Raw_Q1.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --- PLOT B: CLEANED RANKING ---
    plt.figure(figsize=(12, 10))
    ax2 = sns.barplot(data=clean_df_plot, x='F1_Mean', y='Obj_Method', hue='Family', palette=COLORS, dodge=False)
    
    new_labels = []
    for i, (method, score) in enumerate(clean_stats.items()):
        new_rank = i + 1
        shift = raw_rank_map[method] - new_rank
        new_labels.append(f"{new_rank}. {method}")
        if shift != 0:
            shift_text = f"{shift:+d}"
            color = 'green' if shift > 0 else 'red'
            plt.text(score + 0.001, i, shift_text, va='center', ha='left', fontweight='bold', color=color, fontsize=14)

    ax2.set_yticklabels(new_labels, fontsize=14)
    plt.xlabel("Mean F1-Score", fontweight='bold', fontsize=16)
    plt.ylabel("Methodology", fontweight='bold', fontsize=16)
    plt.xticks(fontsize=14)
    plt.xlim(clean_stats.min() - 0.01, clean_stats.max() + 0.01)
    ax2.legend(fontsize=14, title_fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Ranking_Cleaned_Q1.png"), dpi=300, bbox_inches='tight')
    plt.close()

# =============================================================================
# 2. ISI HARİTALARI (HEATMAPS)
# =============================================================================
def generate_q1_heatmap(df, dim1, dim2, filename):
    print(f"Generating Heatmap: {dim1} vs {dim2}...")
    dim1_order = df.groupby(dim1)['F1_Mean'].mean().sort_values(ascending=False).index
    pivot = df.pivot_table(index=dim1, columns=dim2, values='F1_Mean', aggfunc='mean')
    dim2_order = pivot.mean(axis=0).sort_values(ascending=False).index
    pivot = pivot.reindex(index=dim1_order, columns=dim2_order)
    
    row_means = pivot.mean(axis=1)
    pivot_deviation = pivot.sub(row_means, axis=0)
    abs_max = max(abs(pivot_deviation.min().min()), abs(pivot_deviation.max().max()))
    if abs_max < 0.001: abs_max = 0.01
    
    plt.figure(figsize=(12, 8))
    ax = sns.heatmap(pivot_deviation, annot=pivot, fmt=".3f", cmap="RdYlGn", center=0, 
                     vmin=-abs_max, vmax=abs_max, linewidths=0.5, annot_kws={"size": 14})
    
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label(f'Performance Deviation from {dim1} Average', size=14, weight='bold')

    plt.xlabel(dim2, fontweight='bold', fontsize=16)
    plt.ylabel(dim1, fontweight='bold', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14, rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

# =============================================================================
# 3. PARETO GRAFİĞİ (EFFICIENCY FRONTIER)
# =============================================================================
def generate_q1_pareto(df):
    print("Generating Pareto Frontier Plot...")
    eff = df.groupby('Obj_Method').agg({'F1_Mean': 'mean', 'P1_Total_Duration_Sec': 'mean', 'P1_Memory_Median_MB': 'mean'}).reset_index()
    
    plt.figure(figsize=(14, 9))
    ax = plt.gca()
    
    for i, row in eff.iterrows():
        family = get_family(row['Obj_Method'])
        color = COLORS[family]
        size = row['P1_Memory_Median_MB'] / 6
        ax.scatter(row['P1_Total_Duration_Sec'], row['F1_Mean'], s=size, color=color, alpha=0.7, edgecolors='black', linewidths=1.2, zorder=3)

    eff['x_bin'] = (eff['P1_Total_Duration_Sec'] / 600).round()
    eff['y_bin'] = (eff['F1_Mean'] / 0.0015).round()
    label_groups = eff.groupby(['x_bin', 'y_bin'])
    y_range = eff['F1_Mean'].max() - eff['F1_Mean'].min()

    for (_, _), group in label_groups:
        avg_x = group['P1_Total_Duration_Sec'].mean()
        avg_y = group['F1_Mean'].mean()
        
        if len(group) > 2: label_text = f"{len(group)} methods"
        elif len(group) == 2: label_text = f"{group.iloc[0]['Obj_Method']}\n{group.iloc[1]['Obj_Method']}"
        else: label_text = group.iloc[0]['Obj_Method']

        ax.text(avg_x, avg_y + (y_range * 0.04), label_text, fontsize=12, fontweight='bold', ha='center', va='bottom',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=0.3), zorder=5)

    legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'{f}', markerfacecolor=c, markersize=14) 
                       for f, c in COLORS.items()]
    ax.legend(handles=legend_elements, loc='upper right', title="Method Families", fontsize=14, title_fontsize=16, frameon=True)

    plt.xlabel("Total Simulation Time (Seconds)", fontweight='bold', fontsize=16)
    plt.ylabel("Global Mean F1-Score", fontweight='bold', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Pareto_Frontier_Q1.png"), dpi=300, bbox_inches='tight')
    plt.close()

# =============================================================================
# 4. PARAMETRE HASSASİYETİ GRAFİĞİ (PARAMETER SENSITIVITY)
# =============================================================================
def generate_q1_parameter_sensitivity(df):
    print("Generating Parameter Sensitivity Plot...")
    
    local_df = df[df['Obj_Method'].str.contains('local')].copy()
    local_df['k'] = local_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'k'))
    
    robust_df = df[df['Obj_Method'].str.contains('robust')].copy()
    robust_df['sigma'] = robust_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'sigma_'))
    
    atp_df = df[df['Obj_Method'].str.contains('atp_atp')].copy()
    atp_df['lambda'] = atp_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'atp_'))
    
    bio_df = df[df['Obj_Method'].str.contains('biomass')].copy()
    bio_df['threshold'] = bio_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'bio_'))

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 1. Topological Depth (k)
    sns.lineplot(data=local_df, x='k', y='F1_Mean', marker='o', markersize=10, linewidth=3, ax=axes[0,0], color='#e74c3c')
    axes[0,0].set_title("Topological Depth (Local k-hop)", fontweight='bold', fontsize=16)
    axes[0,0].set_xlabel("Neighborhood Depth ($k$)", fontsize=16)
    axes[0,0].set_ylabel("Mean F1-Score", fontsize=16)
    axes[0,0].set_xticks(sorted(local_df['k'].unique()))
    axes[0,0].tick_params(axis='both', which='major', labelsize=14)
    axes[0,0].grid(True, linestyle='--', alpha=0.5)

    # 2. Robustness (Sigma)
    sigma_vals = sorted(robust_df['sigma'].unique())
    sns.lineplot(data=robust_df, x='sigma', y='F1_Mean', marker='s', markersize=10, linewidth=3, ax=axes[0,1], color='#27ae60')
    axes[0,1].set_title("Noise Regularization (Robust $\sigma$)", fontweight='bold', fontsize=16)
    axes[0,1].set_xlabel("Sigma Value ($\sigma$)", fontsize=16)
    axes[0,1].set_ylabel("")
    axes[0,1].set_xscale('log')
    axes[0,1].set_xticks(sigma_vals)
    axes[0,1].set_xticklabels([str(x) for x in sigma_vals]) 
    axes[0,1].tick_params(axis='both', which='major', labelsize=14)
    axes[0,1].grid(True, which="both", linestyle='--', alpha=0.3)

    # 3. ATP Weight (Lambda)
    lambda_vals = sorted(atp_df['lambda'].unique())
    sns.lineplot(data=atp_df, x='lambda', y='F1_Mean', marker='^', markersize=10, linewidth=3, ax=axes[1,0], color='#f39c12')
    axes[1,0].set_title("Energy Constraint Weight (ATP $\lambda$)", fontweight='bold', fontsize=16)
    axes[1,0].set_xlabel("Lambda ($\lambda$)", fontsize=16)
    axes[1,0].set_ylabel("Mean F1-Score", fontsize=16)
    axes[1,0].set_xscale('log')
    axes[1,0].set_xticks(lambda_vals)
    axes[1,0].set_xticklabels([str(int(x)) for x in lambda_vals])
    axes[1,0].tick_params(axis='both', which='major', labelsize=14)
    axes[1,0].grid(True, which="both", linestyle='--', alpha=0.3)

    # 4. Biomass Threshold
    thresh_vals = sorted(bio_df['threshold'].unique())
    sns.lineplot(data=bio_df, x='threshold', y='F1_Mean', marker='D', markersize=10, linewidth=3, ax=axes[1,1], color='#8e44ad')
    axes[1,1].set_title("Growth Viability Threshold (Biomass)", fontweight='bold', fontsize=16)
    axes[1,1].set_xlabel("Minimum Growth Ratio", fontsize=16)
    axes[1,1].set_ylabel("")
    axes[1,1].set_xticks(thresh_vals)
    axes[1,1].tick_params(axis='both', which='major', labelsize=14)
    axes[1,1].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Parameter_Sensitivity_Q1.png"), dpi=300, bbox_inches='tight')
    plt.close()

# =============================================================================
# ÇALIŞTIRMA
# =============================================================================
if __name__ == "__main__":
    df_main = pd.read_csv(INPUT_FILE)
    df_main['Resolution'] = df_main['Resolution'].replace('Pathway', 'Pathway_mean')
    
    generate_q1_rankings(df_main)
    generate_q1_heatmap(df_main, 'ML_Model', 'ML_Density', "Heatmap_MLModel_vs_Density_Q1.png")
    generate_q1_heatmap(df_main, 'Input_Type', 'Resolution', "Heatmap_InputType_vs_Resolution_Q1.png")
    generate_q1_pareto(df_main)
    generate_q1_parameter_sensitivity(df_main)
    
    print(f"Process completed. All processed figures are saved in: {OUTPUT_DIR}")