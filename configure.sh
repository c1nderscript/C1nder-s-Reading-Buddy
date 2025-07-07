#!/bin/bash

set -e

VENV_DIR="${1:-.venv}"
PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python interpreter not found." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install -r requirements.txt

# Install system packages if possible
FONT_PACKAGES=(
  fonts-dejavu-core
  fonts-dejavu-extra
  fonts-noto-core
  fonts-noto-cjk
  fonts-noto-color-emoji
  fonts-liberation
  fonts-freefont-ttf
  fonts-droid-fallback
  pandoc
)

if command -v apt-get >/dev/null 2>&1; then
  if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
  else
    SUDO=""
  fi
  $SUDO apt-get update
  $SUDO apt-get install -y "${FONT_PACKAGES[@]}"
fi

echo "Virtual environment setup complete. Activate with 'source $VENV_DIR/bin/activate'."
