import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import warnings

warnings.filterwarnings("ignore")

# =============================================================================
# AYARLAR
# =============================================================================
INPUT_FILE = "Full_Density_Biological_Validation.csv"

def run_ground_truth_statistical_audit():
    # 1. Veri Yukleme ve Temizlik
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Hata: {INPUT_FILE} dosyasi bulunamadi.")
        return

    # 'Pathway' legacy etiketini cikar (Pathway_mean ile ayni oldugu icin)
    if 'Res' in df.columns:
        df = df[df['Res'] != 'Pathway'].copy()
    
    # Eksik verileri temizle
    df = df.dropna(subset=['F1_Score'])

    # Analiz edilecek boyutlar
    dimensions = ['Res', 'Method', 'Model', 'Input', 'Sel', 'Dataset']
    
    print("NIHAI ISTATISTIKSEL DENETIM: LITERATUR UYUMLULUGU (GROUND TRUTH)")
    print("=" * 85)
    print(f"Veri Kaynagi: {INPUT_FILE}")
    print(f"Hedef Metrik: F1_Score (Biological Overlap Success)")
    print("-" * 85)

    for dim in dimensions:
        if dim not in df.columns:
            continue

        print(f"\nBOYUT ANALIZI: {dim}")
        print("=" * 45)

        # Gruplari hazirla
        grouped = df.groupby(dim)['F1_Score']
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
            print(f"Sonuc: {dim} boyutundaki gruplar biyolojik ortusmede ANLAMLI fark yaratiyor.")
            print("-" * 45)
            
            # Grup sayisina gore test secimi
            if len(group_names) > 2:
                # 2'den fazla grup varsa: Tukey HSD (Post-Hoc)
                print(f"Post-Hoc Analizi (Tukey HSD) Sonuclari:")
                tukey = pairwise_tukeyhsd(endog=df['F1_Score'], groups=df[dim], alpha=0.05)
                # Tabloyu yazdir
                print(tukey.summary())
            
            else:
                # Sadece 2 grup varsa (Ornegin Input: Flux vs Flux_plus_Coeff): Mann-Whitney U
                print(f"Ikili Karsilastirma (Mann-Whitney U) Sonuclari:")
                g1_name, g2_name = group_names[0], group_names[1]
                g1_data = df[df[dim] == g1_name]['F1_Score']
                g2_data = df[df[dim] == g2_name]['F1_Score']
                u_stat, p_mw = stats.mannwhitneyu(g1_data, g2_data)
                
                print(f"   {g1_name} vs {g2_name}:")
                print(f"   p-value = {p_mw:.4e}")
                print(f"   Ortalama F1 Farkı: {g1_data.mean() - g2_data.mean():.4f}")
        
        else:
            print(f"Sonuc: {dim} gruplari arasinda biyolojik sadakat acisindan anlamli bir fark yok.")
        
        print("\n" + "-" * 85)

    print("\nDENETIM TAMAMLANDI.")

if __name__ == "__main__":
    # Pandas cikti ayarlari
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    
    run_ground_truth_statistical_audit()