import sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from pine_final import run
from engine2 import prepare
from engine import rma
X = load()
for sym in ['SENSEX', 'NIFTY', 'CRUDE']:
    P = prepare(sym); T = P['T']; O,H,L,C = P['O'],P['H'],P['L'],P['C']
    A = rma(P['tr'], 14)
    M = [m for m in run(sym) if '2026-10-05' <= T[m['fill']][:10] <= '2026-10-16']
    xs = [x for x in X if x['sym'] == sym]
    print('=====', sym, 'excel', len(xs), 'model', len(M))
    used = set()
    for x in xs:
        tin = x['date'] + ' ' + x['tin']
        best = None
        for k, m in enumerate(M):
            if m['dir'] != x['d']: continue
            for lab, idx in (('arm', m['arm']), ('fill', m['fill'])):
                dt = abs((__import__('datetime').datetime.strptime(T[idx], '%Y-%m-%d %H:%M') - __import__('datetime').datetime.strptime(tin, '%Y-%m-%d %H:%M')).total_seconds()) / 300
                if dt <= 3 and (best is None or dt < best[0]): best = (dt, k, lab, m)
        if best:
            dt, k, lab, m = best; used.add(k)
            print(f"  #{x['n']:>2} {tin} {'L' if x['d']>0 else 'S'} xl e {x['entry']:.6g} s {x['stop']:.6g} R {x['risk']:.4g} {x['maxtp']:>4} | MODEL {lab}{'' if dt==0 else '%+d'%dt} arm {T[m['arm']][11:]} fill {T[m['fill']][11:]} e {m['entry']:.6g} s {m['stop']:.6g} R {abs(m['entry']-m['stop']):.4g} exit {T[m['exit']][5:] if m['exit'] else None} {m['res']}")
        else:
            print(f"  #{x['n']:>2} {tin} {'L' if x['d']>0 else 'S'} xl e {x['entry']:.6g} s {x['stop']:.6g} R {x['risk']:.4g} {x['maxtp']:>4} | MODEL: none")
    for k, m in enumerate(M):
        if k not in used: print(f"     model-only: arm {T[m['arm']]} fill {T[m['fill']][11:]} {'L' if m['dir']>0 else 'S'} e {m['entry']:.6g} s {m['stop']:.6g} exit {T[m['exit']][5:] if m['exit'] else None} {m['res']}")
