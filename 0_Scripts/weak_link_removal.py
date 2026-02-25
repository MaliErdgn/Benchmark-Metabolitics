import pandas as pd
import numpy as np
import os

# =============================================================================
# AYARLAR
# =============================================================================
INPUT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_dynamic_toxic_filter_analysis():
    df = pd.read_csv(INPUT_FILE)
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')
    
    # Analiz edilecek "Mühendislik" boyutları (Dataset'i filtrelemiyoruz, o biyolojik gerçekliktir)
    engineering_dims = ['ML_Model', 'ML_Density', 'Resolution', 'ML_Selector', 'Input_Type']
    
    print("="*100)
    print("      DYNAMIC TOXICITY FILTERING: ALGORITHMIC DATA CLEANING")
    print("="*100)

    toxic_filters = {}
    
    # 1.# 1. ALGORİTMİK TESPİT: İstatistiksel Zayıf Halkaları (Outliers) Bul
    # -------------------------------------------------------------------------
    for dim in engineering_dims:
        dim_stats = df.groupby(dim)['F1_Mean'].mean()
        dim_mean = dim_stats.mean()
        dim_std = dim_stats.std()
        
        # Z-Skoru Hesapla: (Level_Mean - Dim_Mean) / Dim_Std
        # Z < -1.0 olanlar (ortalamanın 1 standart sapma altında kalanlar) toksiktir.
        z_scores = (dim_stats - dim_mean) / dim_std
        
        toxic_levels = z_scores[z_scores < -1.0].index.tolist()
        
        if toxic_levels:
            toxic_filters[dim] = toxic_levels
            print(f"📍 Dimension [{dim:<12}]: Found {len(toxic_levels)} toxic level(s) -> {toxic_levels}")
            for lvl in toxic_levels:
                print(f"   - Level '{lvl}' is a statistical outlier (Z-Score: {z_scores[lvl]:.2f})")
    # 2. FİLTRELEME: Zehirli Satırları Temizle
    # -------------------------------------------------------------------------
    clean_df = df.copy()
    for dim, levels in toxic_filters.items():
        clean_df = clean_df[~clean_df[dim].isin(levels)]

    print("\n" + "-"*100)
    print(f"📊 DATASET SUMMARY")
    print(f"   Original Experiments : {len(df)}")
    print(f"   Cleaned Experiments  : {len(clean_df)}")
    print(f"   Data Retention Rate  : {len(clean_df)/len(df)*100:.1f}%")
    print("-" * 100)

    # 3. YENİ SIRALAMA (RE-RANKING)
    # -------------------------------------------------------------------------
    # Eski (Raw) Sıralama
    raw_ranking = df.groupby('Obj_Method')['F1_Mean'].mean().sort_values(ascending=False)
    raw_rank_map = {method: rank + 1 for rank, method in enumerate(raw_ranking.index)}

    # Yeni (Cleaned) Sıralama
    clean_stats = clean_df.groupby('Obj_Method')['F1_Mean'].agg(['mean', 'std', 'min'])
    clean_stats = clean_stats.sort_values(by='mean', ascending=False)

    print("\n[FINAL RESULTS] CLEANED METHOD RANKING VS. RAW RANKING")
    print("-" * 100)
    
    report = []
    for rank, (method, row) in enumerate(clean_stats.iterrows()):
        new_rank = rank + 1
        old_rank = raw_rank_map[method]
        shift = old_rank - new_rank
        
        report.append({
            "New_Rank": new_rank,
            "Method": method,
            "Clean_F1": row['mean'],
            "Stability(Std)": row['std'],
            "Old_Rank": old_rank,
            "Rank_Shift": f"{shift:+d}" if shift != 0 else "0"
        })

    final_report_df = pd.DataFrame(report)
    print(final_report_df.to_string(index=False))

    # 4. KAZANANIN ANALİZİ
    best_method = final_report_df.iloc[0]['Method']
    print("\n" + "="*100)
    print(f"🏆 ULTIMATE BIOLOGICAL CHAMPION: {best_method}")
    print(f"💡 This method provides the highest performance after removing systemic noise factors.")
    print("="*100)

if __name__ == "__main__":
    run_dynamic_toxic_filter_analysis()