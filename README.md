# A High-Dimensional Benchmark of Objective Functions and Biological Resolutions for Personalized Metabolic Phenotyping

This repository contains the official computational pipeline, scripts, and analysis framework for the benchmarking study of 57,600 unique experimental configurations in personalized metabolic modeling.

## 📂 Data Access & Setup

To ensure reproducibility while maintaining a lightweight repository, all processed datasets and high-dimensional feature matrices are hosted on **Zenodo**.

1. **Download Data:** Access the datasets via Zenodo: **[INSERT YOUR DOI LINK HERE]**
2. **Extraction:** Extract the contents of the downloaded archive directly into the **root directory** of this repository.
3. **Structure Check:** After extraction, your local directory structure must follow the numbered organization for the scripts to resolve file paths correctly:

```
.
├── 0_Scripts/              # Core computational pipeline
│   ├── 00_Quality_Control/ # Data integrity checks
│   ├── 01_Data_Processing/ # Cleaning and consolidation
│   ├── 02_Statistical_Analysis/ # Core benchmarking logic
│   ├── 03_Visualization/   # Figure generation
│   └── makale/             # Manuscript-specific analysis scripts
├── 1_Results/              # Raw simulation outputs
├── 2_Features/             # Generated metabolic features
├── 3_Runstats/             # Execution and performance logs
├── 4_Parquets/             # Intermediate data in parquet format
├── 5_Figures/              # Final manuscript figures
├── 6_Processed_Data/       # Aggregated and mapped datasets
├── 7_Transcriptomic_Data/  # Clinical validation data (GSE datasets)
├── README.md
└── LICENSE
```

## 🛠 Script Nomenclature & Usage

The project follows a modular design. To execute the primary benchmarking workflow, run:
```bash
python 0_Scripts/master.py
```

### Note on Naming Conventions
Within the `0_Scripts/` and `0_Scripts/makale/` directories, you may encounter scripts with unconventional prefixes such as `aht_`, `ali_hoca_talep_`, or `biomarker_poc_`. 

These files represent **targeted analysis modules, intermediate validation steps, and ad-hoc sensitivity tests** developed during specific phases of the research and internal verification (e.g., custom requests from supervisors or targeted data audits). While they follow an iterative naming convention, they contain the underlying logic for specific ground-truth comparisons reported in the study.

## 🧬 Scientific Context
This framework evaluates the following key aspects of metabolic phenotyping:
* **Objective Functions:** Benchmarking across various mathematical formulations (ATP, Robust, etc.).
* **Biological Resolutions:** Comparative analysis of Pathway_min, Pathway_max, and Pathway_mean.
* **Sparsity Paradox:** Evaluating model performance across different feature density thresholds (Top 10% vs. Full Network).
* **Transcriptomic Integration:** Implementation and validation of patient-specific constraints (Cr).

## 🎓 Citation
If you use this code or the associated datasets in your research, please cite:
> *Erdogan, M. A., & Cakmak, A. (2026). A High-Dimensional Benchmark of Objective Functions and Biological Resolutions for Personalized Metabolic Phenotyping.*

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.