"""For every logged SENSEX/CRUDE trade: arm candle (entry match), ATR, logged stopR, normal and tight predictions."""
import sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl')
from load_xl import load
from engine2 import prepare
from engine import rma
fixT = {66: '09:40', 71: '10:10'}
OUT = []
for x in load():
    sym = x['sym']
    if sym not in ('CRUDE', 'SENSEX'): continue
    P = prepare(sym); T = P['T']; O, H, L, C = P['O'], P['H'], P['L'], P['C']; A = rma(P['tr'], 14)
    idx = {t: i for i, t in enumerate(T)}; d = x['d']
    f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin']))
    if f is None: print(x['n'], 'no bar'); continue
    best = None
    for k in range(1, 9):
        j = f - k; mid = (O[j] + C[j]) / 2
        e = max(mid, max(H[j-6:j])) if d > 0 else min(mid, min(L[j-6:j]))
        brk = C[j] > max(H[j-10:j]) if d > 0 else C[j] < min(L[j-10:j])
        sc = abs(e - x['entry']) / A[j] + (0 if brk and d*(C[j]-O[j]) > 0 else 0.5) + 0.01 * k
        if best is None or sc < best[0]: best = (sc, j, e)
    sc, j, e = best; a = A[j]
    sr = d * (x['entry'] - x['stop']) / a
    norm = e - d * 1.8 * a
    tight = min(e - 0.9 * a, L[j]) if d > 0 else max(e + 0.9 * a, H[j])
    OUT.append(dict(n=x['n'], sym=sym, j=j, f=f, d=d, sr=sr, tightLog=sr < 1.4))
    if __name__ == '__main__':
        print(f"#{x['n']:2d} {sym:6s} {T[j]} {'L' if d>0 else 'S'} entry log {x['entry']} model {e:.1f} (fit {sc:.2f}) stop log {x['stop']} stopR {sr:.2f} | norm {norm:.1f} tight {tight:.1f} candleExt {(L[j] if d>0 else H[j])} ATR {a:.2f} {'TIGHT' if sr<1.4 else ''}")
