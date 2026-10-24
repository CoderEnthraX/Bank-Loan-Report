"""Research dataset: every trade of the clone (NEW rules) on all instruments, with outcome labels.
MFE/MAE in R measured from the fill bar, stop-first convention (on the bar where the stop is hit, its favourable extreme is NOT counted;
the fill bar counts only for the stop (its favourable extreme may predate the fill), exactly like the engine).
hitK = price reached entry + K*R before the stop. Output: trades.csv"""
import sys, csv, json, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
from engine import rma
spec = importlib.util.spec_from_file_location('m', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt4/combo.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
NEW = {"slopeCross": True, "minOpenBars": 0, "cooldownBars": 1, "dayStopR": 0, "tightOut": True, "erMin": 0.2}
SYMS = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
rows = []
for sym in SYMS:
    P = prepare(sym); T = P['T']; H, L = P['H'], P['L']; A = rma(P['tr'], 14); n = len(T)
    for x in M.run(sym, NEW):
        d = x['dir']; e = x['entry']; s = x['stop']; R = d * (e - s); f = x['fill']
        mfe = 0.0; mae = 0.0; k = f; stopbar = None
        while k < n:
            fav = d * ((H[k] if d > 0 else L[k]) - e) / R; adv = d * (e - (L[k] if d > 0 else H[k])) / R
            if adv >= 1.0 - 1e-9: stopbar = k; break
            if k > f: mfe = max(mfe, fav)   # fill bar: favourable extreme may predate the fill (engine checks only the stop there)
            mae = max(mae, adv); k += 1
            if mfe >= 3.0: break
        rows.append(dict(sym=sym, arm=T[x['arm']], fill=T[f], exit=T[x['exit']] if x['exit'] is not None else '', dir=d, entry=round(e, 6), stop=round(s, 6),
                         R=round(R, 6), atr=round(A[x['arm']], 6), riskATR=round(R / A[x['arm']], 3), tight=int(bool(x.get('tight'))),
                         res2R=x['res'] if x['res'] is not None else '', mfeR=round(mfe, 3), maeR=round(mae, 3),
                         hit06=int(mfe >= 0.6), hit1=int(mfe >= 1.0), hit15=int(mfe >= 1.5), hit2=int(mfe >= 2.0), stopped_before_3R=int(stopbar is not None),
                         barsHeld=(x['exit'] - f) if x['exit'] is not None else '', armIdx=x['arm'], fillIdx=f))
w = csv.DictWriter(open('trades.csv', 'w', newline=''), fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import collections
print('trades', len(rows))
for sym in SYMS:
    r = [x for x in rows if x['sym'] == sym and x['res2R'] != '']
    print(f"{sym:15s} n={len(r):4d} hit1R={sum(x['hit1'] for x in r)/len(r):.1%} hit1.5R={sum(x['hit15'] for x in r)/len(r):.1%} hit2R={sum(x['hit2'] for x in r)/len(r):.1%} totalR(2R exit)={sum(x['res2R'] for x in r):+.0f}  {r[0]['fill'][:10]}..{r[-1]['fill'][:10]}")
r = [x for x in rows if x['res2R'] != '']
print(f"ALL n={len(r)} hit0.6R={sum(x['hit06'] for x in r)/len(r):.1%} hit1R={sum(x['hit1'] for x in r)/len(r):.1%} hit1.5R={sum(x['hit15'] for x in r)/len(r):.1%} hit2R={sum(x['hit2'] for x in r)/len(r):.1%} totalR={sum(x['res2R'] for x in r):+.0f}")
# consistency: hit2 must equal res2R==2
bad = [x for x in r if (x['res2R'] == 2.0) != bool(x['hit2'])]
print('label check (hit2 vs engine 2R result) mismatches:', len(bad), bad[:3])
