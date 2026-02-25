import pandas as pd
import numpy as np

# =============================================================================
# AYARLAR
# =============================================================================
INPUT_FILE = "Final_Transcriptomic_Validation_Results.csv"

def run_global_trend_analysis():
    # Dosya okuma
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Hata: {INPUT_FILE} dosyasi bulunamadi. Lutfen once validasyon kodunu calistirin.")
        return

    # Sayisal sutunlarin varligini kontrol et
    target_metrics = ['Overlap_Percent', 'Significant_Genes']
    for metric in target_metrics:
        if metric not in df.columns:
            print(f"Hata: Veri setinde '{metric}' sutunu bulunamadi.")
            return

    # Analiz edilecek boyutlar
    dimensions = ['Res', 'Method', 'Model', 'Dataset']

    print("TRANSKRIPTOMIK VALIDASYON: GLOBAL TREND RAPORU")
    print("=" * 70)

    for dim in dimensions:
        if dim not in df.columns:
            print(f"Uyari: '{dim}' sutunu veri setinde bulunamadigi icin atlaniyor.")
            continue

        print(f"\nBOYUT: {dim}")
        print("-" * 70)

        # Gruplama ve ortalama hesaplama
        # Overlap_Percent sutununa gore buyukten kucuge siralama
        summary = df.groupby(dim)[target_metrics].mean().sort_values('Overlap_Percent', ascending=False)
        
        # Sonuclari ekrana yazdirma
        print(summary)
        print("-" * 70)

    # Ozel bir gozlem: Cozunurluk (Res) icindeki en iyi ve en kotu farkini hesapla
    if 'Res' in df.columns:
        res_summary = df.groupby('Res')['Overlap_Percent'].mean()
        max_res = res_summary.idxmax()
        min_res = res_summary.idxmin()
        gap = res_summary.max() - res_summary.min()
        
        print("\nOZET TESPIT:")
        print(f"En yuksek biyolojik ortusme saglayan cozunurluk: {max_res} (%{res_summary.max():.2f})")
        print(f"En dusuk biyolojik ortusme saglayan cozunurluk: {min_res} (%{res_summary.min():.2f})")
        print(f"Cozunurlukler arasi maksimum performans farki: %{gap:.2f}")

if __name__ == "__main__":
    run_global_trend_analysis()