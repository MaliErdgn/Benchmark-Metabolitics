import pandas as pd
import cobra
import json
import os
import warnings

warnings.filterwarnings("ignore")

# =============================================================================
# AYARLAR VE DOSYA YOLLARI
# =============================================================================
DEG_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\GSE37751_DEG_Results.csv"
MAPPING_FILE = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\new-synonym-mapping.json"

# Lutfen Recon3D modelinizin bulundugu tam yolu buraya yazin (xml, mat veya json)
MODEL_PATH = r"C:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data\Recon3D.json"

# Incelemek istedigimiz hedef yolaklar (Literatur ve Modelin sectikleri)
TARGET_PATHWAYS = [
    'Alanine and aspartate metabolism',
    'Arginine and proline metabolism',
    'Taurine and hypotaurine metabolism',
    'Glutathione metabolism',
    'Glycolysis/gluconeogenesis',
    'Biotin metabolism',
    'Eicosanoid metabolism'
]

def load_mapping_dict(filepath):
    """
    JSON dosyasini okur ve gen mapping icin cift yonlu bir sozluk olusturur.
    Boylece JSON'un key-value yonu (Entrez->Symbol veya Symbol->Entrez) fark etmeksizin calisir.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_map = json.load(f)
    
    bidirectional_map = {}
    for k, v in raw_map.items():
        k_clean = str(k).strip().upper()
        v_clean = str(v).strip().upper()
        bidirectional_map[k_clean] = v_clean
        bidirectional_map[v_clean] = k_clean
        
    return bidirectional_map

def run_pathway_deg_validation():
    print("ADIM 1: Transkriptomik (DEG) verisi yukleniyor...")
    try:
        deg_df = pd.read_csv(DEG_FILE)
    except FileNotFoundError:
        print(f"Hata: {DEG_FILE} bulunamadi.")
        return
        
    deg_df['gene_symbol_upper'] = deg_df['gene_symbol'].astype(str).str.upper()
    significant_genes = set(deg_df[deg_df['FDR'] < 0.05]['gene_symbol_upper'])
    measured_genes = set(deg_df['gene_symbol_upper'])
    
    print(f"   -> Toplam olculen gen: {len(measured_genes)}")
    print(f"   -> FDR < 0.05 olan anlamli gen: {len(significant_genes)}")
    
    print("\nADIM 2: JSON Mapping dosyasi yukleniyor...")
    try:
        gene_mapper = load_mapping_dict(MAPPING_FILE)
        print(f"   -> Mapping yuklendi. Toplam {len(gene_mapper)} cift yonlu kural olusturuldu.")
    except Exception as e:
        print(f"   Hata: Mapping dosyasi okunamadi: {e}")
        return

    print("\nADIM 3: Recon3D Modeli yukleniyor (Bu islem biraz surebilir)...")
    try:
        if MODEL_PATH.endswith('.mat'):
            model = cobra.io.load_matlab_model(MODEL_PATH)
        elif MODEL_PATH.endswith('.json'):
            model = cobra.io.load_json_model(MODEL_PATH)
        else:
            model = cobra.io.read_sbml_model(MODEL_PATH)
    except Exception as e:
        print(f"   Hata: Model yuklenemedi: {e}")
        return

    print("\nADIM 4: GPR Kurallari ve Overlap Analizi (Ali Hoca - Madde 1a)")
    print("-" * 80)
    
    results = []
    
    for pathway in TARGET_PATHWAYS:
        rxns_in_pathway = [r for r in model.reactions if str(r.subsystem).lower() == pathway.lower()]
        
        if not rxns_in_pathway:
            continue
            
        pathway_genes_mapped = set()
        
        for rxn in rxns_in_pathway:
            for gene in rxn.genes:
                # Recon3D formatindaki '801.1' gibi ID'leri temizle -> '801'
                clean_id = str(gene.id).split('.')[0].upper()
                
                # Mapping sozlugunden karsiligini bul (Bulamazsa orijinalini birak)
                mapped_symbol = gene_mapper.get(clean_id, clean_id)
                pathway_genes_mapped.add(mapped_symbol)
                
        if not pathway_genes_mapped:
            continue
            
        mapped_in_deg = pathway_genes_mapped.intersection(measured_genes)
        
        if not mapped_in_deg:
            continue
            
        sig_mapped_genes = mapped_in_deg.intersection(significant_genes)
        
        overlap_pct = (len(sig_mapped_genes) / len(mapped_in_deg)) * 100
        
        results.append({
            'Pathway': pathway,
            'Total_Model_Genes': len(pathway_genes_mapped),
            'Genes_Found_in_DEG': len(mapped_in_deg),
            'Significant_Genes': len(sig_mapped_genes),
            'Overlap_Percentage': round(overlap_pct, 2)
        })
        
    if results:
        res_df = pd.DataFrame(results).sort_values('Overlap_Percentage', ascending=False)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(res_df.to_string(index=False))
        
        output_csv = "Pathway_DEG_Validation_Results.csv"
        res_df.to_csv(output_csv, index=False)
        print(f"\nIslem tamamlandi. Sonuclar '{output_csv}' dosyasina kaydedildi.")
    else:
        print("Raporlanacak gecerli bir sonuc bulunamadi. Mapping dogrulugunu kontrol edin.")

if __name__ == "__main__":
    run_pathway_deg_validation()