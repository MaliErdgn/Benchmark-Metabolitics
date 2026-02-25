import pandas as pd
import numpy as np
import glob
import os

# PATHS - Kendi dosya yapına göre buraları kontrol et
#FEATURES_DIR = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\2_Features"
# Eğer her şey 6_Processed_Data içinde birleşmişse orayı hedefle
MASTER_FEATURES_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv" 
# NOT: Eğer "Top100" olmayan hali varsa onu ver, yoksaFEATURES klasöründeki ham dosyalardan okuyalım.

def run_total_feature_overlap_audit():
    print("🥊 TOTAL FEATURE OVERLAP AUDIT: ANOVA vs. Wilcoxon (Full Selection Set)")
    print("="*100)
    
    # 1. VERİ YÜKLEME
    # Eğer MASTER_FEATURES dosyan çok büyükse, örneklem veya tek bir dataset üzerinden gidelim
    # Ama ideal olan her şeyi görüp net konuşmak.
    df = pd.read_csv(MASTER_FEATURES_FILE, low_memory=False)
    
    # Kolon isimlerini standardize et (Sel, Dens, Res, Feat vb.)
    # Senin dosyanda 'Dens' mi 'ML_Density' mi kontrol etmelisin.
    group_cols = ['Dataset', 'Method', 'Res', 'Input', 'Dens', 'Model']

    # 2. SEÇİLEN ÖZELLİKLERİ SET OLARAK GRUPLA
    print("⏳ Özellik setleri oluşturuluyor... (Bu işlem veri boyutuna göre zaman alabilir)")
    
    # Her bir konfigürasyonda ANOVA ve Wilcoxon'un seçtiği TÜM feature isimlerini set yapıyoruz
    sets = df.groupby(group_cols + ['Sel'])['Feat'].apply(set).unstack('Sel').dropna()

    if sets.empty:
        print("❌ HATA: Karşılaştırılacak ANOVA/Wilcoxon çiftleri bulunamadı.")
        return

    # 3. ÖRTÜŞME (OVERLAP) ANALİZİ
    def calculate_metrics(row):
        a = row['ANOVA']
        w = row['Wilcoxon']
        intersection = len(a.intersection(w))
        # Toplam seçilen özellik sayısı (Densiteye göre değişir)
        # ANOVA ve Wilcoxon aynı density'de her zaman aynı sayıda özellik seçer.
        total_selected = len(a) 
        overlap_pct = (intersection / total_selected) * 100 if total_selected > 0 else 0
        return pd.Series([intersection, total_selected, overlap_pct], 
                         index=['Intersection', 'Total_In_Set', 'Overlap_Pct'])

    results = sets.apply(calculate_metrics, axis=1)

    # 4. RAPORLAMA
    print(f"\n[1] GLOBAL OVERLAP STATISTICS")
    print(f"   - Mean Overlap %     : {results['Overlap_Pct'].mean():.2f}%")
    print(f"   - Median Overlap %   : {results['Overlap_Pct'].median():.2f}%")
    print(f"   - Min Overlap %      : {results['Overlap_Pct'].min():.2f}%")
    print(f"   - Max Overlap %      : {results['Overlap_Pct'].max():.2f}%")

    # Çözünürlük Bazlı (Reaction'da 10 bin özellik varken örtüşmek daha mı zor?)
    print("\n[2] OVERLAP BY RESOLUTION (D3)")
    print(results.groupby('Res')['Overlap_Pct'].mean().sort_values(ascending=False))

    # Yoğunluk Bazlı (D7)
    # %10 density'de mi daha çok ayrışıyorlar yoksa %50'de mi?
    print("\n[3] OVERLAP BY DENSITY (D7)")
    # 'Dens' kolonundaki p05, Full gibi değerleri sıralı görmek için
    print(results.groupby('Dens')['Overlap_Pct'].mean())

    # Hastalık Bazlı (D1)
    print("\n[4] OVERLAP BY DATASET (D1)")
    print(results.groupby('Dataset')['Overlap_Pct'].mean().sort_values(ascending=False))

if __name__ == "__main__":
    run_total_feature_overlap_audit()