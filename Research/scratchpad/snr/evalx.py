"""Evaluation of one Sniper configuration: signals (engine), outcomes on M1 (cached by bar / direction / entry / stop), metrics for the
train (2021-2023) and test (2024 - 2 Oct 2026) periods: trades, accuracy at X R, the edge over a random entry (accuracy - 1 / (1 + X)),
net R per trade (costs 0.23 / oz), accuracy by year. post: optional post-hoc mask (the user's filters: kill zones, hours, news)."""
import sys, numpy as np, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr')
import engine as E, outcome as O

XS = (0.2, 0.5, 1.0, 1.5, 2.0)
YEAR0 = [int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp()) for y in range(2021, 2028)]
_OC = {}
_FX = {}


def feat(tf):
    if tf not in _FX:
        _FX[tf] = np.load('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/feat_%d.npz' % tf)['X']
    return _FX[tf]


def outc(tf, si, sd, se, ss, entry_mode, usecut):
    key = (tf, entry_mode, usecut)
    cache = _OC.setdefault(key, {})
    ks = list(zip(si.tolist(), sd.tolist(), np.round(se, 6).tolist(), np.round(ss, 6).tolist()))
    new = [q for q, k in enumerate(ks) if k not in cache]
    if new:
        nq = np.array(new)
        o = O.outcomes(tf, si[nq], sd[nq], se[nq], ss[nq], entry_mode=entry_mode, usecut=usecut)
        for j, q in enumerate(new):
            cache[ks[q]] = (o['mfe'][j], o['end'][j], o['lossR'][j], o['exitR'][j], o['filled'][j], o['jend'][j])
    arr = np.array([cache[k] for k in ks]) if ks else np.zeros((0, 6))
    b = E.load(tf)
    return dict(mfe=arr[:, 0], end=arr[:, 1].astype(int), lossR=arr[:, 2], exitR=arr[:, 3], filled=arr[:, 4].astype(bool), jend=arr[:, 5].astype(int),
                r=np.abs(se - ss), t=b['ue'][si])


def metrics(o, mask=None):
    ok = o['filled'] & (o['end'] >= 0)
    if mask is not None:
        ok = ok & mask
    tr = ok & (o['t'] < O.TEST0); te = ok & (o['t'] >= O.TEST0)
    res = {}
    for X in XS:
        net, hit = O.net_at(o, X)
        g = ~np.isnan(net)
        for nm, m in (('tr', tr & g), ('te', te & g), ('all', ok & g)):
            n = int(m.sum())
            res['%s_n_%g' % (nm, X)] = n
            res['%s_acc_%g' % (nm, X)] = hit[m].mean() if n else np.nan
            res['%s_edge_%g' % (nm, X)] = (hit[m].mean() - 1.0 / (1.0 + X)) if n else np.nan
            res['%s_net_%g' % (nm, X)] = net[m].mean() if n else np.nan
        if X == 1.0:
            for y in range(2021, 2027):
                m = ok & g & (o['t'] >= YEAR0[y - 2021]) & (o['t'] < YEAR0[y - 2020])
                res['acc1_%d' % y] = hit[m].mean() if m.sum() else np.nan
                res['n1_%d' % y] = int(m.sum())
    res['n'] = int(ok.sum()); res['n_tr'] = int(tr.sum()); res['n_te'] = int(te.sum())
    res['risk_med'] = float(np.median(o['r'][ok])) if ok.sum() else np.nan
    return res


def evaluate(tf, P, X=None, usecut=False, post=None):
    si, sd, se, ss, sf = E.run(tf, P, X)
    o = outc(tf, si, sd, se, ss, int(P[E.PI['entry']]) if P[E.PI['offset']] == 0 else 1, usecut)
    mask = None
    if post == 'filt':
        mask = E.load(tf)['filt'][si]
    m = metrics(o, mask)
    return m, (si, sd, se, ss, sf, o)
