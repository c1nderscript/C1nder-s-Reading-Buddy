#!/bin/bash
set -euo pipefail

# Use BASE_DIR if provided, otherwise default to the current directory
BASE_DIR="${BASE_DIR:-$(pwd)}"
SPLIT_DIR="$BASE_DIR/Split"
KINDLE_DIR="$BASE_DIR/Kindle"

mkdir -p "$KINDLE_DIR"

# Check if kindlegen is installed
if command -v kindlegen >/dev/null 2>&1; then
  USE_KINDLEGEN=true
else
  echo "kindlegen not found, will convert to .epub instead of .mobi"
  USE_KINDLEGEN=false
fi

# Ensure pandoc is installed
if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is required but was not found."
  echo "Install it from https://pandoc.org/installing.html and ensure it is in your PATH."
  exit 1
fi

for mdfile in "$SPLIT_DIR"/*.md; do
  base_name=$(basename "$mdfile" .md)
  if [ "$USE_KINDLEGEN" = true ]; then
    # Convert md -> epub with pandoc, then epub -> mobi with kindlegen
    epub_file="$KINDLE_DIR/${base_name}.epub"
    mobi_file="$KINDLE_DIR/${base_name}.mobi"

    pandoc "$mdfile" -o "$epub_file"
    kindlegen "$epub_file" -o "${base_name}.mobi"
    rm "$epub_file"
    echo "Converted $mdfile -> $mobi_file"
  else
    # Convert md -> epub only
    epub_file="$KINDLE_DIR/${base_name}.epub"
    pandoc "$mdfile" -o "$epub_file"
    echo "Converted $mdfile -> $epub_file"
  fi
done

echo "Conversion complete. Files are in $KINDLE_DIR"
