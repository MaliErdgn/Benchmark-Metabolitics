import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import wilcoxon
from matplotlib.lines import Line2D

# =============================================================================
# 1. AYARLAR VE STİL
# =============================================================================
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
sns.set_theme(style="whitegrid", context="paper", font_scale=1.4)

DIMENSIONS = ['Dataset', 'Obj_Method', 'Resolution', 'Input_Type', 'ML_Selector', 'ML_Density', 'ML_Model']
# Zaman maliyetinin ML'den geldiği boyutlar
ML_TIMED_DIMS = ['ML_Model', 'ML_Selector', 'ML_Density']
METRICS = ['F1_Mean', 'AUC_Mean', 'Sens_Mean', 'Spec_Mean', 'Acc_Mean']
TARGET_METRIC = 'F1_Mean'

class DeepDiscoveryEngine:
    def __init__(self, file_path, output_root):
        self.df = pd.read_csv(file_path)
        self.output_root = output_root
        os.makedirs(output_root, exist_ok=True)
        print(f"🚀 Deep Discovery Engine Başlatıldı. Veri Seti: {len(self.df):,} satır.")

    # -------------------------------------------------------------------------
    # GÖRSEL 1: ZEBRALI YATAY PENALIZED BAR (Dual Numeric)
    # -------------------------------------------------------------------------
    def plot_penalized_bars(self, dim, df_dim, folder_path):
        stats = df_dim.groupby(dim)[TARGET_METRIC].agg(['mean', 'std']).fillna(0)
        stats['Penalized'] = stats['mean'] - stats['std']
        stats = stats.sort_values('Penalized', ascending=True)
        
        plt.figure(figsize=(12, len(stats) * 0.5 + 3))
        for i in range(len(stats)):
            if i % 2 == 0: plt.axhspan(i - 0.5, i + 0.5, color='gray', alpha=0.07, zorder=0)
            
        plt.barh(stats.index, stats['mean'], color='lightgray', label='Mean F1', height=0.6, zorder=2)
        plt.barh(stats.index, stats['Penalized'], color='#3498db', label=r'Penalized Score ($\mu - \sigma$)', height=0.6, zorder=3)
        
        for i, (name, row) in enumerate(stats.iterrows()):
            plt.text(row['mean'] + 0.005, i, f"μ:{row['mean']:.3f}", va='center', ha='left', fontsize=9, color='#7f8c8d')
            plt.text(row['Penalized'] - 0.005, i, f"{row['Penalized']:.3f}", color='white', va='center', ha='right', fontweight='bold', fontsize=10, zorder=4)
            
        plt.title(f"Success-Ranked Stability: {dim}", fontsize=14, fontweight='bold')
        plt.xlim(max(0, stats['Penalized'].min() - 0.05), min(1.0, stats['mean'].max() + 0.1))
        plt.legend(loc='lower right', frameon=True, shadow=True)
        sns.despine(left=True); plt.tight_layout()
        plt.savefig(os.path.join(folder_path, f"1_Ranking_{dim}.png"), dpi=300); plt.close()

    # -------------------------------------------------------------------------
    # GÖRSEL 2: ISI HARİTASI (Row-wise Dynamic Normalization)
    # -------------------------------------------------------------------------
    def plot_interaction_matrix(self, dim, folder_path):
        other_dims = [d for d in DIMENSIONS if d != dim]
        dim_order = self.df.groupby(dim)[TARGET_METRIC].mean().sort_values(ascending=False).index
        
        for other in other_dims:
            pivot = self.df.pivot_table(index=dim, columns=other, values=TARGET_METRIC, aggfunc='mean')
            other_order = pivot.mean(axis=0).sort_values(ascending=False).index
            pivot = pivot.reindex(index=dim_order, columns=other_order)
            
            # Row-wise Deviation (Yumuşak Normalizasyon)
            row_means = pivot.mean(axis=1)
            pivot_deviation = pivot.sub(row_means, axis=0)
            
            abs_max = max(abs(pivot_deviation.min().min()), abs(pivot_deviation.max().max()))
            if abs_max < 0.001: abs_max = 0.01
            
            plt.figure(figsize=(14, 10))
            sns.heatmap(pivot_deviation, annot=pivot, fmt=".3f", cmap="RdYlGn", 
                        center=0, vmin=-abs_max, vmax=abs_max, linewidths=0.5, 
                        cbar_kws={'label': f'Performance Deviation from {dim} Average'})
            plt.title(f"Impact Matrix: {dim} vs {other}", fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(folder_path, f"2_Interaction_{dim}_vs_{other}.png"), dpi=300); plt.close()

    # -------------------------------------------------------------------------
    # GÖRSEL 3: SMART EFFICIENCY FRONTIER (Zaman Mantığı Düzeltildi)
    # -------------------------------------------------------------------------
    def plot_efficiency(self, dim, df_dim, folder_path):
        # MANTIK: Boyut ML ile alakalıysa eğitim süresine, değilse HPC süresine bak.
        is_ml_dim = dim in ML_TIMED_DIMS
        cost_col = 'ML_Duration_CV_Sec' if is_ml_dim else 'P1_Total_Duration_Sec'
        cost_label = "ML Training Time (Sec)" if is_ml_dim else "HPC Simulation Time (Sec)"
        
        if cost_col not in df_dim.columns: return

        eff_stats = df_dim.groupby(dim).agg({
            TARGET_METRIC: 'mean', 
            cost_col: 'mean', 
            'P1_Memory_Median_MB': 'mean'
        }).reset_index().sort_values(TARGET_METRIC, ascending=False)

        # Görsel ferahlık için geniş figür
        plt.figure(figsize=(16, 9))
        ax = plt.gca()
        colors = sns.color_palette("husl", len(eff_stats))
        
        y_min, y_max = eff_stats[TARGET_METRIC].min(), eff_stats[TARGET_METRIC].max()
        y_range = y_max - y_min if y_max != y_min else 0.1
        ax.set_ylim(y_min - y_range*0.4, y_max + y_range*0.4)

        for i, row in eff_stats.iterrows():
            size = row['P1_Memory_Median_MB'] / 8 
            ax.scatter(row[cost_col], row[TARGET_METRIC], s=size, color=colors[i], 
                       alpha=0.6, edgecolors='black', linewidths=1.2, zorder=3)
            
            # Offset Küçültüldü: Balona daha yakın etiketler
            v_offset = y_range * 0.06
            ax.text(row[cost_col], row[TARGET_METRIC] + v_offset, row[dim], 
                    fontsize=10, fontweight='bold', ha='center', va='bottom', zorder=5,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.1))

        # Manuel RAM Lejantı (Dışarıda ve Temiz)
        ram_vals = [eff_stats['P1_Memory_Median_MB'].min(), eff_stats['P1_Memory_Median_MB'].median(), eff_stats['P1_Memory_Median_MB'].max()]
        legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'{int(v)} MB',
                           markerfacecolor='gray', markersize=np.sqrt(v/8), alpha=0.5) for v in ram_vals]
        ax.legend(handles=legend_elements, loc='upper left', title="Memory Usage", bbox_to_anchor=(1.02, 1), labelspacing=3, borderpad=1.5, frameon=True)

        ax.set_title(f"Efficiency Frontier: {dim}\n(Cost metric: {cost_label})", fontsize=15, fontweight='bold', pad=25)
        ax.set_xlabel(cost_label, fontweight='bold'); ax.set_ylabel(f"Mean {TARGET_METRIC}", fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3, zorder=0)
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, f"3_Efficiency_{dim}.png"), dpi=300, bbox_inches='tight'); plt.close()

    # -------------------------------------------------------------------------
    # GÖRSEL 4 & 5: DISTRIBUTION & BIAS (Kapsam Korundu)
    # -------------------------------------------------------------------------
    def plot_distribution_boxplot(self, dim, df_dim, folder_path):
        order = df_dim.groupby(dim)[TARGET_METRIC].median().sort_values(ascending=False).index
        plt.figure(figsize=(16, 10))
        sns.boxplot(data=df_dim, x=dim, y=TARGET_METRIC, order=order, palette="viridis", showmeans=True, 
                    meanprops={"marker":"D","markerfacecolor":"white", "markeredgecolor":"black"})
        plt.title(f"Distribution Analysis: {dim}", fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right'); plt.tight_layout()
        plt.savefig(os.path.join(folder_path, f"4_Distribution_{dim}.png"), dpi=300); plt.close()

    def plot_metric_tradeoff(self, dim, df_dim, folder_path):
        stats = df_dim.groupby(dim)[['Sens_Mean', 'Spec_Mean', 'F1_Mean']].mean()
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=stats, x='Spec_Mean', y='Sens_Mean', size='F1_Mean', sizes=(100, 1000), hue=stats.index, palette="tab20", alpha=0.8)
        plt.plot([0, 1], [0, 1], ls="--", c=".3", label="Perfect Balance")
        for i, txt in enumerate(stats.index):
            plt.text(stats['Spec_Mean'][i], stats['Sens_Mean'][i]+0.01, txt, fontsize=9, ha='center', fontweight='bold')
        plt.title(f"Bias Analysis: Sens vs Spec ({dim})", fontsize=15, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left'); plt.tight_layout()
        plt.savefig(os.path.join(folder_path, f"5_Bias_Tradeoff_{dim}.png"), dpi=300); plt.close()

    # -------------------------------------------------------------------------
    # RAPOR MOTORU: DEEP SEMANTIC REPORT (Kapsam Korundu)
    # -------------------------------------------------------------------------
    def generate_deep_report(self, dim, df_dim, folder_path):
        report_path = os.path.join(folder_path, f"DEEP_REPORT_{dim}.txt")
        stats = df_dim.groupby(dim)[METRICS].agg(['mean', 'std', 'min', 'max'])
        f1_stats = stats['F1_Mean'].sort_values('mean', ascending=False)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n      COMPREHENSIVE ANALYSIS: {dim.upper()}\n{'='*80}\n\n")
            f.write(f"1. EXECUTIVE SUMMARY\n   - Winner: {f1_stats['mean'].idxmax()}\n   - Stability Leader: {f1_stats['std'].idxmin()}\n\n")
            
            f.write(f"2. SCORECARD\n{'-'*100}\n")
            summary_df = df_dim.groupby(dim)[METRICS].mean().sort_values('F1_Mean', ascending=False)
            f.write(summary_df.to_string() + "\n\n")

            f.write(f"3. WILCOXON SIGNIFICANCE MATRIX\n")
            pivot_data = self.df.pivot_table(index=[d for d in DIMENSIONS if d != dim], columns=dim, values=TARGET_METRIC)
            items = f1_stats.index[:12]
            p_matrix = pd.DataFrame(index=items, columns=items)
            for e1 in items:
                for e2 in items:
                    if e1 == e2: p_matrix.loc[e1, e2] = "-"
                    else:
                        try:
                            d1, d2 = pivot_data[e1].dropna(), pivot_data[e2].dropna()
                            common = d1.index.intersection(d2.index)
                            if len(common) > 10:
                                _, p = wilcoxon(d1.loc[common], d2.loc[common])
                                p_matrix.loc[e1, e2] = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                            else: p_matrix.loc[e1, e2] = "N/A"
                        except: p_matrix.loc[e1, e2] = "Err"
            f.write(p_matrix.to_string() + "\n\n")

            f.write(f"4. SCENARIO DISCOVERY (Top 5)\n")
            top_scenarios = df_dim.sort_values('F1_Mean', ascending=False).head(5)
            for i, row in top_scenarios.iterrows():
                f.write(f"   -> F1: {row['F1_Mean']:.4f} | {row[dim]} ({row['Dataset']}/{row['ML_Model']})\n")

    def run_full_analysis(self):
        for dim in DIMENSIONS:
            print(f"🔎 Comprehensive Analysis: {dim}...")
            dim_folder = os.path.join(self.output_root, f"D_{dim}")
            os.makedirs(dim_folder, exist_ok=True)
            self.plot_penalized_bars(dim, self.df, dim_folder)
            self.plot_interaction_matrix(dim, dim_folder)
            self.plot_efficiency(dim, self.df, dim_folder)
            self.plot_distribution_boxplot(dim, self.df, dim_folder)
            self.plot_metric_tradeoff(dim, self.df, dim_folder)
            self.generate_deep_report(dim, self.df, dim_folder)
        print(f"✅ COMPLETED: {self.output_root}")

if __name__ == "__main__":
    INPUT_CSV = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"
    OUTPUT_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\Discovery_Engine_Outputs"
    engine = DeepDiscoveryEngine(INPUT_CSV, OUTPUT_DIR)
    engine.run_full_analysis()