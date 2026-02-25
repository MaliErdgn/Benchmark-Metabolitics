import pandas as pd
import os

# =============================================================================
# YAPILANDIRMA
# =============================================================================
FEAT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"

def run_flux_vs_coeff_showdown():
    print("🥊 Flux vs. Coefficient: Head-to-Head Selection Analysis...")
    
    if not os.path.exists(FEAT_FILE):
        print("❌ Dosya bulunamadı.")
        return

    # 1. VERİ YÜKLEME
    df = pd.read_csv(FEAT_FILE, low_memory=False)
    
    # Sadece ikisinin de yarıştığı ortamı alıyoruz: 'Flux_plus_Coeff'
    # (Sütun adı 'Input' veya 'Input_Type' olabilir, kontrol ediyoruz)
    input_col = 'Input' if 'Input' in df.columns else 'Input_Type'
    if input_col in df.columns:
        df = df[df[input_col] == 'Flux_plus_Coeff']
    
    # 2. İSİM NORMALİZASYONU
    # 'Coeff_Glutathione...' ile 'Glutathione...' aynı köke sahip olmalı.
    def normalize_name(feat_name):
        if str(feat_name).startswith("Coeff_"):
            return str(feat_name).replace("Coeff_", ""), "Coeff"
        return str(feat_name), "Flux"

    # Apply ile iki yeni sütun oluştur: 'Base_Name' ve 'Type'
    df[['Base_Name', 'Type']] = df['Feat'].apply(lambda x: pd.Series(normalize_name(x)))

    # 3. SAYIM (COUNTING)
    # Her özellik (Base_Name) kaç kere Flux, kaç kere Coeff olarak seçilmiş?
    pivot = df.pivot_table(index='Base_Name', columns='Type', aggfunc='size', fill_value=0)
    
    # Sadece Coeff veya Flux olarak EN AZ 100 kere seçilmişleri alalım (Gürültüyü at)
    pivot = pivot[(pivot['Coeff'] > 100) | (pivot['Flux'] > 100)]
    
    # Oran Hesapla (Ratio > 1 ise Coeff kazanmış demektir)
    pivot['Ratio (C/F)'] = pivot['Coeff'] / (pivot['Flux'] + 1) # +1 sıfıra bölünme hatası için
    pivot['Total_Selections'] = pivot['Coeff'] + pivot['Flux']
    
    # 4. SIRALAMA VE RAPORLAMA
    # En çok Coeff tercih edilenleri üste alalım
    top_coeff_winners = pivot.sort_values(by='Coeff', ascending=False).head(15)

    print("\n" + "="*100)
    print("      HEAD-TO-HEAD: WHICH FORM DOES THE MODEL PREFER?")
    print("      (Data from Flux_plus_Coeff experiments only)")
    print("="*100)
    print(f"{'FEATURE NAME':<50} | {'COEFF (Count)':<12} | {'FLUX (Count)':<12} | {'RATIO (C/F)':<10}")
    print("-" * 100)
    
    for name, row in top_coeff_winners.iterrows():
        ratio_str = f"{row['Ratio (C/F)']:.1f}x"
        print(f"{name:<50} | {row['Coeff']:<12} | {row['Flux']:<12} | {ratio_str:<10}")

    print("="*100)
    
    # Global İstatistik
    total_c = pivot['Coeff'].sum()
    total_f = pivot['Flux'].sum()
    print(f"\n🌍 GLOBAL SKOR:")
    print(f"   Toplam Coeff Seçimi : {total_c}")
    print(f"   Toplam Flux Seçimi  : {total_f}")
    print(f"   Genel Tercih Oranı  : {total_c/total_f:.2f}x (Coefficient lehine)")

if __name__ == "__main__":
    run_flux_vs_coeff_showdown()