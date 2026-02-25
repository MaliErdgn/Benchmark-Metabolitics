import pandas as pd
import glob
import os

def merge_features_filtered(top_n=100):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    feat_dir = os.path.join(project_root, "2_Features")
    output_dir = os.path.join(project_root, "6_Processed_Data")
    # Dosya adını 'TOP100' olarak güncelledik
    output_file = os.path.join(output_dir, f"MASTER_FEATURES_TOP{top_n}.csv")

    all_feat_files = glob.glob(os.path.join(feat_dir, "FEATURES_*.csv"))
    if not all_feat_files:
        print("❌ HATA: Features klasöründe dosya bulunamadı!")
        return

    print(f"🚀 Master Feature Toparlama (Top {top_n} Filtrelemeli)...")
    
    final_list = []

    for f in all_feat_files:
        ds_name = os.path.basename(f).replace("FEATURES_", "").replace(".csv", "")
        print(f"   -> İşleniyor: {ds_name}...", end=" ", flush=True)
        
        try:
            # low_memory=False ve dtype belirterek Warning'i engelliyoruz
            # Density sütunu genellikle 5. veya 6. sütundur (Dens)
            df = pd.read_csv(f, low_memory=False, dtype={'Dens': str, 'Density': str})
            
            if 'Dataset' not in df.columns:
                df['Dataset'] = ds_name

            # Mutlak değer (Abs_Importance) üzerinden sıralama yapmak için (varsa)
            # Yoksa Imp üzerinden devam et
            sort_col = 'Imp'
            df[sort_col] = df[sort_col].abs()

            # --- KRİTİK FİLTRELEME ---
            # Her bir deney grubundaki en iyi 100 özelliği seç
            group_cols = ['Dataset', 'Method', 'Res', 'Input', 'Sel', 'Dens', 'Model']
            
            # Mevcut olan gruplama sütunlarını bul
            existing_groups = [c for c in group_cols if c in df.columns]
            
            # Grupla ve her gruptan en büyük n tanesini al
            df_top = df.groupby(existing_groups, as_index=False).apply(lambda x: x.nlargest(top_n, sort_col)).reset_index(drop=True)
            
            final_list.append(df_top)
            print(f"✅ (Filtrelendi: {len(df_top):,} satır)")
            
            del df # RAM'i boşalt
            
        except Exception as e:
            print(f"❌ HATA: {e}")

    if final_list:
        print(f"⏳ Filtrelenmiş veriler birleştiriliyor...")
        final_df = pd.concat(final_list, ignore_index=True)
        final_df.to_csv(output_file, index=False)
        print(f"✅ BİTTİ: {output_file} (Toplam Satır: {len(final_df):,})")
    else:
        print("⚠️ Birleştirilecek veri bulunamadı.")

if __name__ == "__main__":
    # Literatür analizi için Top 100 yeterlidir, istersen 50 de yapabilirsin.
    merge_features_filtered(top_n=100)