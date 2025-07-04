#!/bin/bash

set -e

# Paths
BASE_DIR="$(pwd)"
INGEST_DIR="$BASE_DIR/Ingest"
SPLIT_DIR="$BASE_DIR/Split"
KINDLE_DIR="$BASE_DIR/Kindle"

mkdir -p "$INGEST_DIR" "$SPLIT_DIR" "$KINDLE_DIR"

echo "Step 1: Ingest and convert files to Markdown"
python3 ingest_and_convert.py

echo "Step 2: Split large markdown files into chunks"
for mdfile in "$INGEST_DIR"/*.md; do
  ./split_output.sh "$mdfile"
done

echo "Step 3: Shuffle chunked markdown files"
./shuffle.sh

echo "Step 4: Convert chunked markdown files to Kindle format"
./convert_to_kindle.sh

echo "All steps complete. Kindle-ready files in $KINDLE_DIR"
