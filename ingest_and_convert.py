import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
import hashlib

# Configuration
# The knowledge base directory can be overridden with the ``KB_DIR``
# environment variable. It defaults to ``~/Documents/KnowledgeBase``.
KB_DIR = Path(os.environ.get("KB_DIR", Path.home() / "Documents/KnowledgeBase"))
INGEST_DIR = Path("./Ingest")
LOG_DIR = Path("./Logs")
LOG_FILE = LOG_DIR / "workflow.log"


def log(message: str) -> None:
    """Append a timestamped message to the log file under ``LOG_DIR``."""
    LOG_DIR.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        timestamp = datetime.utcnow().isoformat()
        line = f"{timestamp} - {message}"
        print(line)
        f.write(line + "\n")
LEDGER_PATH = Path("ledger.json")

# Supported file extensions.
# Markdown/MDX files are copied directly; everything else uses pandoc.
SUPPORTED_EXTS = {
    ".pdf": "markdown",
    ".md": None,
    ".mdx": None,
    ".docx": "markdown",
    ".txt": "markdown",
    ".html": "markdown",
    ".htm": "markdown",
    ".toml": "markdown",
    ".json": "markdown",
    ".xml": "markdown",
    ".tex": "markdown",
    ".rst": "markdown",
    ".epub": "markdown",
    ".adoc": "markdown",
    ".rtf": "markdown",
    ".yaml": "markdown",
    ".yml": "markdown",
}

# Extensions that can be copied without pandoc
COPY_EXTS = {".md", ".mdx", ".txt"}

def load_ledger():
    if LEDGER_PATH.exists():
        try:
            with LEDGER_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    data.setdefault("file_hashes", {})
    data.setdefault("last_run", None)
    data.setdefault("epub_count", 0)
    return data

def save_ledger(data):
    data["last_run"] = datetime.utcnow().isoformat()
    with LEDGER_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def compute_hash(path: Path) -> str:
    hash_obj = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def convert_to_markdown(src_path: Path, dest_path: Path) -> bool:
    """Convert a supported file to Markdown.

    Files with extensions in ``COPY_EXTS`` are copied directly. Everything else
    is passed through pandoc with a small retry loop.
    """

    if src_path.suffix in COPY_EXTS:
        dest_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
        log(f"Copied {src_path} to {dest_path}")
        return True

    # For other formats use pandoc with retry logic
    attempts = 0
    while attempts < 3:
        try:
            subprocess.run(
                ["pandoc", str(src_path), "-o", str(dest_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            log(f"Converted {src_path} to {dest_path}")
            return True
        except subprocess.CalledProcessError as e:
            attempts += 1
            error_msg = f"Error converting {src_path} (attempt {attempts}): {e.stderr.decode()}"
            print(error_msg, file=sys.stderr)
            log(error_msg)
            if attempts >= 3:
                return False

def main():
    INGEST_DIR.mkdir(exist_ok=True)
    log("Starting ingestion")

    ledger = load_ledger()
    file_hashes = ledger["file_hashes"]
    new_processed = 0

    for root, _, files in os.walk(KB_DIR):
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix.lower() not in SUPPORTED_EXTS:
                continue

            file_hash = compute_hash(filepath)
            if file_hashes.get(str(filepath)) == file_hash:
                log(f"Skipping already processed: {filepath}")
                continue

            # Destination file in Ingest, convert extension to .md
            dest_filename = filepath.stem + ".md"
            dest_path = INGEST_DIR / dest_filename

            log(f"Processing {filepath}")
            success = convert_to_markdown(filepath, dest_path)
            if success:
                file_hashes[str(filepath)] = file_hash
                new_processed += 1

    save_ledger(ledger)
    log(f"Conversion complete. {new_processed} new files processed.")

if __name__ == "__main__":
    main()
