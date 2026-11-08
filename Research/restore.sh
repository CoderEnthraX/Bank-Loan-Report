#!/usr/bin/env bash
# Rebuild the research scratchpad from this checkpoint (see CHECKPOINT.md).
# Every research script uses the absolute path in $S, so the files go back to exactly that place.
# Usage: bash Research/restore.sh        (about 3 minutes; needs python3, unzip, xz)
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad
mkdir -p "$S"
cp -a "$R/scratchpad/." "$S/"                      # all code and text files, same layout as the original scratchpad
cp -a "$R/inputs/wheels/." "$S/"                   # offline Pine parser wheels (pynescript, antlr4 runtime, click)
mkdir -p "$S/gold_raw" "$S/gold/data"              # gold: raw FxPro MT5 M1 export -> M1 / M5 / M15 / H1 bars
unzip -o -q "$R/inputs/GOLD_M1_2021_01_04_to_2026_10_02.zip" -d "$S/gold_raw"
python3 -I "$S/gold/convert.py" "$S/gold_raw/GOLD_M1_2021_01_04_to_2026_10_02.csv" "$S/gold/data"
for f in "$R"/results/gold/*.xz; do               # compact gold results: picks, every scored setting, search paths, recovery runs
  xz -dc "$f" > "$S/gold/$(basename "${f%.xz}")"
done
# entry research kit (CHECKPOINT items 24-25): python packages and the regenerated datasets (caches are not kept in the repo)
pip install --quiet numba scikit-learn lightgbm scipy || echo "pip install failed: install numba scikit-learn lightgbm scipy by hand"
if python3 -c "import numba" 2>/dev/null; then
  (cd "$S/entry" && python3 -I dataset.py H1 M15 M5 M1 && python3 -I barscan.py H1 M15 M5 && python3 -I baseline_m1.py) || echo "entry datasets: rebuild failed"
  [ -f "$S/entry/of.py" ] && (cd "$S/entry" && python3 -I of.py build) || true
fi
echo "restored to $S"
