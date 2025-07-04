#!/bin/bash
set -e

# Determine repository root from this script's location, allow override
REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

# Directories for input markdown chunks and Kindle output
SPLIT_DIR="${SPLIT_DIR:-"$REPO_ROOT/Split"}"
KINDLE_DIR="${KINDLE_DIR:-"$REPO_ROOT/Kindle"}"

mkdir -p "$KINDLE_DIR"

# Check if kindlegen is installed
if command -v kindlegen >/dev/null 2>&1; then
  USE_KINDLEGEN=true
else
  echo "kindlegen not found, will convert to .epub instead of .mobi"
  USE_KINDLEGEN=false
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
