import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare
from gtscore import load_gt
from gtfeat import EXTRA, feats
def ema(x, n):
    a = 2 / (n + 1); o = []; s = None
    for v in x:
        s = v if s is None else a * v + (1 - a) * s; o.append(s)
    return o
def sma(x, n): return [None if i < n - 1 else sum(x[i-n+1:i+1]) / n for i in range(len(x))]
def htf(P, mins):
    """close series of a higher timeframe aligned to each 5m bar: last COMPLETED HTF close and its EMA20/50 (no lookahead)."""
    T = P['T']; C = P['C']; key = ('htf', mins)
    if key in P: return P[key]
    import datetime as dt
    buck = []; closes = []; cur = None; last = None
    for i, t in enumerate(T):
        d = dt.datetime.strptime(t, '%Y-%m-%d %H:%M'); m = (d.hour * 60 + d.minute) // mins
        k = (d.date(), m)
        if k != cur:
            if last is not None: closes.append(C[last])
            cur = k
        last = i; buck.append(len(closes))  # number of completed HTF bars before this 5m bar
    e20 = ema(closes, 20) if closes else []; e50 = ema(closes, 50) if closes else []
    P[key] = (buck, closes, e20, e50); return P[key]
tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
rows = [(t['sym'], t['d'], t['fill'], t['entry'], t['stop']) for t in tr] + EXTRA
res = []
for r in rows:
    f = feats(*r)
    if not f or f['R_atr'] is None: continue
    P = prepare(r[0]); i = P['T'].index(f['imp']); C = P['C']; d = r[1]
    out = dict(sym=r[0], fill=r[2], d=d, half=f['R_atr'] < 1.3, R=round(f['R_atr'], 2))
    for n in (20, 50, 100, 200):
        key = ('ema', n)
        if key not in P: P[key] = ema(C, n)
        out[f'e{n}'] = d * (C[i] - P[key][i]) > 0
    for mins in (15, 60, 240):
        b, cl, e20, e50 = htf(P, mins); k = b[i]
        out[f'h{mins}e20'] = k >= 1 and d * (cl[k-1] - e20[k-1]) > 0
        out[f'h{mins}e50'] = k >= 1 and d * (cl[k-1] - e50[k-1]) > 0
    # prior-day close / session open relation
    res.append(out)
keys = [k for k in res[0] if k not in ('sym', 'fill', 'd', 'half', 'R')]
print('trend filters: how well "with-trend -> 1.8, counter-trend -> 0.9" separates')
for k in keys:
    ok = sum(1 for o in res if o[k] == (not o['half']))
    print(f'  {k:8s} agree {ok}/{len(res)}   half trades with-trend? {[o[k] for o in res if o["half"]]}')
