import pandas as pd
import numpy as np
from scipy.stats import hypergeom
from sklearn.metrics import cohen_kappa_score

# PATH
FEAT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"

def run_selector_significance_audit():
    print("⚖️ SELECTOR SIGNIFICANCE ENGINE: ANOVA vs. Wilcoxon")
    print("="*100)
    
    # Veriyi yükle
    df = pd.read_csv(FEAT_FILE, low_memory=False)
    
    # Deneyi tanımlayan kolonlar
    group_cols = ['Dataset', 'Method', 'Res', 'Input', 'Dens', 'Model']
    
    # ANOVA ve Wilcoxon setlerini oluştur
    sets = df.groupby(group_cols + ['Sel'])['Feat'].apply(set).unstack('Sel').dropna()

    def calculate_significance(row):
        a = row['ANOVA']
        w = row['Wilcoxon']
        
        # Evren Büyüklüğü (N) Ayarı
        res = row.name[2] # 'Res' kolonu
        N = 106 if 'Pathway' in str(res) else 10600
        
        # Fischer/Hypergeometric Parametreleri
        # M: toplam populasyon (N)
        # n: populasyondaki başarı sayısı (ANOVA'nın seçtikleri)
        # N_draw: örneklem büyüklüğü (Wilcoxon'un seçtikleri)
        # k: örneklemdeki başarı sayısı (Kesişim)
        
        k = len(a.intersection(w))
        n1 = len(a)
        n2 = len(w)
        
        # Hipergeometrik P-değeri (P(X >= k))
        # SF (Survival Function) P(X > k-1) verir, yani P(X >= k)
        p_val = hypergeom.sf(k - 1, N, n1, n2)
        
        # Cohen's Kappa hazırlığı
        # Evrendeki her bir feature için seçildi/seçilmedi (1/0) vektörü oluştur
        # Basitleştirilmiş Kappa hesabı (Intersection üzerinden)
        # po: gözlemlenen uyum, pe: beklenen uyum
        po = (k + (N - (n1 + n2 - k))) / N
        pe = ((n1 * n2) + (N - n1) * (N - n2)) / (N**2)
        kappa = (po - pe) / (1 - pe) if (1 - pe) != 0 else 0
        
        return pd.Series([k, n1, p_val, kappa], 
                         index=['Overlap', 'Set_Size', 'P_Value', 'Kappa'])

    print("⏳ İstatistiksel testler hesaplanıyor...")
    results = sets.apply(calculate_significance, axis=1)

    # SONUÇLARI RAPORLA
    print(f"\n[1] GLOBAL SIGNIFICANCE SUMMARY")
    print(f"   - Median P-Value     : {results['P_Value'].median():.2e}")
    print(f"   - Mean Cohen's Kappa : {results['Kappa'].mean():.4f}")
    
    # Anlamlılık oranını ölç (P < 0.05)
    sig_ratio = (results['P_Value'] < 0.05).mean() * 100
    print(f"   - Significant Overlap: %{sig_ratio:.2f} of all experiments")

    print("\n[2] KAPPA (STABILITY) BY RESOLUTION")
    print(results.groupby('Res')['Kappa'].mean().sort_values(ascending=False))

    print("\n[3] P-VALUE ANALYSIS BY DATASET (Median P)")
    print(results.groupby('Dataset')['P_Value'].median().sort_values())

if __name__ == "__main__":
    run_selector_significance_audit()