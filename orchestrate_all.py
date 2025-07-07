import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict

try:
    from pypdf import PdfMerger, PdfReader
except ModuleNotFoundError:  # fall back for environments with PyPDF2 installed
    from PyPDF2 import PdfMerger, PdfReader
from fpdf import FPDF

FONT_PATH = Path(
    os.environ.get(
        "FONT_PATH",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
)


def markdown_to_pdf(src: Path, dest: Path) -> None:
    """Render a Markdown file to PDF using FPDF.

    This avoids pandoc's default pdflatex dependency.
    """
    text = src.read_text(encoding="utf-8")
    # FPDF 1.x does not support characters outside the Basic Multilingual Plane
    # (U+0000–U+FFFF). Filter them out to prevent index errors when writing
    # the PDF.
    sanitized = "".join(ch for ch in text if ord(ch) <= 0xFFFF)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_font(
        "DejaVu",
        "",
        str(FONT_PATH),
        uni=True,
    )
    pdf.set_font("DejaVu", size=12)
    for line in sanitized.splitlines():
        pdf.multi_cell(0, 10, line)
    pdf.output(str(dest))

KB_DIR = Path(os.environ.get("KB_DIR", "/home/cinder/Documents/K_Knowledge_Base"))
CONVERTED_DIR = Path("Converted")
MERGED_DIR = Path("Merged")
CHUNK_DIR = Path("Chunks")
LOG_DIR = Path("Logs")
LEDGER_PATH = Path("ledger.json")

# Additional formats like HTML, TOML and common ebook types are
# converted via pandoc. Markdown/MDX is rendered directly with FPDF.
SUPPORTED_EXTS = {
    ".pdf",
    ".md",
    ".mdx",
    ".txt",
    ".docx",
    ".html",
    ".htm",
    ".toml",
    ".json",
    ".xml",
    ".tex",
    ".rst",
    ".epub",
    ".adoc",
    ".rtf",
    ".yaml",
    ".yml",
}

LOG_FILE = LOG_DIR / "workflow.log"


def log(message: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        timestamp = datetime.utcnow().isoformat()
        line = f"{timestamp} - {message}"
        print(line)
        f.write(line + "\n")


def load_ledger() -> Dict:
    if LEDGER_PATH.exists():
        with LEDGER_PATH.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    data.setdefault("folders", {})
    return data


def save_ledger(data: Dict) -> None:
    with LEDGER_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# This helper mirrors the convert_file function in ingest_and_convert.py

def convert_file(src: Path, dest: Path) -> bool:
    """Convert a supported file to PDF.

    Markdown and MDX files are rendered via :func:`markdown_to_pdf` to avoid
    pandoc's requirement for a LaTeX engine. Other formats fall back to pandoc.
    """

    ext = src.suffix.lower()

    if ext == ".pdf":
        dest.write_bytes(src.read_bytes())
        if dest.stat().st_size == 0:
            dest.unlink(missing_ok=True)
            return False
        return True

    if ext in {".md", ".mdx"}:
        try:
            markdown_to_pdf(src, dest)
            return True
        except Exception as e:  # noqa: BLE001
            log(f"Conversion failed for {src}: {e}")
            dest.unlink(missing_ok=True)
            return False

    tmp_md = dest.with_suffix(".tmp.md")
    try:
        subprocess.run(
            ["pandoc", str(src), "-t", "markdown", "-o", str(tmp_md)],
            check=True,
        )
        markdown_to_pdf(tmp_md, dest)
        tmp_md.unlink(missing_ok=True)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Conversion failed for {src}: {e}")
        tmp_md.unlink(missing_ok=True)
        dest.unlink(missing_ok=True)
        return False


def scan_and_convert(folder: Path, ledger: Dict) -> Path:
    relative = folder.name
    converted = CONVERTED_DIR / relative
    converted.mkdir(parents=True, exist_ok=True)

    folder_record = ledger["folders"].setdefault(relative, {})

    for item in folder.iterdir():
        if item.suffix.lower() not in SUPPORTED_EXTS or not item.is_file():
            continue
        file_hash = compute_hash(item)
        if folder_record.get(str(item)) == file_hash:
            log(f"Skipping already processed file {item}")
            continue
        dest_pdf = converted / (item.stem + ".pdf")
        if convert_file(item, dest_pdf):
            folder_record[str(item)] = file_hash
            log(f"Converted {item} -> {dest_pdf}")
    return converted


def merge_pdfs(pdf_dir: Path, output_path: Path) -> None:
    merger = PdfMerger()
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    valid_pdfs = []
    for pdf in pdf_files:
        if pdf.stat().st_size == 0:
            log(f"Skipping empty PDF {pdf}")
            continue
        try:
            merger.append(str(pdf))
            valid_pdfs.append(pdf)
        except Exception as e:  # noqa: BLE001
            log(f"Failed to append {pdf}: {e}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        merger.write(f)
    merger.close()
    log(f"Merged {len(valid_pdfs)} PDFs into {output_path}")


def chunk_pdf(pdf_path: Path, base_name: str) -> None:
    reader = PdfReader(str(pdf_path))
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    words = text.split()
    if not words:
        log(f"No text found in {pdf_path}; skipping chunking")
        return

    CHUNK_DIR.mkdir(exist_ok=True)
    chunk_size = 20000
    chunk_idx = 1
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(True, margin=15)
        pdf.add_font(
            "DejaVu",
            "",
            str(FONT_PATH),
            uni=True,
        )
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(0, 10, chunk_text)
        out_path = CHUNK_DIR / f"{base_name}_{chunk_idx:03d}.pdf"
        pdf.output(str(out_path))
        log(f"Created chunk {out_path}")
        chunk_idx += 1


def process_folder(folder: Path, ledger: Dict, base_name: str) -> None:
    converted_dir = scan_and_convert(folder, ledger)
    merged_pdf = MERGED_DIR / f"{base_name}.pdf"
    merge_pdfs(converted_dir, merged_pdf)
    chunk_pdf(merged_pdf, base_name)


def main() -> None:
    global KB_DIR, CHUNK_DIR

    ledger = load_ledger()

    existing_dir = ledger.get("output_dir")
    if existing_dir:
        use_existing = (
            input(f"Use existing output directory {existing_dir}? [Y/n] ")
            .strip()
            .lower()
        )
        if use_existing in {"", "y", "yes"}:
            CHUNK_DIR = Path(existing_dir).expanduser()
        else:
            chunk_path = input("Enter the output directory for chunked files: ")
            CHUNK_DIR = Path(chunk_path.strip()).expanduser()
            ledger["output_dir"] = str(CHUNK_DIR)
    else:
        chunk_path = input("Enter the output directory for chunked files: ")
        CHUNK_DIR = Path(chunk_path.strip()).expanduser()
        ledger["output_dir"] = str(CHUNK_DIR)

    source_path = input("Enter the full path of the folder to convert: ").strip()
    KB_DIR = Path(source_path).expanduser()
    if not KB_DIR.is_dir():
        print(f"{KB_DIR} is not a valid directory")
        return

    base_name = input(
        "Enter the base name for the merged and chunked PDF files: "
    ).strip()

    MERGED_DIR.mkdir(exist_ok=True)

    process_folder(KB_DIR, ledger, base_name)

    save_ledger(ledger)
    log("Processing complete")


if __name__ == "__main__":
    main()
