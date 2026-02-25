import pandas as pd
import os

# =============================================================================
# YAPILANDIRMA
# =============================================================================
FEAT_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MASTER_FEATURES_TOP100.csv"

def run_importance_impact_audit():
    print("⚖️ IMPACT AUDIT: Do Coefficients Punch Harder Than Fluxes?")
    
    if not os.path.exists(FEAT_FILE):
        print("❌ Dosya bulunamadı.")
        return

    # 1. VERİ YÜKLE
    df = pd.read_csv(FEAT_FILE, low_memory=False)
    
    # Sadece hibrit girdiyi al (Yarışın olduğu yer)
    input_col = 'Input' if 'Input' in df.columns else 'Input_Type'
    if input_col in df.columns:
        df = df[df[input_col] == 'Flux_plus_Coeff']

    # 2. TİP AYRIMI
    df['Type'] = df['Feat'].apply(lambda x: 'Coefficient (Cr)' if str(x).startswith('Coeff_') else 'Raw Flux')

    # 3. ÖNEM PUANI (IMPORTANCE) ANALİZİ
    # Seçilen özelliklerin ortalama 'Imp' değeri nedir?
    print("\n[1] MEAN IMPORTANCE SCORE PER TYPE")
    print("(Higher score = Greater contribution to the decision boundary)")
    
    imp_stats = df.groupby('Type')['Imp'].agg(['mean', 'median', 'std', 'count'])
    print(imp_stats)
    
    # 4. HASTALIK BAZLI ETKİ GÜCÜ
    print("\n[2] IMPACT BY DISEASE (Mean Importance)")
    ds_imp = df.pivot_table(index='Dataset', columns='Type', values='Imp', aggfunc='mean')
    ds_imp['Cr_Impact_Ratio'] = ds_imp['Coefficient (Cr)'] / ds_imp['Raw Flux']
    print(ds_imp.sort_values('Cr_Impact_Ratio', ascending=False))

    # 5. KANIT CÜMLESİ İÇİN VERİ
    global_cr_imp = imp_stats.loc['Coefficient (Cr)', 'mean']
    global_flux_imp = imp_stats.loc['Raw Flux', 'mean']
    
    print("\n" + "="*80)
    if global_cr_imp > global_flux_imp:
        print(f"✅ KANITLANDI: Katsayıların etki gücü ({global_cr_imp:.4f}), akışlardan ({global_flux_imp:.4f}) daha yüksek.")
        print(f"   -> Katsayılar model kararında {(global_cr_imp/global_flux_imp):.2f} kat daha etkili.")
    else:
        print(f"⚠️ DİKKAT: Katsayılar çok seçiliyor ama etki güçleri daha düşük.")
    print("="*80)

if __name__ == "__main__":
    run_importance_impact_audit()