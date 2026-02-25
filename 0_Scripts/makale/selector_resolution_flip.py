import pandas as pd

# PATH
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_selector_flip_audit():
    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')

    print("="*100)
    print("      SELECTOR-RESOLUTION INTERACTION: FINDING THE FLIP")
    print("="*100)

    # 1. RESOLUTION FLIP
    # Does Wilcoxon win in high-dimension (Reaction) but lose in low-dimension (Pathway)?
    flip = df.pivot_table(index='Resolution', columns='ML_Selector', values='F1_Mean', aggfunc='mean')
    flip['W_Advantage'] = flip['Wilcoxon'] - flip['ANOVA']
    
    print("\n[1] SELECTOR PERFORMANCE BY BIOLOGICAL RESOLUTION")
    print(flip.sort_values('W_Advantage', ascending=False))

    # 2. DENSITY x RESOLUTION x SELECTOR
    # At 10% Density, which Resolution benefits most from Wilcoxon?
    sparse_df = df[df['ML_Density'] == '10']
    sparse_flip = sparse_df.pivot_table(index='Resolution', columns='ML_Selector', values='F1_Mean', aggfunc='mean')
    sparse_flip['W_Advantage_10pct'] = sparse_flip['Wilcoxon'] - sparse_flip['ANOVA']

    print("\n[2] SELECTOR PERFORMANCE AT 10% DENSITY (The Sparsity Sweet Spot)")
    print(sparse_flip.sort_values('W_Advantage_10pct', ascending=False))

    # 3. METHOD VOLATILITY
    # Which Selector creates the most 'unstable' method rankings?
    print("\n[3] RANK VOLATILITY (Std Dev of Method Ranks)")
    for sel in ['ANOVA', 'Wilcoxon']:
        ranks = df[df['ML_Selector'] == sel].groupby('Obj_Method')['F1_Mean'].mean().rank()
        print(f"   Selector: {sel:<10} | Rank Variance: {ranks.std():.4f}")

if __name__ == "__main__":
    run_selector_flip_audit()