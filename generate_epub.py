#!/usr/bin/env python3
"""Convert split Markdown chunks to EPUB or MOBI format.

This script scans the ``Split`` directory for ``part_*.md`` files and converts
any new or changed files into EPUB format using pandoc. If ``kindlegen`` is
available it will additionally create MOBI files. Processed file hashes are
stored in ``ledger.json`` so unchanged files are skipped on subsequent runs.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SPLIT_DIR = Path(os.environ.get("SPLIT_DIR", "Split"))
KINDLE_DIR = Path(os.environ.get("KINDLE_DIR", "Kindle"))
LEDGER_PATH = Path("ledger.json")


def compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_ledger() -> dict:
    if LEDGER_PATH.exists():
        try:
            with LEDGER_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    data.setdefault("file_hashes", {})
    data.setdefault("epub_count", 0)
    data.setdefault("last_run", None)
    return data


def save_ledger(data: dict) -> None:
    data["last_run"] = datetime.utcnow().isoformat()
    with LEDGER_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main() -> None:
    KINDLE_DIR.mkdir(exist_ok=True)

    use_kindlegen = shutil.which("kindlegen") is not None
    ledger = load_ledger()
    file_hashes = ledger["file_hashes"]

    for md_file in sorted(SPLIT_DIR.glob("part_*.md")):
        file_hash = compute_hash(md_file)
        if file_hashes.get(str(md_file)) == file_hash:
            print(f"Skipping already converted {md_file}")
            continue

        epub_path = KINDLE_DIR / f"{md_file.stem}.epub"
        try:
            subprocess.run(["pandoc", str(md_file), "-o", str(epub_path)], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"Failed to convert {md_file}: {e}", file=sys.stderr)
            continue

        output_desc = str(epub_path)
        if use_kindlegen:
            mobi_name = f"{md_file.stem}.mobi"
            try:
                subprocess.run(["kindlegen", str(epub_path), "-o", mobi_name], check=True)
                epub_path.unlink(missing_ok=True)
                output_desc = str(KINDLE_DIR / mobi_name)
            except subprocess.CalledProcessError as e:
                print(f"kindlegen failed for {epub_path}: {e}", file=sys.stderr)

        file_hashes[str(md_file)] = file_hash
        ledger["epub_count"] += 1
        print(f"Converted {md_file} -> {output_desc}")

    save_ledger(ledger)
    print("EPUB generation complete.")


if __name__ == "__main__":
    main()
