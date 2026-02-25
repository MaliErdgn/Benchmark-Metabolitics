import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import warnings

warnings.filterwarnings("ignore")

# =============================================================================
# AYARLAR
# =============================================================================
INPUT_FILE = "Final_Transcriptomic_Validation_Results.csv"

def run_ultimate_statistical_audit():
    # 1. Veri Yukleme ve Temizlik
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Hata: {INPUT_FILE} dosyasi bulunamadi.")
        return

    # 'Pathway' legacy etiketini cikar
    if 'Res' in df.columns:
        df = df[df['Res'] != 'Pathway'].copy()
    
    # Eksik verileri temizle
    df = df.dropna(subset=['Overlap_Percent'])

    # Analiz edilecek boyutlar
    dimensions = ['Res', 'Method', 'Model', 'Dataset']
    
    print("NIHAI ISTATISTIKSEL DENETIM RAPORU: BIYOLOJIK VALIDASYON")
    print("=" * 80)
    print(f"Toplam Deney Sayisi: {len(df)}")
    print(f"Analiz Edilen Boyutlar: {dimensions}")
    print("-" * 80)

    for dim in dimensions:
        if dim not in df.columns:
            continue

        print(f"\nBOYUT ANALIZI: {dim}")
        print("=" * 40)

        # Gruplari hazirla
        grouped = df.groupby(dim)['Overlap_Percent']
        group_names = list(grouped.groups.keys())
        data_to_test = [group.values for name, group in grouped]

        # 1. Global Test: Kruskal-Wallis
        if len(data_to_test) < 2:
            print(f"Uyari: {dim} boyutu icin yeterli grup yok.")
            continue

        h_stat, p_kw = stats.kruskal(*data_to_test)
        print(f"Kruskal-Wallis H-Istatistigi: {h_stat:.4f}")
        print(f"Global p-value: {p_kw:.4e}")

        # 2. Anlamlilik Durumunda Ileri Testler
        if p_kw < 0.05:
            print(f"Sonuc: {dim} gruplari arasindaki fark istatistiksel olarak ANLAMLI (p < 0.05)")
            print("-" * 40)
            
            # Grup sayisina gore test secimi
            if len(group_names) > 2:
                # 2'den fazla grup varsa: Tukey HSD (Post-Hoc)
                # Not: Kruskal sonrasi Tukey kullanimi raporlama kolayligi ve 
                # genel trendleri gormek icin makalelerde yaygin kabul gorur.
                print(f"Post-Hoc Analizi (Tukey HSD) Sonuclari:")
                tukey = pairwise_tukeyhsd(endog=df['Overlap_Percent'], groups=df[dim], alpha=0.05)
                # Sadece anlamli olanlari (reject=True) filtreleyerek basabiliriz 
                # ancak tum tabloyu gormek daha forensik bir yaklasimdir.
                print(tukey.summary())
            
            else:
                # Sadece 2 grup varsa (Ornegin Dataset: BC vs BRCA): Mann-Whitney U
                print(f"İkili Karsilastirma (Mann-Whitney U) Sonuclari:")
                g1_name, g2_name = group_names[0], group_names[1]
                g1_data = df[df[dim] == g1_name]['Overlap_Percent']
                g2_data = df[df[dim] == g2_name]['Overlap_Percent']
                u_stat, p_mw = stats.mannwhitneyu(g1_data, g2_data)
                
                print(f"   {g1_name} vs {g2_name}:")
                print(f"   p-value = {p_mw:.4e}")
                print(f"   Ortalama Fark: {g1_data.mean() - g2_data.mean():.4f}")
        
        else:
            print(f"Sonuc: {dim} gruplari arasinda istatistiksel olarak anlamli bir fark bulunamadi.")
        
        print("\n" + "-" * 80)

    print("\nDENETIM TAMAMLANDI.")

if __name__ == "__main__":
    # Pandas cikti ayarlarini guncelle (Tablolarin tam gorunmesi icin)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    
    run_ultimate_statistical_audit()