"""List candles in a screenshot region without viewing it: x-centre, wick top y, wick bottom y, body top/bottom y, colour.
Usage: python3 -I candles.py <image-id|path> x0 y0 x1 y1
Map y to price with two axis labels, then match the sequence of highs/lows to bars.py output to get exact bar times."""
import sys, os, glob
from PIL import Image
U = '/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
src = sys.argv[1]
if not os.path.exists(src): src = glob.glob(U + src + '*')[0]
im = Image.open(src).convert('RGB'); px = im.load()
x0, y0, x1, y1 = map(int, sys.argv[2:6])
def col(p):
    r, g, b = p
    if r > 150 and g < 110 and b < 120 and r - g > 80: return 'R'          # bearish candle
    if g > 110 and r < 100 and g - r > 55 and g > b + 8: return "U"        # bullish (teal) candle; excludes the cyan VWAP (b > g)
    return None
# mask out horizontal lines (box frames, TP lines, VWAP): pixels whose row run of same colour class is long
H = y1 - y0; Wd = x1 - x0
cls = [[col(px[x, y]) for x in range(x0, x1)] for y in range(y0, y1)]
for yy in range(H):
    row = cls[yy]; x = 0
    while x < Wd:
        k = row[x]; s = x
        while x < Wd and row[x] == k: x += 1
        if k and x - s > 12:
            for z in range(s, x): row[z] = None
colinfo = []
for xx in range(Wd):
    ys = [(yy, cls[yy][xx]) for yy in range(H) if cls[yy][xx]]
    colinfo.append(ys)
# group adjacent columns with candle pixels
groups = []; cur = []
for xx in range(Wd):
    if len(colinfo[xx]) >= 2: cur.append(xx)
    elif cur: groups.append(cur); cur = []
if cur: groups.append(cur)
print('x_centre  wick_top_y  wick_bot_y  body_top_y  body_bot_y  colour  width')
for g in groups:
    ys = [y for xx in g for y, _ in colinfo[xx]]
    kinds = [k for xx in g for _, k in colinfo[xx]]
    widest = max(g, key=lambda xx: len(colinfo[xx]))
    # body = rows covered by >=2 columns of the group
    rowcount = {}
    for xx in g:
        for y, _ in colinfo[xx]: rowcount[y] = rowcount.get(y, 0) + 1
    body = [y for y, n in rowcount.items() if n >= max(2, len(g) // 2)] or ys
    k = max(set(kinds), key=kinds.count)
    print(f'{x0 + (g[0] + g[-1]) / 2:8.1f}  {y0 + min(ys):10d}  {y0 + max(ys):10d}  {y0 + min(body):10d}  {y0 + max(body):10d}  {"bull" if k == "U" else "bear":6s}  {len(g)}')
