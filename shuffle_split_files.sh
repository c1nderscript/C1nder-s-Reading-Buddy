#!/bin/bash
set -e

# Determine repository root from this script's location, allow override
REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

# Directory containing split markdown files
SPLIT_DIR="${SPLIT_DIR:-"$REPO_ROOT/Split"}"

# Collect all part files
files=("$SPLIT_DIR"/part_*.md)

# Count files
count=${#files[@]}

if [ "$count" -eq 0 ]; then
  echo "No files found in $SPLIT_DIR"
  exit 1
fi

# Create an array of shuffled indices from 1 to count
mapfile -t shuffled_indices < <(shuf -i 1-"$count")

# Temporary rename files to avoid overwrites
for i in "${!files[@]}"; do
  mv "${files[$i]}" "${files[$i]}.tmp"
done

# Rename .tmp files to new shuffled numbers
for i in "${!files[@]}"; do
  old_tmp="${files[$i]}.tmp"
  new_num=${shuffled_indices[$i]}
  printf -v new_name "%s/part_%03d.md" "$SPLIT_DIR" "$new_num"
  mv "$old_tmp" "$new_name"
  echo "Renamed $(basename "$old_tmp") -> $(basename "$new_name")"
done

echo "Shuffling complete."
