import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.lines import Line2D
from scipy.stats import wilcoxon

# =============================================================================
# YAPILANDIRMA
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"
OUTPUT_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Method_Analysis_Final_v3"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
sns.set_theme(style="whitegrid", context="paper", font_scale=1.5)

class FinalMethodAuditor:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.df['Resolution'] = self.df['Resolution'].replace('Pathway', 'Pathway_mean')
        self.target = 'F1_Mean'
        self.methods = sorted(self.df['Obj_Method'].unique())

    def get_family_color(self, method):
        if 'local' in method: return 'Topological', '#e74c3c'
        if 'robust' in method: return 'Statistical', '#27ae60'
        if 'atp' in method or 'bio' in method: return 'Biological', '#f39c12'
        return 'Global', '#3498db'

    # -------------------------------------------------------------------------
    # GÖRSEL 1: RELIABILITY RANKING (μ - σ)
    # -------------------------------------------------------------------------
    def plot_ranking(self):
        print("📊 Generating Reliability-Based Ranking Plot...")
        stats = self.df.groupby('Obj_Method')[self.target].agg(['mean', 'std']).reset_index()
        stats['Penalized'] = stats['mean'] - stats['std']
        stats = stats.sort_values('Penalized', ascending=True)
        stats.set_index('Obj_Method', inplace=True)

        fig, ax = plt.subplots(figsize=(14, 10))
        for i in range(len(stats)):
            if i % 2 == 0: ax.axhspan(i - 0.5, i + 0.5, color='gray', alpha=0.07, zorder=0)
        
        ax.barh(stats.index, stats['mean'], color='lightgray', label='Mean F1 (Overall)', height=0.6)
        ax.barh(stats.index, stats['Penalized'], color='#3498db', label='Reliability Score ($\mu - \sigma$)', height=0.6)
        
        for i, (name, row) in enumerate(stats.iterrows()):
            ax.text(row['mean'] + 0.005, i, f"μ:{row['mean']:.3f}", va='center', fontsize=10, color='#7f8c8d')
            ax.text(row['Penalized'] - 0.005, i, f"{row['Penalized']:.3f}", color='white', va='center', ha='right', fontweight='bold', fontsize=11)
        
        ax.set_title("Objective Function Reliability Ranking", fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel("Stability-Adjusted F1-Score")
        # Lejantı dışarı aldık (Çakışma önleyici)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=True, shadow=True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "3.2a_Method_Reliability_Ranking.png"), dpi=300, bbox_inches='tight')
        plt.close()

    # -------------------------------------------------------------------------
    # GÖRSEL 2: ALL-POINTS PARETO WITH CLUSTERED LABELS
    # -------------------------------------------------------------------------
    def plot_pareto(self):
        print("📈 Generating Pareto Frontier with Clustered Labels...")
        eff = self.df.groupby('Obj_Method').agg({
            self.target: 'mean', 
            'P1_Total_Duration_Sec': 'mean', 
            'P1_Memory_Median_MB': 'mean'
        }).reset_index()
        
        plt.figure(figsize=(16, 10))
        ax = plt.gca()
        
        # 1. Tüm noktaları çiz (Her birinin kendi rengi var)
        for i, row in eff.iterrows():
            family, color = self.get_family_color(row['Obj_Method'])
            size = row['P1_Memory_Median_MB'] / 6
            ax.scatter(row['P1_Total_Duration_Sec'], row[self.target], 
                       s=size, color=color, alpha=0.6, edgecolors='black', linewidths=1.2, zorder=3)

        # 2. Etiket Kümeleme Mantığı (Sadece yazılar için)
        # 500 saniye ve 0.0015 F1 birimlik bir kafes (grid) oluşturup içine düşenleri sayıyoruz
        eff['x_bin'] = (eff['P1_Total_Duration_Sec'] / 600).round()
        eff['y_bin'] = (eff[self.target] / 0.0015).round()
        
        label_groups = eff.groupby(['x_bin', 'y_bin'])
        
        y_range = eff[self.target].max() - eff[self.target].min()

        for (_, _), group in label_groups:
            avg_x = group['P1_Total_Duration_Sec'].mean()
            avg_y = group[self.target].mean()
            
            if len(group) > 2:
                label_text = f"{len(group)} methods"
            elif len(group) == 2:
                label_text = f"{group.iloc[0]['Obj_Method']}\n{group.iloc[1]['Obj_Method']}"
            else:
                label_text = group.iloc[0]['Obj_Method']

            ax.text(avg_x, avg_y + (y_range * 0.04), label_text, 
                    fontsize=9, fontweight='bold', ha='center', va='bottom',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.2), zorder=5)

        # Lejant (Dışarıda)
        legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'{f}', markerfacecolor=c, markersize=12) 
                           for f, c in [('Statistical', '#27ae60'), ('Topological', '#e74c3c'), ('Biological', '#f39c12'), ('Global', '#3498db')]]
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), title="Method Families", frameon=True)

        plt.title("Computational Efficiency Frontier", fontsize=18, fontweight='bold', pad=25)
        plt.xlabel("Total Simulation Time (Seconds)", fontweight='bold')
        plt.ylabel("Global Mean F1-Score", fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "3.2b_Method_Pareto_Clustered_Labels.png"), dpi=300, bbox_inches='tight')
        plt.close()

    # -------------------------------------------------------------------------
    # DETAYLI ÇIKTI DOSYASI (.txt)
    # -------------------------------------------------------------------------
    def generate_detailed_log(self):
        log_path = os.path.join(OUTPUT_DIR, "EXHAUSTIVE_METHOD_REPORT.txt")
        print(f"📄 Writing detailed logs to {log_path}...")
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("=== MARKERDB DISCOVERY ENGINE: EXHAUSTIVE METHOD AUDIT ===\n\n")
            
            # 1. Scorecard
            f.write("1. PERFORMANCE SCORECARD (Ranked by Mean F1)\n")
            summary = self.df.groupby('Obj_Method')[self.target].agg(['mean', 'std', 'min', 'max', 'median']).sort_values('mean', ascending=False)
            f.write(summary.to_string() + "\n\n")

            # 2. Model Synergy
            f.write("2. MODEL-SPECIFIC PERFORMANCE\n")
            model_pivot = self.df.pivot_table(index='Obj_Method', columns='ML_Model', values=self.target, aggfunc='mean')
            f.write(model_pivot.to_string() + "\n\n")

            # 3. Significance vs Baseline
            f.write("3. STATISTICAL SIGNIFICANCE VS BASELINE (Wilcoxon)\n")
            group_cols = ['Dataset', 'Resolution', 'Input_Type', 'ML_Model', 'ML_Selector', 'ML_Density']
            pivot_w = self.df.pivot_table(index=group_cols, columns='Obj_Method', values=self.target).dropna()
            sig_list = []
            for m in self.methods:
                if m == 'baseline_base': continue
                _, p = wilcoxon(pivot_w[m], pivot_w['baseline_base'])
                sig_list.append({"Method": m, "P_Value": p})
            f.write(pd.DataFrame(sig_list).sort_values('P_Value').to_string() + "\n")

    def run(self):
        self.plot_ranking()
        self.plot_pareto()
        self.generate_detailed_log()
        print(f"🏁 DONE! Reports are in {OUTPUT_DIR}")

if __name__ == "__main__":
    auditor = FinalMethodAuditor(INPUT_FILE)
    auditor.run()