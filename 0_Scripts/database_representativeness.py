import pandas as pd
import json
import os

# =============================================================================
# YOLLAR
# =============================================================================
BASE_DATA_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data"
OUTPUT_CSV    = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\5_Figures\DATABASE_REPRESENTATIVENESS.csv"
# 'UNIFIED_DISCOVERY_AUDIT_REPORT.txt' içindeki sayıları kullanarak manuel bir tablo da yapabiliriz 
# ama kodla mühürlemek daha iyidir.

def run_database_bias_analysis():
    print("📊 Database Representativeness Audit Starting...")

    # Recon3D'nin toplam kapasitesi (Önceki analizlerimizden biliyoruz)
    TOTAL_RECON_PATHWAYS = 106
    TOTAL_RECON_REACTIONS = 10600

    # UNIFIED_DISCOVERY_AUDIT_REPORT verilerini bir sözlüğe alıyoruz
    # (Az önce çalıştırdığınız scriptin ham verileri)
    audit_data = {
        "Alzheimer": {"clinical_reac": 661, "clinical_path": 62},
        "Diabetes":   {"clinical_reac": 160, "clinical_path": 29},
        "PDAC":       {"clinical_reac": 14,  "clinical_path": 6},
        "PRAD":       {"clinical_reac": 6,   "clinical_path": 4},
        "BC":         {"clinical_reac": 3,   "clinical_path": 3},
        "BRCA":       {"clinical_reac": 3,   "clinical_path": 3}
    }

    results = []

    for ds, counts in audit_data.items():
        # REACTION SEVİYESİ
        reac_rep = (counts['clinical_reac'] / TOTAL_RECON_REACTIONS) * 100
        # PATHWAY SEVİYESİ
        path_rep = (counts['clinical_path'] / TOTAL_RECON_PATHWAYS) * 100

        results.append({
            "Dataset": ds,
            "Total_Model_Pathways": TOTAL_RECON_PATHWAYS,
            "MarkerDB_Known_Pathways": counts['clinical_path'],
            "Pathway_Knowledge_Coverage_%": round(path_rep, 2),
            "MarkerDB_Known_Reactions": counts['clinical_reac'],
            "Reaction_Knowledge_Coverage_%": round(reac_rep, 2)
        })

    df_rep = pd.DataFrame(results)
    
    print("\n" + "="*90)
    print("      DATABASE REPRESENTATIVENESS REPORT: HOW MUCH DOES MARKERDB KNOW?")
    print("="*90)
    print(df_rep.to_string(index=False))
    print("-" * 90)
    print("💡 Interpretation:")
    print("   - Low %: MarkerDB is sparse for this disease. Validation hits will naturally be low.")
    print("   - High %: MarkerDB is rich. Failure to hit these is a true model failure.")
    print("="*90)
    
    df_rep.to_csv(OUTPUT_CSV, index=False)

if __name__ == "__main__":
    run_database_bias_analysis()