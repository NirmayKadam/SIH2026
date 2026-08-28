# Data Provenance

This document serves as the ground truth for dataset origins, ensuring the "No Synthetic Data" architecture rule is respected and verifiable.

## ICIJ Offshore Leaks
- **Leak used:** Panama Papers (2016)
- **Jurisdiction/firm filter applied:** Entities and officers matching `country_codes` == `"IND"` (India).
- **Node/edge count after filtering:** ~400 nodes, ~600 edges (demo subset).
- **License:** Open Database License (ODbL) — must cite ICIJ when displayed/published.
- **Source:** https://offshoreleaks.icij.org/pages/database
- **Acquisition:** Download `panama_papers.csv.zip`. Extract `nodes-entities.csv`, `nodes-officers.csv`, and `relationships.csv`. Filter them externally (e.g. via pandas script) to subset for India, and place the filtered CSVs into `data/raw/icij_offshore_leaks/`.

## Enron Email Corpus
- **Custodians included:** Kenneth Lay (`lay-k`)
- **Date range:** 2000 - 2001
- **Email count after filtering:** ~20 highly connected emails focusing on financial subjects.
- **Source:** https://www.cs.cmu.edu/~enron/
- **Acquisition:** Download the latest tarball. Extract `lay-k/all_documents/`. Select 20 emails with significant overlap in recipients/subjects. Place `.txt` copies in `data/raw/enron_emails/`.

## Court Judgments
- **Judgments used:** 
  1. *Vijay Madanlal Choudhary vs Union Of India* (PMLA constitutional validity) - 2022
  2. *Chidambaram vs Directorate of Enforcement* (INX Media case) - 2019
- **Selection rationale:** High-profile Indian money laundering cases demonstrating multi-layered corporate shell structures and hawala transactions.
- **Source:** [Indian Kanoon](https://indiankanoon.org/)
- **Acquisition:** Search for the case titles. Download or print-to-PDF the judgment text. Save the files as `vijay_madanlal.pdf` and `chidambaram.pdf` inside `data/raw/court_judgments/`.

## What's real vs. what's simulated
Be ready to say this exact sentence to judges: 
"All entities and relationships in this demo come from real, publicly available datasets — we do not use synthetic data anywhere in the running system. We subsampled for a demo-sized graph; the pipeline itself is what would scale to full FIR/CDR/financial data in a real deployment."
