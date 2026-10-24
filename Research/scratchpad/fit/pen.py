import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forced import eval_symbol, prepare, BASE
from gtscore import load_gt
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
c = dict(BASE); c.update({"brkLen":10,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1})
from engine2 import hh, ll
for sym in sorted({t['sym'] for t in tr}):
    P = prepare(sym); T = P['T']; O,H,L,C = P['O'],P['H'],P['L'],P['C']; A = P[('atr',14)] if ('atr',14) in P else None
    TP, FP, FN, fpl, ee = eval_symbol(P, c, [t for t in tr if t['sym'] == sym], [w for w in win if w['sym'] == sym], sym)
    A = P[('atr',14)]
    for ft, dd, at in fpl:
        i = T.index(at); f = T.index(ft); d = 1 if dd == 'L' else -1
        mid = (O[i]+C[i])/2; e = max(mid, hh(H,i,6)) if d>0 else min(mid, ll(L,i,6))
        pen = d*(e - (L[f] if d>0 else H[f]))/A[i]
        print('FP', sym, at, ft, dd, 'pen/A %.3f' % pen, 'bars', f-i)
for t in tr:
    P = prepare(t['sym']); T = P['T']; O,H,L,C = P['O'],P['H'],P['L'],P['C']
    if t['fill'] not in T or not t['entry']: continue
    f = T.index(t['fill']); d = t['d']; A = P[('atr',14)][f]
    pen = d*(t['entry'] - (L[f] if d>0 else H[f]))/A
    if pen < 0.05: print('TP', t['sym'], t['fill'], 'pen/A %.3f' % pen)
