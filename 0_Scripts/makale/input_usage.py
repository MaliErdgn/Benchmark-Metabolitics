import pandas as pd
import numpy as np
import os

# =============================================================================
# YAPILANDIRMA
# =============================================================================
# Cr katsayılarının başında "Coeff_" prefixi olduğu varsayılıyor (ml_pipeline.py'ye göre)
COEFF_PREFIX = "Coeff_"
FEAT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"
BENCHMARK_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_BENCHMARK_FINAL.csv"

def run_cr_preference_audit():
    print("🧬 Cr vs Flux: Feature Preference & Usage Audit Starting...")

    if not os.path.exists(FEAT_FILE):
        print(f"HATA: {FEAT_FILE} bulunamadı.")
        return

    # 1. ÖZELLİK VERİSİNİ YÜKLE
    # Top 100 listelerini okuyoruz
    df_feat = pd.read_csv(FEAT_FILE, low_memory=False)
    
    # Sadece 'Flux_plus_Coeff' konfigürasyonlarını alalım
    # (Not: Senin dosya yapında 'Input' veya 'Input_Type' sütunu olduğunu varsayıyorum)
    input_col = 'Input' if 'Input' in df_feat.columns else 'Input_Type'
    if input_col in df_feat.columns:
        df_feat = df_feat[df_feat[input_col] == 'Flux_plus_Coeff']

    # 2. ÖZELLİĞİN TÜRÜNÜ BELİRLE (Cr mi Flux mı?)
    # Feature ismi COEFF_PREFIX ile başlıyorsa Cr'dir.
    df_feat['Is_Cr'] = df_feat['Feat'].str.startswith(COEFF_PREFIX)

    # 3. KULLANIM İSTATİSTİKLERİ (Hastalık ve Metot Bazında)
    print("\n[1] Cr SELECTION RATIO IN TOP-100")
    # Her deney grubunda (Dataset, Method, Model) kaç Cr seçildi?
    usage_stats = df_feat.groupby(['Dataset', 'Method', 'Model', 'Res']).agg({
        'Is_Cr': ['sum', 'count']
    }).reset_index()
    usage_stats.columns = ['Dataset', 'Method', 'Model', 'Res', 'Cr_Count', 'Total_Features']
    usage_stats['Cr_Percentage'] = (usage_stats['Cr_Count'] / usage_stats['Total_Features']) * 100

    # 4. GLOBAL ÖZET
    print("\nGlobal Preference (Mean % of Cr in Top-100):")
    global_pref = usage_stats.groupby('Dataset')['Cr_Percentage'].mean()
    print(global_pref)

    # 5. METOT BAZLI ÖZET
    print("\nMethod-wise Preference (Which method relies most on Cr?):")
    method_pref = usage_stats.groupby('Method')['Cr_Percentage'].mean().sort_values(ascending=False)
    print(method_pref)

    # 6. EN YÜKSEK Cr KULLANIMINA SAHİP 10 REAKSİYON
    # "Bazı reaksiyonların akışı değil, katsayısı daha önemlidir" kanıtı
    print("\n[2] TOP 10 REACTION COEFFICIENTS (Most frequently selected as Cr):")
    cr_only = df_feat[df_feat['Is_Cr'] == True]
    top_cr_reactions = cr_only['Feat'].value_counts().head(10)
    print(top_cr_reactions)

    # 7. BAŞARI KORELASYONU (Kritik Analiz)
    # -------------------------------------------------------------------------
    # Benchmark dosyasını yükle ve F1 skorlarını eşleştir
    df_bench = pd.read_csv(BENCHMARK_FILE)
    df_bench = df_bench[df_bench['Input_Type'] == 'Flux_plus_Coeff']
    
    # Usage stats ile benchmark skorlarını birleştir (Join)
    # (Sütun isimlerini master benchmark'a göre eşleştirin)
    merged = pd.merge(usage_stats, df_bench, 
                     left_on=['Dataset', 'Method', 'Model', 'Res'], 
                     right_on=['Dataset', 'Obj_Method', 'ML_Model', 'Resolution'])

    correlation = merged['Cr_Percentage'].corr(merged['F1_Mean'])
    print(f"\n[3] SUCCESS CORRELATION:")
    print(f"   Correlation between Cr Usage % and F1_Mean: {correlation:.4f}")
    
    print("\n" + "="*80)
    print("   AUDIT COMPLETE: Provide results to build the narrative.")
    print("="*80)

if __name__ == "__main__":
    run_cr_preference_audit()