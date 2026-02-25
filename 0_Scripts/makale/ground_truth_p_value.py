import pandas as pd
from scipy import stats
import os

# =============================================================================
# AYARLAR
# =============================================================================
INPUT_FILE = "Full_Density_Biological_Validation.csv"

def run_kruskal_wallis_test():
    print("BASLADI: Kruskal-Wallis H-Testi Analizi")
    print("-" * 60)
    
    # Veri setini kontrol et ve oku
    if not os.path.exists(INPUT_FILE):
        print(f"Hata: '{INPUT_FILE}' dosyasi bulunamadi. Lutfen dosya yolunu kontrol edin.")
        return
        
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Hata: Dosya okunurken bir sorun olustu: {e}")
        return

    # F1_Score sutununun varligini kontrol et
    if 'F1_Score' not in df.columns:
        print("Hata: Veri setinde 'F1_Score' sutunu bulunamadi.")
        return

    # Incelenecek parametreler
    parameters = ['Model', 'Res', 'Method', 'Input', 'Sel']
    
    # Her bir parametre icin analizi dondur
    for param in parameters:
        if param not in df.columns:
            print(f"Parametre: {param}")
            print("Hata: Bu sutun veri setinde bulunamadi, atliyor.")
            print("-" * 60)
            continue
            
        # Parametrenin icindeki her bir alt grup icin F1 skorlarini ayri bir listeye (array) al
        # Ornek: Model parametresi icin RF'nin F1 skorlari bir array, SVM'nin F1 skorlari diger bir array olur
        grouped_data = df.groupby(param)
        groups = [group['F1_Score'].values for name, group in grouped_data]
        group_names = [name for name, group in grouped_data]
        
        # Testin calisabilmesi icin en az 2 karsilastirilabilir grup olmalidir
        if len(groups) < 2:
            print(f"Parametre: {param}")
            print(f"Uyari: Karsilastirma yapmak icin yeterli farkli alt grup yok. (Bulunan gruplar: {group_names})")
            print("-" * 60)
            continue
            
        # Kruskal-Wallis testini uygula
        try:
            h_stat, p_value = stats.kruskal(*groups)
            
            print(f"Parametre: {param}")
            print(f"Incelenen Alt Gruplar: {group_names}")
            print(f"H-istatistigi: {h_stat:.4f}")
            print(f"P-value: {p_value:.4e}")
            
            # Anlamlilik kontrolu
            if p_value < 0.05:
                print("Sonuc: Fark Istatistiksel Olarak Anlamli (p < 0.05)")
            else:
                print("Sonuc: Anlamli Bir Fark Yok")
                
        except Exception as e:
            print(f"Parametre: {param}")
            print(f"Test sirasinda hata olustu: {e}")
            
        print("-" * 60)

if __name__ == "__main__":
    run_kruskal_wallis_test()