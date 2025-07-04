# KnowledgeBase Markdown Merger & Kindle Converter

This repository provides a simple pipeline to convert a folder of documents into a Kindle-ready eBook.

## Features

- Recursively scan your knowledgebase for PDF, Markdown, DOCX, TXT and MDX files.
- Convert the supported files into clean Markdown using `pandoc`.
- Split large Markdown files into chunks of about 20,000 characters.
- Shuffle the chunks to randomize reading order.
- Convert the shuffled files to EPUB or MOBI format.
- Track processed files to avoid duplication.
- Run the entire workflow with a single script.

## Repository Structure

```text
.
├── Ingest/                # Converted Markdown files
├── Split/                 # Split Markdown chunks (~20k characters)
├── Kindle/                # Final EPUB or MOBI files
├── Logs/                  # Logs tracking processed source files
├── ingest_and_convert.py  # Python script for scanning and conversion
├── ingest_and_convert.sh  # Master bash script orchestrating the pipeline
├── split_markdown.sh    # Bash script to split Markdown files into chunks
├── shuffle_split_files.sh # Bash script to shuffle chunked Markdown files
├── convert_to_kindle.sh   # Bash script to convert Markdown chunks to Kindle format
└── README.md              # This documentation file
```

## Prerequisites

- Python 3
- [Pandoc](https://pandoc.org/installing.html) for file conversions
- `kindlegen` (optional, recommended for MOBI output)
- Unix-like shell environment (Linux, macOS, WSL)

## Setup

1. Clone this repository and navigate into it.
2. Install dependencies and verify `pandoc`:

   ```bash
   pandoc --version
   ```

   Optionally install kindlegen and ensure it is in your PATH. Set the `KB_DIR` environment variable or edit `ingest_and_convert.py` if your knowledge base lives elsewhere.

3. Make the scripts executable:

   ```bash
   chmod +x ingest_and_convert.sh split_markdown.sh shuffle_split_files.sh convert_to_kindle.sh
   ```

## Usage

Run the full pipeline with:
```bash
./ingest_and_convert.sh
```

### What Happens?

1. **Scan & Convert** – `ingest_and_convert.py` scans your knowledgebase (default `/home/$USER/Documents/K_Knowledge_Base`) and converts supported files to Markdown in `Ingest/`.
2. **Split Markdown** – Large Markdown files are split into ~20,000-character chunks saved in `Split/` using `split_markdown.sh`.
3. **Shuffle Chunks** – The chunk files are shuffled randomly by `shuffle_split_files.sh`.
4. **Convert to Kindle Format** – Markdown chunks are converted to `.mobi` (if `kindlegen` is present) or `.epub` in `Kindle/` via `convert_to_kindle.sh`.

## Tracking Processed Files

The system keeps a log of all processed source files in `Logs/processed_files.log`. This prevents re-processing unchanged files on subsequent runs. To reset processing, clear or remove the log file.

## Troubleshooting

- If conversions fail, try running `pandoc` commands manually on problem files to debug.
- Verify `PATH` settings if `pandoc` or `kindlegen` commands are not found.
- Check file permissions on source and output directories.

