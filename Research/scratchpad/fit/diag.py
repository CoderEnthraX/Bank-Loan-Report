"""Per-bar displacement diagnostics.  python3 -I diag.py SYM 'from' 'to' [N=6]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import prepare, rma
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 6
P = prepare(sym); R = P['rows']; atr = rma(P['tr'], 14)
for i, r in enumerate(R):
    if not (a <= r['t'] <= b) or i < N + 1: continue
    ph = max(x['h'] for x in R[i-N:i]); pl = min(x['l'] for x in R[i-N:i])
    rng = r['h'] - r['l']; body = abs(r['c'] - r['o']); A = atr[i]
    up = r['c'] > r['o']
    clo = ((r['h'] - r['c']) if up else (r['c'] - r['l'])) / rng * 100 if rng else 0
    brk = (r['c'] - ph) / A if up else (pl - r['c']) / A
    flag = ('DAYSTART ' if P['daystart'][i] else '') + ('L' if up and r['c'] > ph else 'S' if (not up) and r['c'] < pl else '-')
    print(f"{r['t'][5:]} {'up' if up else 'dn'} rng/A {rng/A:4.2f} body/A {body/A:4.2f} body% {100*body/rng if rng else 0:5.1f} closeFromExt% {clo:5.1f} brk/A {brk:+5.2f} c-vwap/A {(r['c']-r['vwap'])/A:+5.2f} ATR {A:.5g} {flag} {'MY-L' if r['lf'] else ''}{'MY-S' if r['sf'] else ''}")
