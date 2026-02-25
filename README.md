# A High-Dimensional Benchmark of Objective Functions and Biological Resolutions for Personalized Metabolic Phenotyping

This repository contains the computational pipeline, statistical analysis scripts, and visualization framework for the benchmarking study of 57,600 unique experimental configurations in personalized metabolic modeling.

## 📂 Data Access & Setup

To ensure reproducibility while maintaining a lightweight repository, all processed datasets and high-dimensional feature matrices are hosted on **Zenodo**.

1. **Download Data:** Access the datasets via Zenodo: **[D10.5281/zenodo.18770830I]**
2. **Extraction:** Extract the contents of the archive directly into the **root directory** of this repository.
3. **Structure Check:** For the scripts to resolve file paths correctly, the following directory structure must be maintained:

```
.
├── 0_Scripts/              # Core computational pipeline
│   ├── 00_Quality_Control/ # Data integrity checks
│   ├── 01_Data_Processing/ # Cleaning and consolidation
│   ├── 02_Statistical_Analysis/ # Core benchmarking logic
│   ├── 03_Visualization/   # Figure generation
│   └── makale/             # Manuscript-specific analysis scripts
├── 1_Results/              # Raw simulation outputs (Available on Zenodo)
├── 2_Features/             # Generated metabolic features
├── 3_Runstats/             # Execution and performance logs
├── 4_Parquets/             # Intermediate data in parquet format
├── 5_Figures/              # Final manuscript figures
├── 6_Processed_Data/       # Aggregated and mapped datasets
├── 7_Transcriptomic_Data/  # Clinical validation data (GSE datasets)
├── README.md
└── LICENSE
```

## 🛠 Usage & Pipeline Logic

The research workflow is divided into two primary phases:

### Phase 1: High-Throughput Simulations (HPC)
The initial generation of 57,600 metabolic flux profiles was performed on the **TRUBA High-Performance Computing (HPC)** cluster. Due to the massive computational requirements, these simulations are not intended to be run on standard local machines. The pre-calculated results of these simulations are provided in the Zenodo archive.

### Phase 2: Post-Processing and Statistical Analysis
The scripts in this repository focus on this phase. To generate the primary analysis tables, statistical summaries, and performance metrics reported in the paper, run:

```bash
python 0_Scripts/master.py
```

*Note: `master.py` serves as the orchestrator for data aggregation and statistical reporting from the pre-processed simulation outputs.*

## 📋 Script Nomenclature
Within the `0_Scripts/` and `0_Scripts/makale/` directories, you may encounter scripts with unconventional prefixes (e.g., `aht_`, `ali_hoca_talep_`, `biomarker_poc_`). 

These files represent **targeted analysis modules and ad-hoc sensitivity tests** developed during specific phases of the research and internal verification. While following an iterative naming convention, they contain the underlying logic for specific data audits and ground-truth comparisons reported in the study.

## 🎓 Citation
If you use this code or the associated datasets in your research, please cite:
> *Erdogan, M. A., & Cakmak, A. (2026). A High-Dimensional Benchmark of Objective Functions and Biological Resolutions for Personalized Metabolic Phenotyping.*

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.