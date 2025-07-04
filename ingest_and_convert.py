import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configuration
# The knowledge base directory can be overridden with the ``KB_DIR``
# environment variable. It defaults to ``~/Documents/KnowledgeBase``.
KB_DIR = Path(os.environ.get("KB_DIR", Path.home() / "Documents/KnowledgeBase"))
INGEST_DIR = Path("./Ingest")
LOG_DIR = Path("./Logs")
PROCESSED_LOG = LOG_DIR / "processed_files.log"

# Supported file extensions and their pandoc target
SUPPORTED_EXTS = {
    ".pdf": "markdown",
    ".md": None,       # just copy
    ".mdx": None,      # copy but can be stripped later
    ".docx": "markdown",
    ".txt": "markdown",
}

def load_processed():
    if not PROCESSED_LOG.exists():
        return set()
    with PROCESSED_LOG.open("r") as f:
        return set(line.strip() for line in f.readlines())

def log_processed(file_path, error=False):
    with PROCESSED_LOG.open("a") as f:
        timestamp = datetime.utcnow().isoformat()
        if error:
            f.write(f"{file_path}\t{timestamp}\tERROR\n")
        else:
            f.write(f"{file_path}\t{timestamp}\n")

def convert_to_markdown(src_path: Path, dest_path: Path):
    # For md/mdx/txt just copy
    if src_path.suffix in [".md", ".mdx", ".txt"]:
        dest_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
        return True
    # For pdf/docx use pandoc with retry logic
    attempts = 0
    while attempts < 3:
        try:
            subprocess.run(
                ["pandoc", str(src_path), "-o", str(dest_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except subprocess.CalledProcessError as e:
            attempts += 1
            print(
                f"Error converting {src_path} (attempt {attempts}): {e.stderr.decode()}",
                file=sys.stderr,
            )
            if attempts >= 3:
                log_processed(str(src_path), error=True)
                return False

def main():
    INGEST_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    processed_files = load_processed()
    new_processed = 0

    for root, _, files in os.walk(KB_DIR):
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix.lower() not in SUPPORTED_EXTS:
                continue
            if str(filepath) in processed_files:
                print(f"Skipping already processed: {filepath}")
                continue

            # Destination file in Ingest, convert extension to .md
            dest_filename = filepath.stem + ".md"
            dest_path = INGEST_DIR / dest_filename

            print(f"Processing: {filepath}")
            success = convert_to_markdown(filepath, dest_path)
            if success:
                log_processed(str(filepath))
                new_processed += 1

    print(f"Conversion complete. {new_processed} new files processed.")

if __name__ == "__main__":
    main()
