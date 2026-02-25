import pandas as pd
import glob
import os

def count_total_results():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "../1_Results")
    
    csv_files = glob.glob(os.path.join(results_dir, "RESULTS_*.csv"))
    
    total_rows = 0
    print(f"--- SONUÇ SATIR SAYIMI ---\n")
    print(f"{'DATASET':<15} | {'SATIR SAYISI':<15}")
    print("-" * 35)
    
    for f in csv_files:
        ds_name = os.path.basename(f).replace("RESULTS_", "").replace(".csv", "")
        try:
            df = pd.read_csv(f)
            count = len(df)
            total_rows += count
            print(f"{ds_name:<15} | {count:<15,}")
        except Exception as e:
            print(f"{ds_name:<15} | HATA ({e})")
            
    print("-" * 35)
    print(f"{'TOPLAM':<15} | {total_rows:<15,}")
    print("=" * 35)
    
    if total_rows > 50000:
        print("\n✅ ONAYLANDI: 50.000'den fazla deney sonucu mevcut.")
    else:
        print("\n⚠️ UYARI: Beklenen sayıdan az.")

if __name__ == "__main__":
    count_total_results()