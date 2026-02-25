import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import fdrcorrection
import warnings

# Gereksiz uyarilari gizle
warnings.filterwarnings("ignore")

# Dosya yollari (Ayni dizinde olduklari varsayilmistir)
EXPR_FILE = "7_Transcriptomic_Data/GSE37751.hugene10st.gene_symbol.csv"
META_FILE = "7_Transcriptomic_Data\MasterMapping_MetImmune_03_16_2022_release.csv"
OUTPUT_FILE = "GSE37751_DEG_Results.csv"

def run_deg_analysis():
    print("Metadata dosyasi yukleniyor ve eslesmeler hazirlaniyor...")
    try:
        meta_df = pd.read_csv(META_FILE)
    except FileNotFoundError:
        print(f"Hata: {META_FILE} bulunamadi.")
        return

    if 'RNAID' not in meta_df.columns or 'TN' not in meta_df.columns:
        print("Hata: Metadata dosyasinda 'RNAID' veya 'TN' sutunu bulunamadi.")
        return

    # RNAID sutununu key, TN sutununu value olacak sekilde bir sozluk olustur.
    # Eslesme hatalarini onlemek icin bosluklari temizleyip buyuk harfe ceviriyoruz.
    meta_dict = dict(zip(
        meta_df['RNAID'].astype(str).str.strip(), 
        meta_df['TN'].astype(str).str.strip().str.upper()
    ))

    print("Ifade verisi yukleniyor...")
    try:
        expr_df = pd.read_csv(EXPR_FILE, index_col=0)
    except FileNotFoundError:
        print(f"Hata: {EXPR_FILE} bulunamadi.")
        return

    tumor_cols = []
    normal_cols = []

    for col in expr_df.columns:
        clean_col = str(col).strip()
        if clean_col in meta_dict:
            status = meta_dict[clean_col]
            # TN sutunundaki olasi 'Tumor' veya 'Normal' kisaltmalarini kapsayacak sekilde kontrol et
            if status in ['T', 'TUMOR', '1']:
                tumor_cols.append(col)
            elif status in ['N', 'NORMAL', '0', 'C', 'CONTROL']:
                normal_cols.append(col)

    print("-" * 60)
    print(f"Eslestirme Sonucu:")
    print(f"Tumor ornegi sayisi: {len(tumor_cols)}")
    print(f"Normal ornek sayisi: {len(normal_cols)}")
    print("-" * 60)

    if len(tumor_cols) == 0 or len(normal_cols) == 0:
        print("Hata: Gruplardan biri bos. Metadata ile ifade verisi arasindaki isimlendirmeleri kontrol edin.")
        return

    print("Ortalamalar, LogFC ve P-value hesaplaniyor...")
    tumor_data = expr_df[tumor_cols]
    normal_data = expr_df[normal_cols]

    # Sifira bolunme hatalarini onlemek icin ortalamalara 0.001 ekleniyor
    tumor_mean = tumor_data.mean(axis=1) + 0.001
    normal_mean = normal_data.mean(axis=1) + 0.001

    # Log2 Fold Change
    logFC = np.log2(tumor_mean / normal_mean)

    # Scipy Welch's t-test (equal_var=False)
    t_stats, p_values = stats.ttest_ind(tumor_data, normal_data, axis=1, equal_var=False, nan_policy='omit')

    # Sonuclari DataFrame olarak birlestir
    deg_results = pd.DataFrame({
        'gene_symbol': expr_df.index,
        'Tumor_Mean': tumor_mean.values,
        'Normal_Mean': normal_mean.values,
        'logFC': logFC.values,
        'p_value': p_values
    })

    # NaN p-value degerlerini FDR hesabinin patlamamasi icin 1.0 ile doldur
    deg_results['p_value'] = deg_results['p_value'].fillna(1.0)

    print("FDR duzeltmesi uygulaniyor...")
    rejected, fdr_values = fdrcorrection(deg_results['p_value'], alpha=0.05)
    deg_results['FDR'] = fdr_values

    # Sonuclari sirala
    deg_results = deg_results.sort_values('FDR', ascending=True).reset_index(drop=True)

    deg_results.to_csv(OUTPUT_FILE, index=False)
    print(f"Islem tamamlandi. Sonuclar '{OUTPUT_FILE}' dosyasina kaydedildi.\n")

    print("EN ANLAMLI ILK 10 GEN:")
    print("-" * 60)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(deg_results.head(10).to_string(index=False))

if __name__ == "__main__":
    run_deg_analysis()