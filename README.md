# Proteome-Wide Off-Target Receptor Screening Pipeline

## Overview
This repository has all the steps and work we did to study how common drugs affect things they are not supposed to using Diphenhydramine as an example.

We looked at how these drugs stick to lots of different human proteins. 25,820 Of them. By combining real data from the Protein Data Bank with predictions, from AlphaFold2. Our process includes cleaning up the protein structures filtering them by the type of tissue they come from testing lots of drugs against these proteins using Vina-GPU and then checking how well they really fit using SeeSARs HYDE scoring function. We used Diphenhydramine as a model to see how this works.

## Repository Structure

* The `data/` folder contains files which has the structure for our project, the target sequences in a file called `master_sequences.fasta` and the shapes of the molecules we are looking at in `.sdf` and `.pdbqt` files. It also has a list of all the things we have in the dataset in a file called `ALL_UNIQUE_PDB_IDS.txt`. We did not include the big files like `cns.zip` because they take up too much space.

* The `docs/` folder has pictures that help us understand how the pipeline works. It has a picture called `deduplicate.png` that shows how we get rid of things and it also has information about the quality control checks we do.

* The `results/` folder has all the summarized information from our analysis. It has files like `docking_scores.csv` and `final_hyde_scores.csv` that show us how well things worked together. It also has information about the pathways we found in a file called `Top_10_Novel_Pathways.csv` and pictures of how proteins interact with each other in a file called `string.png`. We also have pictures that show how the sequences of the proteins line up, in the `results/` folder, made with a tool called ESPript.

* The `scripts/` folder has all the code we use to make the pipeline run automatically and to analyze the data. It is really important because it has all the codes we need to do our analysis. We use the automated scripts in the folder to make sure everything runs smoothly.

## Script Documentation & Workflow

### 1. Dataset Curation, Retrieval & Preprocessing

The Dataset Curation, Retrieval & Preprocessing scripts do a lot of work for us. They help get the dataset and make sure they good to use for further steps. 
* `Fetch_structures.py` is a script that gets the models we need from experiments and the ones made by computers.
* We use `unique_pdbs_all.py` and `matchBtwFoldersPDBids_uniqueness.py` to make sure we do not have any duplicates in our dataset. We want to be really careful about this so we check for duplicates at the UniProt ID level even when we have datasets that overlap.
* Then we have `protein_structures_cleaning.py` and `clean_for_docking.py` which help get our files ready for docking. They do things like remove heteroatoms and alternate conformers and add polar hydrogens.
* Finally `assess_experimental_quality.py` checks the quality of the structures. It makes sure that the Dataset are good enough and have structures that have a resolution of better than 3 Å.

**Cloud-Based AlphaFold Retrieval (Google Colab):**
Due to local bandwidth/storage constraints, the following cloud notebooks were utilized to query the EBI API and batch-download predicted models:
* 🔗 **[Colab Notebook 1: Tissue-Specific AlphaFold Rescue](https://colab.research.google.com/drive/1izMs-S-qyHY6eG9yBkLDbUYOVGspOFU5)** - Maps missing PDB IDs (e.g., vascular tissue) to UniProt accessions, deduplicates, and downloads the corresponding AlphaFold `.pdb` files.
* 🔗 **[Colab Notebook 2: Failed ID Recovery](https://colab.research.google.com/drive/1pNrDKwkf_0-CzpOTui0H74202myKtLOD)** - Scans `failed_ids.txt` to retry API retrieval for missing structural predictions and generates success/failure logs.
* 🔗 **[Colab Notebook 3: Batch AlphaFold Downloader](https://colab.research.google.com/drive/1QydupiQdahYomH9Yb7Hpr3Ybjb_8VkDl)** - Executes bulk downloads from a curated list of required `alphafold_uniprot_ids.txt`.

### 2. Binding Site Prediction
* `extract_pockets.py` & `rank_proteins_binding_sites.py`:This system uses computer programs called P2Rank and DoGSiteScorer. It looks at all the proteins in the body to find the best places where molecules can attach to proteins. The computer programs are very good, at identifying where molecules can bind to proteins without needing a template to follow.

### 3. High-Throughput Molecular Docking (HTVS)
I am working with scripts that help me set up and run the parallelized docking and thermodynamic refinement.
*(Note: I did the production docking on an external GPU server)
* I use `prep_configs.sh` and `get_box.py` to make docking grid boxes. These boxes are centered on the binding pockets that I found and they have a grid spacing of 1.0 Å.
* The `2_run_gpu.sh` script is what I use to run the OpenCL-optimized Vina-GPU engine. This engine is really fast. Helps me screen a lot of proteins at the same time.
* I also use `run_vina_hyde.sh`. RUN_FLEXX_FINAL.sh` to do the secondary thermodynamic refinement phase. In this phase I look again at the 2,000 hits and use atomic dehydration penalties to try to minimize false positives. I do this to make sure the docking and thermodynamic refinement are accurate.

### 4. Biological & Structural Analysis
* `top_pathways.py`. `string_prep.py`: These process the top off-target hits like GABRG2, DHFR, FASN and ACE2 for KEGG pathway enrichment and STRING Protein-Protein Interaction analysis.
* `run_tmalign.py`. `get_rmsd.py`: These calculate Template Modeling scores to evaluate how similar protein structures are, without relying on sequence alignment.
* `run_msa.py` and `run_espript_msa.py`: These do Multiple Sequence Alignments against target structures to find conserved binding areas, for pharmacology.

## Key Findings
This pipeline successfully validated established CNS off-targets (NMDA, Muscarinic Receptors, GABRG2) and uncovered highly enriched novel metabolic vulnerabilities, notably in Fatty Acid Biosynthesis (FASN) and Folate Biosynthesis (DHFR). Full data summaries and atomic-level binding refinements can be found in the `results/` directory.
