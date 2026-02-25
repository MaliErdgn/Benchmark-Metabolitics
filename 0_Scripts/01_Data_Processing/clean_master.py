import pandas as pd
import os

def clean_master_benchmark():
    # --- 1. YOL TANIMLAMALARI ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    input_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_FINAL.csv")
    output_file = os.path.join(project_root, "6_Processed_Data", "MASTER_BENCHMARK_CLEAN.csv")

    if not os.path.exists(input_file):
        print(f"❌ HATA: {input_file} bulunamadı!")
        return

    # --- 2. VERİ YÜKLEME ---
    print(f"🚀 Veri okunuyor: {input_file}")
    df = pd.read_csv(input_file)
    initial_count = len(df)
    
    # --- 3. STANDARDİZASYON (Pathway -> Pathway_mean) ---
    # 'Pathway' ismini 'Pathway_mean' olarak değiştiriyoruz çünkü ikisi teknik olarak aynı
    print("🧹 'Pathway' etiketleri 'Pathway_mean' olarak standardize ediliyor...")
    df['Resolution'] = df['Resolution'].replace('Pathway', 'Pathway_mean')

    # --- 4. MÜKERRER TEMİZLİĞİ (Deduplication) ---
    # Bir deneyi eşsiz kılan kolonlar kümesi:
    unique_params = [
        'Dataset', 'Obj_Method', 'Resolution', 'Input_Type', 
        'ML_Model', 'ML_Selector', 'ML_Density'
    ]
    
    print("♻️  Mükerrer satırlar temizleniyor (Parametre bazlı)...")
    # keep='first' diyerek ilk rastladığımızı (genelde en güncel olanı) tutuyoruz
    df_clean = df.drop_duplicates(subset=unique_params, keep='first')
    
    final_count = len(df_clean)
    removed_count = initial_count - final_count

    # --- 5. SONUÇLARIN KAYDI ---
    df_clean.to_csv(output_file, index=False)
    
    # --- 6. RAPORLAMA ---
    print("\n" + "="*50)
    print(f"📊 TEMİZLİK RAPORU")
    print("-" * 50)
    print(f"Başlangıç Satır Sayısı  : {initial_count:,}")
    print(f"Silinen Mükerrer Satır : {removed_count:,}")
    print(f"Final (Temiz) Satır    : {final_count:,}")
    print("-" * 50)
    
    # Dataset bazlı kontrol
    print("\nDataset Başına Düşen Deney Sayısı (Beklenen: 9,600):")
    print(df_clean.groupby('Dataset').size())
    
    print("\nÇözünürlük Dağılımı (Standardize Edilmiş):")
    print(df_clean['Resolution'].value_counts())
    
    print("\n✅ İşlem Tamamlandı. Temiz dosya: MASTER_BENCHMARK_CLEAN.csv")
    print("="*50)

if __name__ == "__main__":
    clean_master_benchmark()