import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import fdrcorrection
import warnings

# Gereksiz uyarilari gizle
warnings.filterwarnings("ignore")

# Dosya yolu ayari (Kendi dosya adiniza/yolunuza gore degistirin)
FILE_PATH = "7_Transcriptomic_Data/PMC4187326_BRCA.tpm.gene_symbol.csv"

def run_deg_analysis():
    print("Veri seti yukleniyor, lutfen bekleyin...")
    # Ilk sutunu (gen isimleri) index olarak ayarliyoruz
    try:
        df = pd.read_csv(FILE_PATH, index_col=0)
    except FileNotFoundError:
        print(f"Hata: {FILE_PATH} bulunamadi. Lutfen dosya adini kontrol edin.")
        return

    print("Sutunlar TCGA barkod kuralina gore analiz ediliyor...")
    tumor_cols = []
    normal_cols = []

    for col in df.columns:
        # Noktalari tire ile degistirip standart TCGA formatina (TCGA-XX-XXXX-01A) ceviriyoruz
        parts = col.replace('.', '-').split('-')
        
        # Eger gecerli bir TCGA barkoduysa (en az 4 parca iceriyorsa)
        if "TCGA" in col.upper() and len(parts) >= 4:
            # 4. parca ornek tipini belirtir (01A, 11A vb.)
            sample_code_str = parts[3][:2] 
            
            if sample_code_str.isdigit():
                sample_code = int(sample_code_str)
                if 1 <= sample_code <= 9:
                    tumor_cols.append(col)
                elif 10 <= sample_code <= 19:
                    normal_cols.append(col)
        else:
            # TCGA formati degilse, duz metin aramasi yap
            if 'TUMOR' in col.upper() or ' T ' in col.upper():
                tumor_cols.append(col)
            elif 'NORMAL' in col.upper() or ' N ' in col.upper():
                normal_cols.append(col)

    print(f"Tespit edilen Tumor ornegi sayisi: {len(tumor_cols)}")
    print(f"Tespit edilen Normal ornek sayisi: {len(normal_cols)}")

    if len(tumor_cols) == 0 or len(normal_cols) == 0:
        print("Hata: Tumor veya Normal gruplarindan biri bos. Sutun isimlerini kontrol edin.")
        return

    print("Ortalamalar, LogFC ve P-value hesaplaniyor...")
    # Sadece ilgili sutunlari al
    tumor_data = df[tumor_cols]
    normal_data = df[normal_cols]

    # Ortalamalari hesapla ve sifira bolunmeyi onlemek icin 0.001 ekle
    tumor_mean = tumor_data.mean(axis=1) + 0.001
    normal_mean = normal_data.mean(axis=1) + 0.001

    # Log2 Fold Change hesapla
    logFC = np.log2(tumor_mean / normal_mean)

    # Bagimsiz 2 orneklem t-testi (Vektorize olarak tum satirlara uygular)
    # equal_var=False (Welch's t-test) ekspresyon verileri icin daha guvenilirdir
    t_stats, p_values = stats.ttest_ind(tumor_data, normal_data, axis=1, equal_var=False, nan_policy='omit')

    # Sonuclari bir DataFrame'de topla
    deg_results = pd.DataFrame({
        'gene_symbol': df.index,
        'Tumor_Mean': tumor_mean.values,
        'Normal_Mean': normal_mean.values,
        'logFC': logFC.values,
        'p_value': p_values
    })

    # P-value'su hesaplanamayan (NaN) satirlari temizle veya p=1 olarak doldur
    # FDR hesaplamasi NaN degerlerde hata verir
    deg_results['p_value'] = deg_results['p_value'].fillna(1.0)

    print("FDR (Benjamini-Hochberg) duzeltmesi uygulaniyor...")
    # FDR hesapla
    rejected, fdr_values = fdrcorrection(deg_results['p_value'], alpha=0.05)
    deg_results['FDR'] = fdr_values

    # Sonuclari FDR degerine gore kucukten buyuge (en anlamlilar en uste) sirala
    deg_results = deg_results.sort_values('FDR', ascending=True).reset_index(drop=True)

    # Dosyaya kaydet
    output_filename = 'BRCA_DEG_Results.csv'
    deg_results.to_csv(output_filename, index=False)
    print(f"Islem tamamlandi! Sonuclar '{output_filename}' adli dosyaya kaydedildi.")

    print("\n---------------------------------------------------------")
    print("EN ANLAMLI (FDR DEGERI EN DUSUK) ILK 10 GEN")
    print("---------------------------------------------------------")
    # Pandas gosterim ayarlari (Tum sutunlari gostermesi icin)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(deg_results.head(10).to_string(index=False))

if __name__ == "__main__":
    run_deg_analysis()