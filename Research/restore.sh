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
echo "restored to $S"
