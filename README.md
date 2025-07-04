1. ```
   KnowledgeBase Markdown Merger & Kindle Converter
   This repository provides a complete pipeline to:
   
   Recursively scan your knowledgebase directory for PDFs, Markdown, DOCX, TXT, and MDX files.
   
   Convert all supported files into clean Markdown format.
   
   Split large Markdown files into manageable chunks.
   
   Shuffle the chunked files to randomize reading order.
   
   Convert the shuffled Markdown chunks into Kindle-compatible EPUB or MOBI files.
   
   Track which files have already been processed to avoid duplication.
   
   Run the entire pipeline via a single master script.
   
   📁 Repository Structure
   graphql
   Copy
   .
   ├── Ingest/                # Converted Markdown files from source documents
   ├── Split/                 # Split Markdown chunks (~5,000 chars each)
   ├── Kindle/                # Final EPUB or MOBI files for Kindle
   ├── Logs/                  # Logs tracking processed source files
   ├── ingest_and_convert.py  # Python script for scanning, converting, and tracking
   ├── ingest_and_convert.sh  # Master bash script orchestrating the pipeline
   ├── split_markdown.sh      # Bash script to split Markdown files into chunks
   ├── shuffle_split_files.sh # Bash script to shuffle chunked Markdown files
   ├── convert_to_kindle.sh   # Bash script to convert Markdown chunks to Kindle format
   ├── README.md              # This documentation file
   🔧 Prerequisites
   Python 3.x
   
   Pandoc (https://pandoc.org/installing.html) — for file conversions
   
   Kindlegen (optional, recommended for MOBI output)
   Download from https://www.amazon.com/gp/feature.html?docId=1000765211
   Or use EPUB output if kindlegen is unavailable
   
   Unix-like shell environment (Linux, macOS, WSL)
   
   ⚙️ Setup Instructions
   Clone this repository and navigate into it.
   
   Install dependencies:
   
   Ensure python3 and pip are installed
   
   Install any Python dependencies (currently none external needed)
   
   Install pandoc and verify by running:
   
   bash
   Copy
   pandoc --version
   Optionally install kindlegen and ensure it is in your PATH.
   
   Set the ``KB_DIR`` environment variable or edit ``ingest_and_convert.py`` if your knowledge base lives elsewhere.
   
   🚀 Usage
   Run the full pipeline with:
   
   bash
   Copy
   chmod +x ingest_and_convert.sh split_markdown.sh shuffle_split_files.sh convert_to_kindle.sh
   ./ingest_and_convert.sh
   What happens?
   Scan & Convert
   The Python script scans your knowledgebase directory (defaults to ``~/Documents/KnowledgeBase`` or the value of ``KB_DIR``), converts PDFs, DOCX, TXT, MDX, and Markdown to Markdown files in Ingest/.
   It skips files already processed by referencing Logs/processed_files.log.
   
   Split Markdown
   Large markdown files are split into ~5,000 character chunks saved into Split/.
   
   Shuffle Chunks
   The chunk files are shuffled randomly to vary reading order.
   
   Convert to Kindle Format
   Markdown chunks in Split/ are converted to .mobi (if kindlegen is present) or .epub in Kindle/.
   
   🗂️ Tracking Processed Files
   The system keeps a log of all processed source files in Logs/processed_files.log.
   
   This prevents re-processing unchanged files on subsequent runs.
   
   To reset processing, clear or remove the log file.
   
   ⚠️ Notes
   Large PDFs or complex documents may have imperfect markdown conversion; manual cleanup may be needed.
   
   .mdx files will be treated as markdown but JSX components are not specially handled.
   
   Ensure pandoc and kindlegen are executable from your shell.
   
   🧩 Extending & Customization
   Add support for other file types by extending SUPPORTED_EXTS in ingest_and_convert.py.
   
   Modify chunk size by editing split_markdown.sh.
   
   Add error handling and detailed logging as needed.
   
   🆘 Troubleshooting
   If conversions fail, try running pandoc commands manually on problem files to debug.
   
   Verify PATH settings if pandoc or kindlegen commands are not found.
   
   Check file permissions on source and output directories.xxxxxxxxxx bashCopyEditMerged/merged_output.md
   ```