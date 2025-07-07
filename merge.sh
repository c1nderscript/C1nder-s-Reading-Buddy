#!/bin/bash
set -euo pipefail

INGEST_DIR="./Ingest"
MERGED_DIR="./Merged"
OUTPUT_FILE="$MERGED_DIR/merged_output.md"

mkdir -p "$MERGED_DIR"
> "$OUTPUT_FILE"

for file in "$INGEST_DIR"/*.{md,mdx}; do
  if [ -f "$file" ]; then
    echo "## File: $(basename "$file")" >> "$OUTPUT_FILE"

    # Simple JSX removal: skip lines containing JSX tags <Component ...>
    # Adjust pattern to your JSX style as needed
    grep -vE '<[A-Za-z][^>]*>' "$file" >> "$OUTPUT_FILE"

    echo -e "\n\n---\n\n" >> "$OUTPUT_FILE"
  fi
done

echo "Markdown files merged (with JSX removed) into: $OUTPUT_FILE"

