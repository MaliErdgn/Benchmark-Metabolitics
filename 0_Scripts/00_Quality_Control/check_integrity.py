import os
import glob
import pandas as pd
import random

def check_integrity():
    # Klasör Yolları (Anlaştığımız yapıya göre)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dirs = {
        "Results": os.path.join(base_dir, "../1_Results"),
        "Features": os.path.join(base_dir, "../2_Features"),
        "Runstats": os.path.join(base_dir, "../3_Runstats"),
        "Parquets": os.path.join(base_dir, "../4_Parquets")
    }

    print(f"--- BAŞLANGIÇ DİZİNİ: {base_dir} ---\n")
    
    # 1. Klasör Varlık Kontrolü
    missing_dirs = [d for n, d in dirs.items() if not os.path.exists(d)]
    if missing_dirs:
        print(f"❌ KRİTİK HATA: Şu klasörler bulunamadı: {missing_dirs}")
        return
    print("✅ Tüm ana klasörler mevcut.")

    # 2. Results Dosyaları Kontrolü
    res_files = glob.glob(os.path.join(dirs["Results"], "RESULTS_*.csv"))
    datasets_res = [os.path.basename(f).replace("RESULTS_", "").replace(".csv", "") for f in res_files]
    print(f"\n📊 1_Results Klasörü:")
    print(f"   -> Bulunan Dosya Sayısı: {len(res_files)}")
    print(f"   -> Tespit Edilen Datasetler: {sorted(datasets_res)}")

    # 3. Features Dosyaları Kontrolü
    feat_files = glob.glob(os.path.join(dirs["Features"], "FEATURES_*.csv"))
    datasets_feat = [os.path.basename(f).replace("FEATURES_", "").replace(".csv", "") for f in feat_files]
    print(f"\n📊 2_Features Klasörü:")
    print(f"   -> Bulunan Dosya Sayısı: {len(feat_files)}")
    
    # 4. Çapraz Eşleşme (Consistency Check)
    missing_features = set(datasets_res) - set(datasets_feat)
    if missing_features:
        print(f"❌ UYARI: Şu datasetlerin 'Results' dosyası var ama 'Features' dosyası YOK: {missing_features}")
    else:
        print("✅ Results ve Features datasetleri birebir eşleşiyor.")

    # 5. RunStats Kontrolü
    stats_files = glob.glob(os.path.join(dirs["Runstats"], "*_RunStats.csv"))
    print(f"\n📊 3_Runstats Klasörü:")
    print(f"   -> Toplam İstatistik Dosyası: {len(stats_files)}")
    if len(stats_files) < 100:
        print("⚠️ UYARI: RunStats dosya sayısı beklenenden az (Beklenen: ~120). Eksik kopyalama olabilir.")

    # 6. Okuma Testi (Sanity Check)
    print("\n🧪 Okuma Testleri (Random Sampling):")
    
    # CSV Testi
    try:
        test_csv = random.choice(res_files)
        df = pd.read_csv(test_csv)
        print(f"   ✅ CSV Okuma Başarılı: {os.path.basename(test_csv)} (Satır: {len(df)})")
    except Exception as e:
        print(f"   ❌ CSV Okuma Hatası: {e}")

    # Parquet Testi
    try:
        parquet_files = glob.glob(os.path.join(dirs["Parquets"], "**", "*.parquet"), recursive=True)
        if parquet_files:
            test_pq = random.choice(parquet_files)
            df_pq = pd.read_parquet(test_pq)
            print(f"   ✅ Parquet Okuma Başarılı: {os.path.basename(test_pq)} (Şekil: {df_pq.shape})")
        else:
            print("   ⚠️ UYARI: Hiç Parquet dosyası bulunamadı (Klasör boş olabilir).")
    except Exception as e:
        print(f"   ❌ Parquet Okuma Hatası: {e} (pyarrow/fastparquet kurulu mu?)")

    print("\n" + "="*40)
    print("BÜTÜNLÜK KONTROLÜ TAMAMLANDI")
    print("="*40)

if __name__ == "__main__":
    check_integrity()