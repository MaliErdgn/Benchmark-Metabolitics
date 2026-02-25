import pandas as pd
import os

# =============================================================================
# YAPILANDIRMA
# =============================================================================
FILE_PATH = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\MARKERDB_ULTIMATE_DATABASE.csv"

def audit_database_quality():
    if not os.path.exists(FILE_PATH):
        print(f"❌ HATA: Dosya bulunamadı -> {FILE_PATH}")
        return

    print(f"🚀 MarkerDB Ultimate Database Denetleniyor...")
    print(f"📍 Dosya: {os.path.basename(FILE_PATH)}\n")

    # Veriyi yükle
    df = pd.read_csv(FILE_PATH)
    total_rows = len(df)

    # İstatistik Tablosu Hazırla
    audit_stats = []

    for col in df.columns:
        filled_count = df[col].count() # Non-null count
        missing_count = total_rows - filled_count
        fill_rate = (filled_count / total_rows) * 100
        unique_values = df[col].nunique()
        
        # Örnek değer (ilk dolu değeri al)
        sample = df[col].dropna().iloc[0] if filled_count > 0 else "N/A"

        audit_stats.append({
            "Column": col,
            "Filled": filled_count,
            "Missing": missing_count,
            "Fill_Rate_%": round(fill_rate, 2),
            "Unique_Items": unique_values,
            "Sample_Data": str(sample)[:30] # Çok uzunsa kes
        })

    # DataFrame Olarak Yazdır
    report_df = pd.DataFrame(audit_stats)
    
    print("="*100)
    print(f"{'COLUMN NAME':<18} | {'FILLED':<8} | {'MISSING':<8} | {'FILL %':<10} | {'UNIQUE':<8} | {'SAMPLE'}")
    print("-" * 100)
    
    for _, row in report_df.iterrows():
        print(f"{row['Column']:<18} | {row['Filled']:<8} | {row['Missing']:<8} | {row['Fill_Rate_%']:<10}% | {row['Unique_Items']:<8} | {row['Sample_Data']}")
    
    print("="*100)
    print(f"📊 TOPLAM KAYIT: {total_rows}")
    print(f"🧬 BENZERSİZ HASTALIK: {df['Disease_Name'].nunique() if 'Disease_Name' in df.columns else 'N/A'}")
    print(f"🧪 BENZERSİZ MARKER  : {df['MDBID'].nunique() if 'MDBID' in df.columns else 'N/A'}")
    print("="*100)

    # Kritik Uyarı: HMDB ID doluluk oranı makale için en önemli metriktir
    if 'HMDB_ID' in df.columns:
        hmdb_fill = report_df[report_df['Column'] == 'HMDB_ID']['Fill_Rate_%'].values[0]
        if hmdb_fill < 50:
            print(f"⚠️ UYARI: HMDB_ID doluluk oranı düşük (%{hmdb_fill}). Validasyon başarısı etkilenebilir.")
        else:
            print(f"✅ GÜVENLİ: HMDB_ID doluluk oranı yüksek (%{hmdb_fill}).")

if __name__ == "__main__":
    audit_database_quality()