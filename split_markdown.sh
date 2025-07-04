#!/bin/bash

# Fixed input file path
INPUT_FILE="/home/cinder/Documents/C_Scripts/Markdown Merger/Merged/merged_output.md"

# Output directory for split files
OUTPUT_DIR="/home/cinder/Documents/C_Scripts/Markdown Merger/Split"

# Max characters per split file
MAX_CHARS=20000

if [ ! -f "$INPUT_FILE" ]; then
  echo "File not found: $INPUT_FILE"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

split_index=1
current_chunk=""

while IFS= read -r line || [ -n "$line" ]; do
  current_chunk+="$line"$'\n'
  if [ ${#current_chunk} -ge $MAX_CHARS ]; then
    printf -v filename "%s/part_%03d.md" "$OUTPUT_DIR" "$split_index"
    echo "$current_chunk" > "$filename"
    echo "Created $filename"
    split_index=$((split_index + 1))
    current_chunk=""
  fi
done < "$INPUT_FILE"

if [ -n "$current_chunk" ]; then
  printf -v filename "%s/part_%03d.md" "$OUTPUT_DIR" "$split_index"
  echo "$current_chunk" > "$filename"
  echo "Created $filename"
fi

echo "Splitting complete. Files saved in $OUTPUT_DIR"
