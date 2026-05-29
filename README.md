# Proteome-Wide Off-Target Receptor Screening Pipeline

## Overview
This repository contains the computational pipeline and data analysis workflow used to study the off-target polypharmacology of common drugs, utilizing Diphenhydramine (DPH) as a model compound. 

The project evaluates binding affinities across 25,820 unique human protein structures by integrating high-resolution experimental Protein Data Bank (PDB) data with AlphaFold2 predicted models. The pipeline features automated structural cleaning, tissue-specific filtering, high-throughput virtual screening (HTVS) using Vina-GPU, and thermodynamic refinement via SeeSAR's HYDE scoring function.

## Repository Structure

* `data/`: Contains lightweight structural reference files, target sequences (`master_sequences.fasta`), ligand structures (`.sdf`, `.pdbqt`), and dataset inventory logs (`ALL_UNIQUE_PDB_IDS.txt`). *(Note: Raw 7.5GB proteome databases and heavy archives like `cns.zip` are excluded via `.gitignore` due to size constraints).*
* `docs/`: Visual documentation of the pipeline parameters, deduplication processes (`deduplicate.png`), and quality control (QC) thresholds.
* `results/`: Contains the summarized HTVS scores (`docking_scores.csv`, `final_hyde_scores.csv`), functional enrichment pathways (`Top_10_Novel_Pathways.csv`), Protein-Protein Interaction networks (`string.png`), and ESPript alignment visualizations.
* `scripts/`: The core automation and analysis scripts used to execute the pipeline.

## Script Documentation & Workflow

### 1. Dataset Curation, Retrieval & Preprocessing
These scripts automate the retrieval, deduplication, and quality control of the structural dataset.
* `fetch_structures.py`: Retrieves targeted experimental and Al-generated structural models.
* `unique_pdbs_all.py` & `matchBtwFoldersPDBids_uniqueness.py`: Ensures strict deduplication at the UniProt ID level across overlapping tissue datasets.
* `protein_structures_cleaning.py` & `clean_for_docking.py`: Standardizes files for docking by removing heteroatoms, alternate conformers, adding polar hydrogens.
* `assess_experimental_quality.py`: Enforces quality control thresholds (e.g., restricting to structures with better than 3 Å resolution).

**Cloud-Based AlphaFold Retrieval (Google Colab):**
Due to local bandwidth/storage constraints, the following cloud notebooks were utilized to query the EBI API and batch-download predicted models:
* 🔗 **[Colab Notebook 1: Tissue-Specific AlphaFold Rescue](https://colab.research.google.com/drive/1izMs-S-qyHY6eG9yBkLDbUYOVGspOFU5)** - Maps missing PDB IDs (e.g., vascular tissue) to UniProt accessions, deduplicates, and downloads the corresponding AlphaFold `.pdb` files.
* 🔗 **[Colab Notebook 2: Failed ID Recovery](https://colab.research.google.com/drive/1pNrDKwkf_0-CzpOTui0H74202myKtLOD)** - Scans `failed_ids.txt` to retry API retrieval for missing structural predictions and generates success/failure logs.
* 🔗 **[Colab Notebook 3: Batch AlphaFold Downloader](https://colab.research.google.com/drive/1QydupiQdahYomH9Yb7Hpr3Ybjb_8VkDl)** - Executes bulk downloads from a curated list of required `alphafold_uniprot_ids.txt`.

### 2. Binding Site Prediction
* `extract_pockets.py` & `rank_proteins_binding_sites.py`: Implements template-free machine learning algorithms (P2Rank/DoGSiteScorer) to identify and extract the most accessible ligand-binding sites across the proteome.

### 3. High-Throughput Molecular Docking (HTVS)
Scripts configuring and executing the parallelized docking and thermodynamic refinement. *(Note: Production docking was executed on a dedicated external GPU server, not locally or via Colab).*
* `prep_configs.sh` & `get_box.py`: Automates the generation of docking grid boxes centered on the predicted primary binding pockets with 1.0 Å grid spacing.
* `2_run_gpu.sh`: Execution script for deploying the OpenCL-optimized Vina-GPU engine for rapid proteome-wide screening.
* `run_vina_hyde.sh` & `RUN_FLEXX_FINAL.sh`: Executes the secondary thermodynamic refinement phase, reassessing the top 2,000 hits based on atomic dehydration penalties to minimize false positives.

### 4. Biological & Structural Analysis
Scripts translating raw docking scores into systems-biology insights.
* `top_pathways.py` & `string_prep.py`: Processes the top off-target hits (e.g., GABRG2, DHFR, FASN, ACE2) for KEGG pathway enrichment and STRING Protein-Protein Interaction analysis.
* `run_tmalign.py` & `get_rmsd.py`: Calculates Template Modeling scores (TM-score) to evaluate structural homology independent of sequence alignment.
* `run_msa.py` & `run_espript_msa.py`: Performs Multiple Sequence Alignments mapped against top target structures to identify conserved pharmacological binding motifs.

## Key Findings
This pipeline successfully validated established CNS off-targets (NMDA, Muscarinic Receptors, GABRG2) and uncovered highly enriched novel metabolic vulnerabilities, notably in Fatty Acid Biosynthesis (FASN) and Folate Biosynthesis (DHFR). Full data summaries and atomic-level binding refinements can be found in the `results/` directory.
