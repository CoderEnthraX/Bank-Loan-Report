"""Matched logged trades vs model: entry/stop offsets, ATR variants implied by the logged risk."""
import sys, os, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
from engine import rma
import dm
inp = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"dayStopR": 0}
fixT = {66: '09:40'}
def sma(x, n): return [None if i < n-1 else sum(x[i-n+1:i+1])/n for i in range(len(x))]
for sym in ('SENSEX', 'CRUDE'):
    P = prepare(sym); T = P['T']; idx = {t: i for i, t in enumerate(T)}
    O,H,L,C=P['O'],P['H'],P['L'],P['C']
    tr = P['tr']; AT = {f'rma{n}': rma(tr, n) for n in (10, 14, 20)}; AT['sma14'] = sma(tr, 14)
    trades = dm.run(sym, inp)
    print('=====', sym)
    print(' #  date       fill  d  dEntry(log-mod)  dStop  logR/mod R | logR/1.8 / ATR: ' + ' '.join(AT) + ' rma14@fill rma14@arm-1  | tight')
    for x in load():
        if x['sym'] != sym: continue
        f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin']))
        m = None
        for t in trades:
            if t['dir'] == x['d'] and f is not None and abs(t['fill'] - f) <= 1 and (m is None or abs(t['fill']-f) < abs(m['fill']-f)): m = t
        if m is None: print(f" {x['n']} {x['date']} {x['tin']} MISS"); continue
        a = m['arm']; lr = abs(x['entry'] - x['stop']); mr = abs(m['entry'] - m['stop'])
        rat = ' '.join(f"{lr/1.8/AT[k][a]:.3f}" for k in AT)
        print(f" {x['n']} {x['date']} {x['tin']} {'L' if x['d']>0 else 'S'} {x['entry']-m['entry']:+8.2f} {x['stop']-m['stop']:+8.2f}  {lr/mr:.3f} | {rat}  {lr/1.8/AT['rma14'][m['fill']]:.3f} {lr/1.8/AT['rma14'][a-1]:.3f} | {m.get('tight')}")
