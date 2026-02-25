import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re

# =============================================================================
# YAPILANDIRMA
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"
OUTPUT_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Parameter_Analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
sns.set_theme(style="whitegrid", context="paper", font_scale=1.4)

def extract_param_value(method_name, prefix):
    match = re.search(f"{prefix}([0-9\.]+)", method_name)
    if match:
        return float(match.group(1))
    return None

def run_parameter_sensitivity_fixed():
    print("🎛️ Parameter Sensitivity Audit (Fixed Axis) Started...")
    df = pd.read_csv(INPUT_FILE)
    
    # --- VERİ HAZIRLIĞI ---
    local_df = df[df['Obj_Method'].str.contains('local')].copy()
    local_df['k'] = local_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'k'))
    
    robust_df = df[df['Obj_Method'].str.contains('robust')].copy()
    robust_df['sigma'] = robust_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'sigma_'))
    
    atp_df = df[df['Obj_Method'].str.contains('atp_atp')].copy()
    atp_df['lambda'] = atp_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'atp_'))
    
    bio_df = df[df['Obj_Method'].str.contains('biomass')].copy()
    bio_df['threshold'] = bio_df['Obj_Method'].apply(lambda x: extract_param_value(x, 'bio_'))

    # --- GÖRSELLEŞTİRME ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Topological Depth (k) - Lineer Eksen
    sns.lineplot(data=local_df, x='k', y='F1_Mean', marker='o', markersize=10, linewidth=3, ax=axes[0,0], color='#e74c3c')
    axes[0,0].set_title("Topological Depth (Local k-hop)", fontweight='bold')
    axes[0,0].set_xlabel("Neighborhood Depth ($k$)")
    axes[0,0].set_ylabel("Mean F1-Score")
    axes[0,0].set_xticks(sorted(local_df['k'].unique())) # 1, 2, 3, 4, 5, 6
    axes[0,0].grid(True, linestyle='--', alpha=0.5)

    # 2. Robustness (Sigma) - Log Eksen + MANUEL TICK
    sigma_vals = sorted(robust_df['sigma'].unique()) # [0.01, 0.05, 0.1, 0.5]
    sns.lineplot(data=robust_df, x='sigma', y='F1_Mean', marker='s', markersize=10, linewidth=3, ax=axes[0,1], color='#27ae60')
    axes[0,1].set_title("Noise Regularization (Robust $\sigma$)", fontweight='bold')
    axes[0,1].set_xlabel("Sigma Value ($\sigma$)")
    axes[0,1].set_xscale('log')
    # İşte sihirli dokunuş:
    axes[0,1].set_xticks(sigma_vals)
    axes[0,1].set_xticklabels([str(x) for x in sigma_vals]) 
    axes[0,1].grid(True, which="both", linestyle='--', alpha=0.3)

    # 3. ATP Weight (Lambda) - Log Eksen + MANUEL TICK
    lambda_vals = sorted(atp_df['lambda'].unique()) # [1.0, 10.0, 50.0, 100.0]
    sns.lineplot(data=atp_df, x='lambda', y='F1_Mean', marker='^', markersize=10, linewidth=3, ax=axes[1,0], color='#f39c12')
    axes[1,0].set_title("Energy Constraint Weight (ATP $\lambda$)", fontweight='bold')
    axes[1,0].set_xlabel("Lambda ($\lambda$)")
    axes[1,0].set_xscale('log')
    axes[1,0].set_xticks(lambda_vals)
    axes[1,0].set_xticklabels([str(int(x)) for x in lambda_vals]) # 1, 10, 50, 100
    axes[1,0].grid(True, which="both", linestyle='--', alpha=0.3)

    # 4. Biomass Threshold - Lineer Eksen + MANUEL TICK
    thresh_vals = sorted(bio_df['threshold'].unique())
    sns.lineplot(data=bio_df, x='threshold', y='F1_Mean', marker='D', markersize=10, linewidth=3, ax=axes[1,1], color='#8e44ad')
    axes[1,1].set_title("Growth Viability Threshold (Biomass)", fontweight='bold')
    axes[1,1].set_xlabel("Minimum Growth Ratio")
    axes[1,1].set_xticks(thresh_vals) # 0.01, 0.05, 0.1, 0.2
    axes[1,1].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Figure_Parameter_Sensitivity_Fixed.png"), dpi=300)
    
    print(f"\n✅ Düzeltilmiş Grafik Kaydedildi: {OUTPUT_DIR}")
    print(f"   -> Robust X-Ekseni artık {sigma_vals} değerlerini gösteriyor.")

if __name__ == "__main__":
    run_parameter_sensitivity_fixed()