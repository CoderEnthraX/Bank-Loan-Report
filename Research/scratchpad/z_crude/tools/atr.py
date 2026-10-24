import sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
P = prepare('CRUDE'); rows = P['rows']; tr = P['tr']
hl = [r['h']-r['l'] for r in rows]
a14 = rma(tr, 14); h14 = rma(hl, 14); a10=rma(tr,10); a20=rma(tr,20)
idx = {r['t']: r['i'] for r in rows}
for t in sys.argv[1:]:
    i = idx[t]; r = rows[i]
    L=6; ph=max(x['h'] for x in rows[i-L:i]); pl=min(x['l'] for x in rows[i-L:i])
    rng=r['h']-r['l']; body=abs(r['c']-r['o'])
    print(f"{t} O{r['o']:g} H{r['h']:g} L{r['l']:g} C{r['c']:g} rng {rng:g} body {body:g} ({body/rng*100 if rng else 0:.0f}%) vwap {r['vwap']:.1f} ph {ph:g} pl {pl:g} ATR14 {a14[i]:.3f} 1.8ATR {1.8*a14[i]:.3f} rng/ATR {rng/a14[i]:.2f} HL-ATR14 {h14[i]:.3f} 1.8HL {1.8*h14[i]:.3f} ATR10 {a10[i]:.2f} ATR20 {a20[i]:.2f}")
