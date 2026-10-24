import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from bstate import *
from pfeat import pf
def first_e(P, i, d, kind):
    ev = events(P, kind); ds = i - P['sinceStart'][i]
    return not any(ev[j] == d for j in range(ds, i))
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]; Dd = daily(P); k = dayidx(P, i); pd = Dd[k - 1]; td = Dd[k]; p2 = Dd[k - 2]
    f = dict(fdE1=first_e(P, i, d, 'E1'), fdE2=first_e(P, i, d, 'E2'), fdE3=first_e(P, i, d, 'E3'),
             pdBody=d * (pd['c'] - pd['o']) / A, pd2=d * (pd['c'] - p2['c']) / A, p2Body=d * (p2['c'] - p2['o']) / A,
             pdRng=(pd['h'] - pd['l']) / A, pdClosePos=((pd['c'] - pd['l']) / (pd['h'] - pd['l']) if d > 0 else (pd['h'] - pd['c']) / (pd['h'] - pd['l'])),
             gap=d * (td['o'] - pd['c']) / A, vsPDC=d * (P['C'][i] - pd['c']) / A, vsPDO=d * (P['C'][i] - pd['o']) / A,
             vsPDH=d * (P['C'][i] - (pd['h'] if d > 0 else pd['l'])) / A, vsPDL=d * (P['C'][i] - (pd['l'] if d > 0 else pd['h'])) / A,
             pdVW=d * (pd['c'] - pd['vw']) / A if pd['vw'] else 0, dOpen=d * (P['C'][i] - td['o']) / A, since=P['sinceStart'][i])
    rows.append((t, f))
if __name__ == '__main__':
    for t, f in rows:
        if f['fdE1'] and f['pdBody'] < 0 or t['tight']:
            print(f"{t['sym']:6s} {t['fill'][5:]} {'L' if t['d']>0 else 'S'} {'T' if t['tight'] else ' '}", ' '.join((f"{k}={v:+.2f}" if isinstance(v, float) else f"{k}={int(v)}") for k, v in f.items()))
