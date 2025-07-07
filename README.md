# KnowledgeBase Merger & PDF Chunker

This repository provides a modular pipeline for consolidating a knowledge base into easy-to-read PDFs. It recursively converts supported files to PDF, merges them per subfolder and splits the results into ~20k word chunks. Each run records file hashes so unchanged files are skipped.

## Features

- Recursively scan subfolders under the knowledge base directory.
- Convert Markdown (`.md`/`.mdx`), text (`.txt`), DOCX and PDF files to PDF via `pandoc`.
- Merge all PDFs in a subfolder into a single file in `Merged/`.
- Split merged PDFs into ~20,000 word chunks saved in `Chunks/`.
- Track processed files in `ledger.json` to avoid duplicate work.
- Log actions in `Logs/`.

## Repository Structure

```text
.
├── Converted/             # Temporary PDFs per source folder
├── Merged/                # Final merged PDFs per folder
├── Chunks/                # Chunked PDF outputs (~20k words)
├── Logs/                  # Log files
├── orchestrate_all.py     # End-to-end workflow script
├── ledger.json            # Processing ledger (auto-created)
└── README.md              # This documentation file
```

## Prerequisites

- Python 3
- [pandoc](https://pandoc.org/installing.html)
- `pip install -r requirements.txt` (installs `PyPDF2`, `fpdf` and `pytest`)

Ensure `pandoc` is accessible in your `PATH`. Optionally set the environment variable `KB_DIR` to point to your knowledge base. The default is `/home/cinder/Documents/K_Knowledge_Base`.

## Usage

Run the entire pipeline from the repository root:

```bash
python orchestrate_all.py
```

This will:
1. Scan each subfolder in `KB_DIR` for new or modified files.
2. Convert supported files to PDF (stored under `Converted/`).
3. Merge all PDFs in each subfolder into `Merged/<folder>.pdf`.
4. Split the merged PDF into 20k-word chunks placed in `Chunks/`.
5. Update `ledger.json` and write logs to `Logs/workflow.log`.

You can delete `ledger.json` to force a full reprocess.

## Running Tests

```bash
pytest
```

The tests validate that workflow scripts are executable.
