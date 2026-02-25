import pandas as pd
import json
import os

# =============================================================================
# YOLLAR
# =============================================================================
MARKERDB_TSV = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\all_chemicals.tsv"
SYNONYM_MAP = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\new-synonym-mapping.json"
ML_FEATURES = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"

def deep_audit_validation():
    print("🔬 Deep Audit: MarkerDB Validation & Mapping Diagnostic Starting...")

    # 1. MARKERDB ANALİZİ: Hastalık İsimleri Neden Bulunmuyor?
    # -------------------------------------------------------------------------
    df_markers = pd.read_csv(MARKERDB_TSV, sep='\t')
    
    # Mevcut tüm conditionları içeren bir liste yapalım (İlk 50 benzersiz kelime)
    all_conds = df_markers['conditions'].dropna().str.split(';').explode().str.strip().unique()
    print(f"\n📂 MarkerDB Analizi:")
    print(f"   -> Toplam Kayıt: {len(df_markers)}")
    print(f"   -> Tespit Edilen Bazı Hastalık İsimleri: {all_conds[:15]}")
    
    # Akıllı Arama: İçinde 'Breast' geçen gerçek condition ismini bulalım
    real_bc_names = [c for c in all_conds if 'breast' in str(c).lower()]
    print(f"   -> 'Breast' içeren gerçek etiketler: {real_bc_names}")
    
    if not real_bc_names:
        print("❌ KRİTİK: MarkerDB dosyasında 'Breast' kelimesi bulunamadı!")
        return

    # 2. MARKERLARI ÇEK (Tüm varyasyonları dahil ederek)
    # -------------------------------------------------------------------------
    bc_markers_df = df_markers[df_markers['conditions'].astype(str).str.contains('|'.join(real_bc_names), case=False, na=False)]
    bc_samples = bc_markers_df[['name', 'hmdb_id']].drop_duplicates()
    print(f"✅ Filtreleme Başarılı: {len(bc_samples)} adet Breast Cancer marker'ı bulundu.")

    # 3. MAPPING (BRIDGING)
    # -------------------------------------------------------------------------
    with open(SYNONYM_MAP, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    normalized_mapping = {str(k).lower().strip(): v for k, v in mapping.items()}

    valid_markers = [] # (Orijinal İsim, ReconID)
    for _, row in bc_samples.iterrows():
        m_name = str(row['name']).lower().strip()
        m_hmdb = str(row['hmdb_id']).lower().strip()
        
        rid = normalized_mapping.get(m_hmdb) or normalized_mapping.get(m_name)
        if rid:
            valid_markers.append((row['name'], rid))

    print(f"🔗 Köprü Kuruldu: {len(valid_markers)} marker Recon3D formatına çevrildi.")

    # 4. ML HIT TEST (REACTION-AWARE SEARCH)
    # -------------------------------------------------------------------------
    df_ml = pd.read_csv(ML_FEATURES, low_memory=False)
    df_bc = df_ml[df_ml['Dataset'] == 'BC']
    
    # ÖNEMLİ: Reaksiyon ID'leri içinde metabolit adı geçmeyebilir. 
    # Ama Pathway isimleri içinde geçebilir veya modellerimiz direkt o yolu bulmuştur.
    # PoC için hem Feat (Reaction) hem de varsa Pathway üzerinden bakacağız.
    
    print("\n🔬 Modellerimizin Keşifleri Kontrol Ediliyor...")
    print("-" * 80)
    
    hit_count = 0
    for original_name, rid in valid_markers[:30]: # İlk 30 taneyi test et
        # A) Reaksiyon isminde ara (Substring)
        match_rxn = df_bc[df_bc['Feat'].str.contains(str(rid), na=False, case=False)]
        
        # B) TODO: İleride reaksiyon-metabolit ilişkisi (S-Matrix) buraya gelecek
        
        if not match_rxn.empty:
            hit_count += 1
            top_m = match_rxn.sort_values('Imp', ascending=False).iloc[0]
            print(f"⭐ [REACTION HIT] '{original_name}' -> Bulunan Reaksiyon: {top_m['Feat']} ({top_m['Method']})")
        else:
            # Alternatif: Pathway isimlerinde ara (Örn: 'Arginine metabolism')
            # Metabolit isminin bir parçasını pathwaylerde ara
            search_term = original_name.split(' ')[-1] # 'Spermidine' gibi
            match_path = df_bc[df_bc['Feat'].str.contains(search_term, na=False, case=False)]
            
            if not match_path.empty:
                hit_count += 1
                top_p = match_path.sort_values('Imp', ascending=False).iloc[0]
                print(f"🍀 [PATHWAY HIT] '{original_name}' -> İlişkili Yol: {top_p['Feat']} ({top_p['Method']})")

    print("-" * 80)
    print(f"📊 SONUÇ: {len(valid_markers)} markerın içinden {hit_count} potansiyel hit yakalandı.")

if __name__ == "__main__":
    deep_audit_validation()