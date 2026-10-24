"""stop_author feature library: DMI/ADX, ER, CHOP, EMAs, VWAP sigma, HTF resample."""
import sys, math
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from engine import rma
from adxfit import dmi
from volrec import recover

def ema(x, n):
    a = 2 / (n + 1); o = []; s = None
    for v in x:
        s = v if s is None else a * v + (1 - a) * s; o.append(s)
    return o
def sma(x, n):
    o = [None] * len(x); s = 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n: s -= x[i - n]
        if i >= n - 1: o[i] = s / n
    return o

def get(sym):
    P = prepare(sym)
    if 'dmi' not in P: P['dmi'] = dmi(P['rows'], 14, 14)
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    if 'vsd' not in P: recover(sym)
    C = P['C']
    for n in (9, 20, 21, 50, 100, 200):
        if ('ema', n) not in P: P[('ema', n)] = ema(C, n)
    return P

def er(C, i, n):
    ch = abs(C[i] - C[i - n]); v = sum(abs(C[k] - C[k - 1]) for k in range(i - n + 1, i + 1))
    return ch / v if v else 0.0
def ers(C, i, n):
    ch = C[i] - C[i - n]; v = sum(abs(C[k] - C[k - 1]) for k in range(i - n + 1, i + 1))
    return ch / v if v else 0.0
def chop(P, i, n=14):
    H, L, tr = P['H'], P['L'], P['tr']; s = sum(tr[i - n + 1:i + 1]); rg = max(H[i - n + 1:i + 1]) - min(L[i - n + 1:i + 1])
    return 100 * math.log10(s / rg) / math.log10(n) if rg > 0 else 0
def linreg(C, i, n):
    xs = list(range(n)); ys = C[i - n + 1:i + 1]; mx = (n - 1) / 2; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys)); syy = sum((y - my) ** 2 for y in ys)
    b = sxy / sxx; r2 = sxy * sxy / (sxx * syy) if syy else 0
    return b, r2

def feats(P, i):
    dip, dim, adx = P['dmi']; C, V, H, L = P['C'], P['V'], P['H'], P['L']; A = P[('atr', 14)][i]; sd = P['vsd'][i] or 0
    f = dict(adx=adx[i], dip=dip[i], dim=dim[i], spr=dip[i] - dim[i], sl1=adx[i] - adx[i - 1], sl3=adx[i] - adx[i - 3], sl5=adx[i] - adx[i - 5], sl10=adx[i]-adx[i-10],
             pk20=adx[i] - max(adx[i - 19:i + 1]), pk50=adx[i] - max(adx[i - 49:i + 1]), lo20=adx[i]-min(adx[i-19:i+1]),
             er10=er(C, i, 10), er14=er(C, i, 14), er20=er(C, i, 20), ers14=ers(C,i,14), chop14=chop(P, i, 14), chop20=chop(P, i, 20),
             cv=(C[i] - V[i]) / A, cvs=(C[i] - V[i]) / sd if sd else 0, vsl3=(V[i] - V[i - 3]) / A, vsl10=(V[i] - V[i - 10]) / A,
             ce20=(C[i] - P[('ema', 20)][i]) / A, e2050=(P[('ema', 20)][i] - P[('ema', 50)][i]) / A, e50200=(P[('ema', 50)][i] - P[('ema', 200)][i]) / A,
             e921=(P[('ema',9)][i]-P[('ema',21)][i])/A, ce200=(C[i]-P[('ema',200)][i])/A, ce50=(C[i]-P[('ema',50)][i])/A,
             sdA=sd / A, ss=P['sinceStart'][i])
    b, r2 = linreg(C, i, 20); f['lr20'] = b / A; f['r2_20'] = r2
    b, r2 = linreg(C, i, 50); f['lr50'] = b / A; f['r2_50'] = r2
    return f

def htf(P, m):
    """Resample to m-minute bars aligned to session start (daystart). Returns (hrows, map5->index of developing HTF bar, values computed incl developing bar)."""
    key = ('htf', m)
    if key in P: return P[key]
    T, O, H, L, C = P['T'], P['O'], P['H'], P['L'], P['C']
    import datetime as dt
    bars = []; idx = [0] * len(T); cur = None; t0 = None
    for i in range(len(T)):
        t = dt.datetime.strptime(T[i], '%Y-%m-%d %H:%M')
        if P['daystart'][i]: t0 = t
        if t0 is None: t0 = t
        slot = int((t - t0).total_seconds() // 60 // m)
        k = (t0, slot)
        if cur is None or cur['k'] != k:
            cur = dict(k=k, o=O[i], h=H[i], l=L[i], c=C[i], first=i, last=i); bars.append(cur)
        else:
            cur['h'] = max(cur['h'], H[i]); cur['l'] = min(cur['l'], L[i]); cur['c'] = C[i]; cur['last'] = i
        idx[i] = len(bars) - 1
    P[key] = (bars, idx); return P[key]

def htf_dmi_at(P, m, i, n=14):
    """ADX/DI of the m-minute series with the developing HTF bar truncated at 5m bar i (realtime semantics)."""
    bars, idx = htf(P, m); k = idx[i]
    rows = [dict(o=b['o'], h=b['h'], l=b['l'], c=b['c']) for b in bars[:k]]
    b = bars[k]; seg = range(b['first'], i + 1)
    rows.append(dict(o=b['o'], h=max(P['H'][j] for j in seg), l=min(P['L'][j] for j in seg), c=P['C'][i]))
    rows = rows[-600:]
    dip, dim, adx = dmi(rows, n, n)
    return dip[-1], dim[-1], adx[-1], rows

def htf_series(P, m, n=14):
    """Per 5m bar: DMI/ADX/chop/ER of the last COMPLETED m-minute bar (historical lookahead_off semantics)."""
    key = ('htfs', m, n)
    if key in P: return P[key]
    bars, idx = htf(P, m)
    rows = [dict(o=b['o'], h=b['h'], l=b['l'], c=b['c']) for b in bars]
    dip, dim, adx = dmi(rows, n, n)
    C = [r['c'] for r in rows]
    trh = [rows[0]['h'] - rows[0]['l']] + [max(b['h'] - b['l'], abs(b['h'] - a['c']), abs(b['l'] - a['c'])) for a, b in zip(rows, rows[1:])]
    atrh = rma(trh, 14)
    ch = [None] * len(rows); e = [None] * len(rows); es = [None]*len(rows)
    for k in range(20, len(rows)):
        s = sum(trh[k - 13:k + 1]); rg = max(r['h'] for r in rows[k - 13:k + 1]) - min(r['l'] for r in rows[k - 13:k + 1])
        ch[k] = 100 * math.log10(s / rg) / math.log10(14) if rg > 0 else 0
        e[k] = er(C, k, 10); es[k] = ers(C, k, 10)
    e20 = ema(C, 20); e50 = ema(C, 50)
    out = []
    for i in range(len(P['T'])):
        k = idx[i]
        if bars[k]['last'] != i: k -= 1   # developing bar not visible historically
        if k < 30 or adx[k] is None: out.append(None); continue
        out.append(dict(adx=adx[k], spr=dip[k] - dim[k], chop=ch[k], er=e[k], ers=es[k], dirc=1 if rows[k]['c'] > rows[k]['o'] else -1,
                        e2050=(e20[k] - e50[k]) / atrh[k], ce20=(rows[k]['c'] - e20[k]) / atrh[k], k=k))
    P[key] = out; return out
