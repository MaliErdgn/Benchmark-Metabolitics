import pandas as pd

# 1. Dosyayi oku (Kendi dosya yolunu buraya yaz, eger ayni klasordeyse direkt ismini yazabilirsin)
df = pd.read_csv('Full_Density_Biological_Validation.csv')

# 2. Incelemek istedigimiz ana parametreler (Sutun isimleri CSV'de varsa analize dahil edilir)
parameters_to_analyze = ['Model', 'Res', 'Method', 'Input', 'Sel']
available_params = [col for col in parameters_to_analyze if col in df.columns]

print("=== PARAMETRE BAZINDA ORTALAMA VE MAKSIMUM F1 SKORLARI ===")

for param in available_params:
    print(f"\n--- {param} Performansi ---")
    
    # Parametreye gore grupla, F1_Score'un ortalamasini ve en yuksek (max) degerini bul
    summary = df.groupby(param)['F1_Score'].agg(['mean', 'max']).reset_index()
    
    # Ortalama F1 skoruna gore buyukten kucuge sirala
    summary = summary.sort_values(by='mean', ascending=False)
    
    # Sutun isimlerini duzenle ve yazdir
    summary.rename(columns={'mean': 'Avg_F1', 'max': 'Max_F1'}, inplace=True)
    
    # Sonuclari yuvarla
    summary['Avg_F1'] = summary['Avg_F1'].round(3)
    summary['Max_F1'] = summary['Max_F1'].round(3)
    
    print(summary.to_string(index=False))