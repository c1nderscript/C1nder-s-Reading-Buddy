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

echo "Step 2: Merge markdown files"
./merge.sh

echo "Step 3: Split merged markdown file into chunks"
./split_markdown.sh

echo "Step 4: Shuffle chunked markdown files"
./shuffle_split_files.sh

echo "Step 5: Convert chunked markdown files to Kindle format"
./convert_to_kindle.sh

echo "All steps complete. Kindle-ready files in $KINDLE_DIR"
