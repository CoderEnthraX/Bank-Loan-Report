"""Detail of one configuration: accuracy and net R at every target, per period (train 2021-23 / test 2024-26) and per year, longs / shorts,
all signals vs one trade at a time (a signal while the previous trade is open is skipped), with the user's filters, with the 23:55 IST force
close; z-score of the test edge (binomial). Used by the workbook builder."""
import sys, numpy as np, datetime as dt
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import engine as E, evalx as V, outcome as O

LV = (0.2, 0.3, 0.5, 0.6, 0.75, 1.0, 1.5, 2.0)
Y0 = {y: int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp()) for y in range(2021, 2028)}


def signals(tf, kw, lv='pd'):
    P = E.params(**kw)
    si, sd, se, ss, sf = E.run(tf, P, V.feat(tf), lv=lv)
    return si, sd, se, ss, sf


def one_at_a_time(o, X):
    """keep a signal only when the previous kept trade has ended (its end minute at target X: the hit minute is not known exactly,
    so the trade's full end minute (stop / 3R / force close) is used: conservative)"""
    keep = np.zeros(len(o['t']), bool); free_at = -1
    js = o['js'] if 'js' in o else None
    order = np.argsort(o['t'])
    for q in order:
        if not o['filled'][q] or o['end'][q] < 0:
            continue
        start = js[q] if js is not None else 0
        if start > free_at:
            keep[q] = True; free_at = o['jend'][q]
    return keep


def table(o, mask, lv=LV):
    rows = []
    for X in lv:
        net, hit = O.net_at(o, X)
        m = mask & ~np.isnan(net) & o['filled'] & (o['end'] >= 0)
        n = int(m.sum())
        acc = hit[m].mean() if n else np.nan
        rand = 1.0 / (1.0 + X)
        z = (acc - rand) / np.sqrt(rand * (1 - rand) / n) if n else np.nan
        rows.append(dict(X=X, n=n, acc=acc, rand=rand, edge=acc - rand if n else np.nan, z=z, net=net[m].mean() if n else np.nan, tot=net[m].sum() if n else 0.0))
    return rows


def full(tf, kw, lv='pd', post=None, usecut=False):
    si, sd, se, ss, sf = signals(tf, kw, lv)
    em = int(kw.get('entry', 0)) if kw.get('offset', 0) == 0 else 1
    o = V.outc(tf, si, sd, se, ss, em, usecut)
    o['js'] = E.load(tf)['j1'][si] + 1
    base = np.ones(len(si), bool)
    if post == 'filt':
        base &= E.load(tf)['filt'][si]
    t = o['t']
    per = dict(train=base & (t < O.TEST0), test=base & (t >= O.TEST0), all=base)
    out = {k: table(o, m) for k, m in per.items()}
    out['years'] = {y: table(o, base & (t >= Y0[y]) & (t < Y0[y + 1]), lv=(0.5, 0.6, 1.0)) for y in range(2021, 2027)}
    out['long_test'] = table(o, per['test'] & (sd == 1)); out['short_test'] = table(o, per['test'] & (sd == -1))
    out['long_train'] = table(o, per['train'] & (sd == 1)); out['short_train'] = table(o, per['train'] & (sd == -1))
    k1 = one_at_a_time(o, 1.0)
    out['oat_test'] = table(o, per['test'] & k1); out['oat_train'] = table(o, per['train'] & k1)
    out['n_signals'] = len(si); out['years_span'] = 5.75
    out['risk_med'] = float(np.median(o['r'])) if len(si) else np.nan
    return out, (si, sd, se, ss, sf, o)
