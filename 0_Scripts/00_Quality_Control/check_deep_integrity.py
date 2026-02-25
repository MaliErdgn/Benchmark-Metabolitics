import os
import itertools

def deep_audit():
    # --- 1. PROJE YAPILANDIRMASI (BEKLENENLER) ---
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    DATASETS = ["BC", "PRAD", "BRCA", "PDAC", "Alzheimer", "Diabetes"]
    
    # Metot Listesi (Dosya isimlendirme formatına uygun)
    METHODS = ["baseline_base", "topology_base"]
    METHODS += [f"local_k{k}" for k in range(1, 7)]
    METHODS += [f"robust_sigma_{s}" for s in [0.01, 0.05, 0.1, 0.5]]
    METHODS += [f"atp_atp_{l}" for l in [1.0, 10.0, 50.0, 100.0]]
    METHODS += [f"biomass_bio_{b}" for b in [0.01, 0.05, 0.1, 0.2]]
    
    # Çözünürlükler ve Tipler
    RESOLUTIONS = ["Reaction", "Pathway_mean", "Pathway_median", "Pathway_min", "Pathway_max", "Pathway_sum"]
    TYPES = ["Flux", "Coeff"]

    # Klasör Yolları
    DIRS = {
        "Results": os.path.join(base_dir, "../1_Results"),
        "Runstats": os.path.join(base_dir, "../3_Runstats"),
        "Parquets": os.path.join(base_dir, "../4_Parquets")
    }

    print(f"--- DERİN DENETİM BAŞLIYOR: {base_dir} ---\n")

    # --- 2. DENETİM LİSTELERİ ---
    missing_results = []
    missing_runstats = []
    missing_parquets = []
    
    total_checks = 0

    # --- 3. TARAMA DÖNGÜSÜ ---
    for ds in DATASETS:
        print(f"🔎 Taranıyor: {ds}...", end="\r")
        
        # A) RESULTS KONTROLÜ
        # Beklenen: RESULTS_{Dataset}.csv
        if not os.path.exists(os.path.join(DIRS["Results"], f"RESULTS_{ds}.csv")):
            missing_results.append(ds)
        total_checks += 1

        for method in METHODS:
            # B) RUNSTATS KONTROLÜ
            # Beklenen: {Dataset}_{Method}_RunStats.csv
            stats_name = f"{ds}_{method}_RunStats.csv"
            if not os.path.exists(os.path.join(DIRS["Runstats"], stats_name)):
                missing_runstats.append(stats_name)
            total_checks += 1

            for res in RESOLUTIONS:
                for typ in TYPES:
                    # C) PARQUET KONTROLÜ
                    # Beklenen: 4_Parquets/{Dataset}/{Dataset}_{Method}_{Type}_{Resolution}.parquet
                    # Not: Coeff dosyalarında 'Reaction' harici Pathway varyasyonları da üretmiştik
                    
                    pq_name = f"{ds}_{method}_{typ}_{res}.parquet"
                    pq_path = os.path.join(DIRS["Parquets"], ds, pq_name)
                    
                    if not os.path.exists(pq_path):
                        missing_parquets.append(f"{ds}/{pq_name}")
                    total_checks += 1

    print(f"✅ Tarama Bitti. Toplam {total_checks} dosya/kombinasyon kontrol edildi.\n")

    # --- 4. RAPORLAMA ---
    
    # Rapor 1: Results
    if missing_results:
        print(f"❌ [RESULTS] Eksik Dosyalar ({len(missing_results)}):")
        for f in missing_results: print(f"   - RESULTS_{f}.csv")
    else:
        print("✅ [RESULTS] Tüm dataset sonuçları tam.")

    # Rapor 2: RunStats
    if missing_runstats:
        print(f"\n❌ [RUNSTATS] Eksik Dosyalar ({len(missing_runstats)}):")
        # Çok fazlaysa ilk 5'i göster
        for f in missing_runstats[:5]: print(f"   - {f}")
        if len(missing_runstats) > 5: print(f"   ... ve {len(missing_runstats)-5} tane daha.")
    else:
        print("✅ [RUNSTATS] Tüm istatistik dosyaları (120 adet) tam.")

    # Rapor 3: Parquets
    if missing_parquets:
        print(f"\n❌ [PARQUETS] Eksik Dosyalar ({len(missing_parquets)}):")
        for f in missing_parquets[:10]: print(f"   - {f}")
        if len(missing_parquets) > 10: print(f"   ... ve {len(missing_parquets)-10} tane daha.")
        
        # Analitik Özet (Hangi dataset, hangi metod patlak?)
        print("\n   >> Hata Analizi:")
        miss_ds = set([m.split("_")[0] for m in missing_parquets])
        print(f"   Etkilenen Datasetler: {miss_ds}")
    else:
        print("✅ [PARQUETS] Tüm Parquet dosyaları (1440+ adet) tam ve yerinde.")

    print("\n" + "="*40)
    if not (missing_results or missing_runstats or missing_parquets):
        print("🚀 MÜKEMMEL: Veri seti %100 eksiksiz.")
    else:
        print("⚠️ DİKKAT: Eksikler var, yukarıdaki listeyi kontrol et.")
    print("="*40)

if __name__ == "__main__":
    deep_audit()