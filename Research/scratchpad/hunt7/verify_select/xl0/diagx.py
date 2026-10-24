"""For each Excel trade: find the arm candle j (fill-1..fill-8) whose model entry matches the logged entry,
print its gating conditions and the model state. Usage: python3 -I diagx.py SYM n1 n2 ..."""
import sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
from engine import rma
sym = sys.argv[1]; want = set(int(a) for a in sys.argv[2:])
P = prepare(sym); T = P['T']; O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = rma(P['tr'], 14); idx = {t: i for i, t in enumerate(T)}
for x in load():
    if x['sym'] != sym or x['n'] not in want: continue
    f = idx.get(x['date'] + ' ' + x['tin']); d = x['d']
    print(f"#{x['n']} {x['date']} {x['tin']} {'L' if d>0 else 'S'} entry {x['entry']} stop {x['stop']} R {x['risk']} out {x['maxtp']} exit {x['tout']}")
    if f is None: print('   fill bar not in data'); continue
    print(f"   fill bar {T[f]} O {O[f]} H {H[f]} L {L[f]} C {C[f]}  touches entry: {L[f] <= x['entry'] if d>0 else H[f] >= x['entry']}")
    for k in range(1, 9):
        j = f - k; mid = (O[j] + C[j]) / 2; rng = H[j] - L[j]
        hh6 = max(H[j-6:j]); ll6 = min(L[j-6:j]); hh10 = max(H[j-10:j]); ll10 = min(L[j-10:j])
        e = max(mid, hh6) if d > 0 else min(mid, ll6)
        tol = max(1.0, abs(x['entry']) * 2e-5)
        hit = abs(e - x['entry']) <= tol or abs(mid - x['entry']) <= tol
        if not hit: continue
        sR = abs(x['entry'] - x['stop']) / A[j]
        body = abs(C[j] - O[j]) / rng * 100 if rng else 0
        ext = ((H[j] - C[j]) if d > 0 else (C[j] - L[j])) / rng * 100 if rng else 0
        brk = d * (C[j] - (hh10 if d > 0 else ll10)) / A[j]
        mom = d * (C[j] - C[j - 10]) / A[j]
        vs = d * (V[j] - V[j - 3]) / A[j]; cv = d * (C[j] - V[j]) / A[j]
        print(f"   ARM? {T[j][11:]} k{k} entry_model {e:.6g} (mid {mid:.6g}, lvl6 {(hh6 if d>0 else ll6):.6g}) stop/ATR {sR:.2f} | dirOK {d*(C[j]-O[j])>0} rng/A {rng/A[j]:.2f} body% {body:.0f} ext% {ext:.0f} brk10/A {brk:+.2f} mom10/A {mom:+.2f} vwapSlope3/A {vs:+.3f} c-vwap/A {cv:+.2f} since {P['sinceStart'][j]}")
