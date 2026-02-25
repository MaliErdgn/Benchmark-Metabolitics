import pandas as pd
import glob
import os

def consolidate_data():
    # --- 1. YOL TANIMLAMALARI ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir)) 
    
    results_dir = os.path.join(project_root, "1_Results")
    stats_dir = os.path.join(project_root, "3_Runstats")
    
    # --- YENİ KONUM ---
    output_dir = os.path.join(project_root, "6_Processed_Data")
    os.makedirs(output_dir, exist_ok=True) # Klasörü oluştur
    output_file = os.path.join(output_dir, "MASTER_BENCHMARK_FINAL.csv")

    print(f"--- VERİ BİRLEŞTİRME BAŞLATILIYOR ---")
    print(f"📂 Hedef Klasör: {output_dir}")

    # --- 2. RESULTS DOSYALARINI OKU ---
    res_files = glob.glob(os.path.join(results_dir, "RESULTS_*.csv"))
    if not res_files:
        print("❌ HATA: '1_Results' klasöründe CSV dosyası bulunamadı.")
        return

    all_data = []

    for f in res_files:
        ds_name = os.path.basename(f).replace("RESULTS_", "").replace(".csv", "")
        print(f"   -> İşleniyor: {ds_name}...", end=" ", flush=True)
        
        try:
            df = pd.read_csv(f)
            stats_lookup = {}
            stats_files = glob.glob(os.path.join(stats_dir, f"{ds_name}_*_RunStats.csv"))
            
            for sf in stats_files:
                fname = os.path.basename(sf)
                method_part = fname.replace(f"{ds_name}_", "").replace("_RunStats.csv", "")
                
                try:
                    s_df = pd.read_csv(sf)
                    if not s_df.empty:
                        stats_data = s_df.iloc[0].to_dict()
                        clean_stats = {}
                        for k, v in stats_data.items():
                            if k not in ['Session_ID', 'Dataset', 'Method', 'Parameter_Label']:
                                new_key = k if k.startswith("P1_") else f"P1_{k}"
                                clean_stats[new_key] = v
                        stats_lookup[method_part] = clean_stats
                except: pass

            stat_rows = []
            for method in df['Obj_Method']:
                stat_rows.append(stats_lookup.get(method, {}))
            
            df_stats_ext = pd.DataFrame(stat_rows)
            df_merged = pd.concat([df, df_stats_ext], axis=1)
            all_data.append(df_merged)
            print("✅")

        except Exception as e:
            print(f"❌ HATA: {e}")

    # --- 3. BİRLEŞTİRME VE KAYIT ---
    if all_data:
        master_df = pd.concat(all_data, axis=0, ignore_index=True)
        
        all_cols = list(master_df.columns)
        ideal_order = [
            'Dataset', 'Obj_Method', 'Resolution', 'Input_Type', 
            'ML_Model', 'ML_Selector', 'ML_Density', 
            'F1_Mean', 'F1_Std', 'Acc_Mean', 'AUC_Mean',
            'Selected_Feat_Count', 'ML_Duration_CV_Sec'
        ]
        
        priority = [c for c in ideal_order if c in all_cols]
        remaining = [c for c in all_cols if c not in priority]
        master_df = master_df[priority + remaining]

        master_df.to_csv(output_file, index=False)
        
        print("\n" + "="*50)
        print(f"🚀 İŞLEM TAMAMLANDI")
        print(f"📄 Dosya: {os.path.basename(output_file)}")
        print(f"📊 Satır: {len(master_df):,}")
        
        if 'P1_Total_Duration_Sec' in master_df.columns:
            missing = master_df['P1_Total_Duration_Sec'].isna().sum()
            if isinstance(missing, pd.Series): missing = missing.max()
            print(f"⚠️  Eşleşmeyen P1 Verisi: {missing} satır")
        
        print("="*50)
        
        # Ana dizindeki eski dosyayı temizle (opsiyonel)
        old_root_file = os.path.join(project_root, "MASTER_BENCHMARK_FINAL.csv")
        if os.path.exists(old_root_file):
            os.remove(old_root_file)
            print(f"🗑️  Ana dizindeki eski dosya silindi.")
    else:
        print("❌ Birleştirilecek veri bulunamadı.")

if __name__ == "__main__":
    consolidate_data()