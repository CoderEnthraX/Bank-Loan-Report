import sys
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from tightdata import TRADES
def daily(P):
    if 'daily' in P: return P['daily']
    st = [i for i, x in enumerate(P['daystart']) if x]; st.append(len(P['T']))
    D = []
    for a, b in zip(st[:-1], st[1:]):
        D.append(dict(a=a, b=b, o=P['O'][a], h=max(P['H'][a:b]), l=min(P['L'][a:b]), c=P['C'][b - 1], vw=P['V'][b - 1]))
    P['daily'] = D; return D
def dayidx(P, i):
    D = daily(P)
    for k, x in enumerate(D):
        if x['a'] <= i < x['b']: return k
def ema(x, n):
    a = 2 / (n + 1); o = []; s = None
    for v in x: s = v if s is None else a * v + (1 - a) * s; o.append(s)
    return o
def feats(P, i):
    D = daily(P); k = dayidx(P, i); c = P['C'][i]; pd = D[k - 1]; A = P[('atr', 14)][i]
    closes = [x['c'] for x in D[:k]]
    f = {}
    f['vsPDR'] = 1 if c > pd['h'] else (-1 if c < pd['l'] else 0)
    f['vsPDC'] = (c - pd['c']) / A
    f['vsPDVW'] = (c - pd['vw']) / A if pd['vw'] else 0
    for n in (5, 10, 20, 50):
        e = ema(closes, n)[-1] if closes else c; f[f'vsDE{n}'] = (c - e) / A
        f[f'DE{n}sl'] = (ema(closes, n)[-1] - ema(closes, n)[-2]) / A if len(closes) > 2 else 0
    f['pdDir'] = 1 if pd['c'] > pd['o'] else -1
    f['pd2'] = (pd['c'] - D[k - 2]['c']) / A
    return f
if __name__ != '__main__': SNAP = []
else: SNAP = [('CRUDE','2026-10-09 13:40',-1),('EURUSD','2026-10-12 12:50',-1),('GC','2026-10-12 13:00',0),('NASDAQ','2026-10-12 12:45',0),('NASDAQ','2026-10-09 13:40',0),
        ('NIFTY','2026-10-12 12:10',-1),('NIFTY','2026-10-12 12:40',-1),('SENSEX','2026-10-12 12:40',-1),('US30','2026-10-12 13:00',0)]
if __name__ == '__main__': print('SNAPSHOTS (table bias)')
for s, t, b in SNAP:
    P = prepare(s); i = P['T'].index(t); f = feats(P, i)
    print(f"  {s:6s} {t} bias {b:+d}", ' '.join(f"{k}={v:+.2f}" if isinstance(v, float) else f"{k}={v:+d}" for k, v in f.items()))
print('TIGHT + twin') if __name__ == '__main__' else None
for t in (TRADES if __name__ == '__main__' else []):
    if t['tight'] or (t['sym'] == 'SENSEX' and t['fill'].startswith('2026-10-09')):
        P = prepare(t['sym']); f = feats(P, t['arm_i']); d = t['d']
        print(f"  {t['sym']:6s} {t['fill']} {'L' if d>0 else 'S'} {'T' if t['tight'] else ' '}", ' '.join(f"{k}={d*v:+.2f}" if isinstance(v, float) else f"{k}={d*v:+d}" for k, v in f.items()))
