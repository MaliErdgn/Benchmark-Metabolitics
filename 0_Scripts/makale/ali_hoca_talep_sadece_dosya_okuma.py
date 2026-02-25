import pandas as pd
import os

# Ayarlar (Lutfen kendi klasor yolunuzu girin)
DATA_DIR = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\7_Transcriptomic_Data"
FILE_NAME = "PMC4187326_BRCA.tpm.gene_symbol.csv"
FILE_PATH = os.path.join(DATA_DIR, FILE_NAME)

def explore_dataset():
    print("ADIM 1: Veri Seti Sutunlari Inceleniyor...")
    print("-" * 70)
    
    try:
        # Bellek tasarrufu icin sadece ilk 5 satiri okuyoruz
        df = pd.read_csv(FILE_PATH, nrows=5)
        columns = df.columns.tolist()
        
        print("Ilk 10 Sutun Basligi:")
        for i, col in enumerate(columns[:10]):
            print(f"{i+1}. {col}")
            
        print("\nADIM 2: Tumor/Normal Ayrimi Icin Kalip Analizi...")
        print("-" * 70)
        
        # Basit kelime eslesmesi kontrolu
        tumor_keywords = ['tumor', 'tumour', 't', 'case', 'disease']
        normal_keywords = ['normal', 'n', 'control', 'healthy', 'ctrl']
        
        tumor_cols = [c for c in columns if any(kw in str(c).lower() for kw in tumor_keywords)]
        normal_cols = [c for c in columns if any(kw in str(c).lower() for kw in normal_keywords)]
        
        print(f"Icerisinde 'Tumor' vb. kelimeler barindiran sutun sayisi: {len(tumor_cols)}")
        print(f"Icerisinde 'Normal' vb. kelimeler barindiran sutun sayisi: {len(normal_cols)}")
        
        # TCGA Barkod Kontrolu (Ozel Biyoinformatik Kurali)
        tcga_cols = [c for c in columns if str(c).startswith("TCGA-")]
        if len(tcga_cols) > 0:
            print("\nOzel Durum Tespit Edildi: TCGA barkodlari kullaniliyor.")
            print("TCGA formatinda 14. ve 15. karakterler ornek tipini belirler:")
            print("- '01' ile '09' arasi: Tumor (Orn: TCGA-XX-XXXX-01A)")
            print("- '10' ile '19' arasi: Normal (Orn: TCGA-XX-XXXX-11A)")
            
    except Exception as e:
        print(f"Dosya okuma hatasi: {e}")
        
    print("\nADIM 3: Metadata / Klinik Veri Kontrolu...")
    print("-" * 70)
    
    try:
        all_files = os.listdir(DATA_DIR)
        meta_keywords = ['meta', 'clin', 'anno', 'pheno', 'design', 'sample', 'info']
        
        meta_files = [f for f in all_files if any(kw in f.lower() for kw in meta_keywords) and f != FILE_NAME]
        
        if meta_files:
            print("Ayni klasorde metadata/klinik veri olabilecek su dosyalar bulundu:")
            for mf in meta_files:
                print(f"- {mf}")
        else:
            print("Klasorde isim bazli belirgin bir metadata veya klinik veri dosyasi bulunamadi.")
            
    except Exception as e:
        print(f"Klasor okuma hatasi: {e}")

if __name__ == "__main__":
    explore_dataset()