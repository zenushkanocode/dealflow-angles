#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline --since-days 180 --max-per-feed 50
echo "Open docs/index.html (or: python -m http.server -d docs 8080)"
