"""dump model conditions for bars: python3 -I conds.py SYM 'YYYY-MM-DD HH:MM' ..."""
import sys, datetime
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma
sym = sys.argv[1]; P = eprep(sym); R = P['rows']; atr = rma(P['tr'], 14)
O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
idx = {r['t']: k for k, r in enumerate(R)}
for t in sys.argv[2:]:
    i = idx[t]; A = atr[i]; d = 1 if C[i] > O[i] else -1
    ph = max(H[i-10:i]); pl = min(L[i-10:i]); eh = max(H[i-6:i]); el = min(L[i-6:i]); rng = H[i]-L[i]
    mid = (O[i]+C[i])/2; ent = max(mid, eh) if d > 0 else min(mid, el)
    vs = [d*(V[i-k]-V[i-k-1])/A for k in range(6)]
    print(f"{t} {'UP' if d>0 else 'DN'} O {O[i]} H {H[i]} L {L[i]} C {C[i]} ATR {A:.3f}")
    print(f"   brk10 {d*(C[i]-(ph if d>0 else pl))/A:+.3f}A (lvl {ph if d>0 else pl}) rng {rng/A:.2f}A body {abs(C[i]-O[i])/rng*100:.1f}% ext {((H[i]-C[i]) if d>0 else (C[i]-L[i]))/rng*100:.1f}% mom10 {d*(C[i]-C[i-10])/A:+.2f}A mom5 {d*(C[i]-C[i-5])/A:+.2f}A c-vwap {d*(C[i]-V[i])/A:+.2f}A vsl3 {d*(V[i]-V[i-3])/A:+.4f}A vsl1..6 {' '.join(f'{x:+.3f}' for x in vs)}")
    print(f"   entry {ent:.6g} (mid {mid}, lvl6 {eh if d>0 else el}) close-entry {d*(C[i]-ent)/A:.2f}A  entry-lvl10 {d*(ent-(ph if d>0 else pl))/A:+.2f}A  next bars: " + ' | '.join(f"{R[i+k]['t'][11:]} O{O[i+k]} H{H[i+k]} L{L[i+k]} C{C[i+k]}" for k in range(1,4)))
