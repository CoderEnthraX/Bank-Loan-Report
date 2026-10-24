"""Find trade boxes (pink/red stop box, green target box) and white entry lines in a screenshot, without viewing it.
Usage: python3 -I boxes.py <image-id|path> [x0 y0 x1 y1]   -> prints every box border rectangle in native pixel coords.
Detection: long horizontal runs of border-coloured pixels (pink ~ (240,80,140), green ~ (0,220,120)) paired with vertical runs."""
import sys, os, glob
from PIL import Image
U = '/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
src = sys.argv[1]
if not os.path.exists(src): src = glob.glob(U + src + '*')[0]
im = Image.open(src).convert('RGB'); W, H = im.size
x0, y0, x1, y1 = (map(int, sys.argv[2:6]) if len(sys.argv) >= 6 else (0, 0, W, H))
px = im.load()
def kind(p):
    r, g, b = p
    if r > 170 and g < 130 and b > 70 and r - g > 90: return 'P'      # pink/red border (stop side / box frame)
    if r > 150 and 100 < g < 205 and b > 110 and 20 < r - g < 90: return 'E'  # light-pink entry line
    if r > 200 and g > 200 and b > 200: return 'W'                     # white entry line
    if g > 150 and r < 140 and g - r > 70 and g - b > 20: return 'G'   # green border (TP4 side / box frame)
    if 40 < r < 110 and 105 < g < 175 and 75 < b < 145 and g - r > 45: return 't'  # faint TP1-TP3 lines
    return None
runs = []  # horizontal runs: (kind, y, xa, xb)
for y in range(y0, y1):
    cur = None; start = 0
    for x in range(x0, x1 + 1):
        k = kind(px[x, y]) if x < x1 else None
        if k != cur:
            if cur and x - start >= 10: runs.append((cur, y, start, x - 1))
            cur = k; start = x
# merge runs on adjacent rows (2-px borders) with same span
runs.sort(key=lambda r: (r[0], r[2], r[3], r[1]))
merged = []
for r in runs:
    if merged and merged[-1][0] == r[0] and abs(merged[-1][2] - r[2]) <= 2 and abs(merged[-1][3] - r[3]) <= 2 and r[1] - merged[-1][4] <= 2:
        m = merged[-1]; merged[-1] = (m[0], m[1], m[2], m[3], r[1])
    else:
        merged.append((r[0], r[1], r[2], r[3], r[1]))
lines = sorted(merged, key=lambda m: (m[2], m[1]))
print(f'image {os.path.basename(src)} {W}x{H}; horizontal border lines (kind y_top-y_bottom x_left-x_right): P=pink/red frame, G=green frame, E/W=entry line, t=TP1-3 line')
for k, ya, xa, xb, yb in lines:
    print(f'  {k} y {ya}-{yb}  x {xa}-{xb}  (len {xb-xa+1})')
