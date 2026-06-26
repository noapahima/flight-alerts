#!/bin/bash
set -e

cd "$(dirname "$0")"

if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

python3 main.py
