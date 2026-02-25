import pandas as pd
import json
import os
import re
import glob

# =============================================================================
# YOLLAR
# =============================================================================
BASE_DATA_DIR = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\6_Processed_Data"
FEAT_DIR      = r"c:\Users\Mali\My Drive\M.Sc\Paper\Benchmark Metabolitics\2_Features"
JSON_DB_PATH  = os.path.join(BASE_DATA_DIR, "MARKERDB_GLOBAL_DATABASE.json")
MODEL_PATH    = os.path.join(BASE_DATA_DIR, "Recon3D.json")
MAPPING_PATH  = os.path.join(BASE_DATA_DIR, "new-synonym-mapping.json")
FEAT_TOP100   = os.path.join(BASE_DATA_DIR, "MASTER_FEATURES_TOP100.csv")

OUTPUT_REPORT = os.path.join(BASE_DATA_DIR, "UNIFIED_DISCOVERY_AUDIT_REPORT.txt")

DISEASE_MAP = {
    "BC": "Breast Cancer", "BRCA": "Breast Cancer",
    "Alzheimer": "Alzheimer", "Diabetes": "Diabetes",
    "PDAC": "Pancreatic", "PRAD": "Prostate"
}

def run_unified_discovery_audit():
    print("🚀 Unified Discovery Audit Engine Started (Reaction + Pathway)...")

    # 1. BIOLOGICAL MAPS (RECON3D)
    # -------------------------------------------------------------------------
    with open(MODEL_PATH, 'r') as f:
        model = json.load(f)
    
    met_to_reactions = {}
    rxn_to_pathway = {}
    
    for rxn in model['reactions']:
        rxn_id = rxn['id']
        pathway = rxn.get('subsystem', 'Unknown')
        rxn_to_pathway[rxn_id] = pathway
        for met_id in rxn['metabolites'].keys():
            clean_met = re.sub(r'_[a-z]$', '', met_id) # Kompartman temizliği
            if clean_met not in met_to_reactions: met_to_reactions[clean_met] = set()
            met_to_reactions[clean_met].add(rxn_id)

    # 2. MARKERDB & MAPPING
    # -------------------------------------------------------------------------
    with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    norm_map = {str(k).lower().strip(): v for k, v in mapping.items()}

    with open(JSON_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    # 3. CLINICAL UNIVERSES (REACTION & PATHWAY)
    # -------------------------------------------------------------------------
    clinical_reac_universe = []
    clinical_path_universe = []
    
    for entry in db:
        m_name = str(entry['marker_name']).lower().strip()
        m_hmdb = str(entry['hmdb_id']).lower().strip() if entry.get('hmdb_id') else None
        rid = norm_map.get(m_hmdb) or norm_map.get(m_name)
        if not rid: continue
        
        rid_clean = rid.split('_')[0]
        assoc_rxns = met_to_reactions.get(rid_clean, set())
        assoc_paths = set([rxn_to_pathway.get(r) for r in assoc_rxns])

        for cond in entry.get('associated_conditions', []):
            c_name = cond['condition_name']
            for ds_key, ds_pattern in DISEASE_MAP.items():
                if ds_pattern.lower() in c_name.lower():
                    for rxn in assoc_rxns:
                        clinical_reac_universe.append({"Dataset": ds_key, "Feat": rxn})
                    for path in assoc_paths:
                        clinical_path_universe.append({"Dataset": ds_key, "Feat": path})
    
    df_clinical_reac = pd.DataFrame(clinical_reac_universe).drop_duplicates()
    df_clinical_path = pd.DataFrame(clinical_path_universe).drop_duplicates()

    # 4. TOP-100 DATA LOAD
    # -------------------------------------------------------------------------
    print("📂 Loading Top-100 features...")
    df_top100_all = pd.read_csv(FEAT_TOP100, low_memory=False)
    res_col = 'Res' if 'Res' in df_top100_all.columns else 'Resolution'
    
    # 5. UNIFIED AUDIT LOOP
    # -------------------------------------------------------------------------
    report = ["================================================================================",
              "      UNIFIED CLINICAL DISCOVERY AUDIT: REACTION vs. PATHWAY",
              "      (Top-100 Performance vs. Theoretical Full-Set Recall)",
              "================================================================================\n"]

    for ds_key in DISEASE_MAP.keys():
        print(f"🔎 Processing: {ds_key}...")
        
        # A) Targets
        targets_reac = set(df_clinical_reac[df_clinical_reac['Dataset'] == ds_key]['Feat'].unique())
        targets_path = set(df_clinical_path[df_clinical_path['Dataset'] == ds_key]['Feat'].unique())
        
        if not targets_reac and not targets_path: continue

        # B) Top-100 Analysis
        t100_ds = df_top100_all[df_top100_all['Dataset'] == ds_key]
        t100_hits_reac = targets_reac.intersection(set(t100_ds[t100_ds[res_col] == 'Reaction']['Feat'].unique()))
        t100_hits_path = targets_path.intersection(set(t100_ds[t100_ds[res_col].str.contains('Pathway', na=False)]['Feat'].unique()))

        # C) Full-Set Analysis (Streaming)
        full_hits_reac = set()
        full_hits_path = set()
        full_feat_file = glob.glob(os.path.join(FEAT_DIR, f"FEATURES_{ds_key}.csv"))
        
        if full_feat_file:
            print(f"   📂 Streaming {ds_key} Full Features...")
            chunks = pd.read_csv(full_feat_file[0], usecols=['Feat', res_col], chunksize=250000, low_memory=False)
            for chunk in chunks:
                # Reaction Full Hits
                reac_only = chunk[chunk[res_col] == 'Reaction']
                full_hits_reac.update(set(reac_only['Feat'].unique()).intersection(targets_reac))
                
                # Pathway Full Hits (Across any pathway strategy)
                path_only = chunk[chunk[res_col].str.contains('Pathway', na=False)]
                full_hits_path.update(set(path_only['Feat'].unique()).intersection(targets_path))

        # D) REPORTING
        report.append(f"--- DATASET: {ds_key} ---")
        
        # Reaction Section
        report.append(f" [REACTION LEVEL (10.6k features)]")
        report.append(f"   * Clinical Universe Hits: {len(targets_reac)}")
        report.append(f"   * Top-100 Discovery     : {len(t100_hits_reac)} ({len(t100_hits_reac)/len(targets_reac)*100:.1f}%)")
        report.append(f"   * Full-Set Recall       : {len(full_hits_reac)} ({len(full_hits_reac)/len(targets_reac)*100:.1f}%)")
        report.append(f"   * Hidden Signal (R>100) : {len(full_hits_reac) - len(t100_hits_reac)}")
        
        # Pathway Section
        report.append(f"\n [PATHWAY LEVEL (106 features)]")
        report.append(f"   * Clinical Universe Hits: {len(targets_path)}")
        report.append(f"   * Top-100 Discovery     : {len(t100_hits_path)} ({len(t100_hits_path)/len(targets_path)*100:.1f}%)")
        report.append(f"   * Full-Set Recall       : {len(full_hits_path)} ({len(full_hits_path)/len(targets_path)*100:.1f}%)")
        report.append(f"   * Hidden Signal (R>100) : {len(full_hits_path) - len(t100_hits_path)}")
        report.append("-" * 70 + "\n")

    # Final Save
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print("\n".join(report))
    print(f"\n✅ UNIFIED AUDIT FINISHED. Report: {OUTPUT_REPORT}")

if __name__ == "__main__":
    run_unified_discovery_audit()