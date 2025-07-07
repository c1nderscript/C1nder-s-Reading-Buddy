# KnowledgeBase Merger & PDF Chunker

This repository provides a modular pipeline for consolidating a knowledge base into easy-to-read PDFs. It recursively converts supported files to PDF, merges them per subfolder and splits the results into ~20k word chunks. Each run records file hashes so unchanged files are skipped.

## Features

- Recursively scan subfolders under the knowledge base directory.
- Convert Markdown (`.md`/`.mdx`) directly to PDF using FPDF with a Unicode font.
- Convert text (`.txt`), HTML, TOML, DOCX and other common e-book formats via `pandoc`.
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
- [pandoc](https://pandoc.org/installing.html) for non-Markdown formats

Run `./configure.sh` once to create a virtual environment and install the
packages from `requirements.txt`.

```
./configure.sh
source .venv/bin/activate
```

Ensure `pandoc` is accessible in your `PATH` for converting DOCX and text files. Markdown files are handled directly via FPDF, which embeds the DejaVuSans TrueType font so that Unicode characters render correctly (no LaTeX engine required). The chunking step uses the same font to avoid encoding errors. Optionally set the environment variable `KB_DIR` to point to your knowledge base. The default is `/home/cinder/Documents/K_Knowledge_Base`.

## Usage

Run the entire pipeline from the repository root:

```bash
python orchestrate_all.py
```

When run for the first time the script asks for the directory where chunked
files should be written and stores that choice in `ledger.json`. On subsequent
runs you can simply confirm the saved location or enter a new one.

You will be prompted for:
1. The full path to the folder of documents to convert.
2. A base name for the merged PDF and its chunks.

It will then:
1. Convert supported files in the chosen folder to PDF (stored under `Converted/`).
2. Merge them into `Merged/<base_name>.pdf`.
3. Split the merged PDF into 20k‑word chunks placed in the configured output directory.
4. Update `ledger.json` and write logs to `Logs/workflow.log`.

You can delete `ledger.json` to force a full reprocess.

## Running Tests

```bash
pytest
```

The tests validate that workflow scripts are executable.
