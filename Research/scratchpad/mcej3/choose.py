"""Best monthly settings, selection: every candidate's 70 monthly results ($1,000 fresh each month) -> metrics on the choice period
(2021-01 .. 2023-12, 36 months), the test period (2024-01 .. 2026-10, 34 months) and all 70. Picks are chosen on the choice period only.
Candidates: ARS = trade set x money run x month lock; GRID = subset of the 12 strategies x money run (per-strategy accounts, $1,000 / k each).
A candidate needs: no blown month in the choice period and trades in at least 30 of its 36 months.
Output: mcej3/choose.pkl (picks, top lists, full monthly rows of the picks) + choose.txt"""
import sys, pickle, itertools
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
M = pickle.load(open(S + '/mcej3/money_meta.pkl', 'rb'))
RUNS, RULES, CAPS, LOCKS = M['runs'], M['rules'], M['caps'], M['locks']
NM = len(M['months']); IN = np.arange(36); OUT = np.arange(36, NM)


def metrics(net, blown, active, dd=None):
    """net: (..., months) -> dict of arrays over the leading axes (dd: the deepest drop inside each month, when known)"""
    def part(ix):
        x = net[..., ix]
        d = dict(lose=(x < -1e-9).sum(-1), prof=(x > 1e-9).sum(-1), total=x.sum(-1), worst=x.min(-1), best=x.max(-1),
                 blown=blown[..., ix].sum(-1), active=active[..., ix].sum(-1))
        if dd is not None: d['dd'] = dd[..., ix].max(-1)
        return d
    return dict(IN=part(IN), OUT=part(OUT), ALL=part(np.arange(NM)))


def money_name(j, li=None):
    b, ri, ci = RUNS[j]
    s = 'base $%d, %s, %s' % (b, RULES[ri], CAPS[ci])
    if li is not None: s += ', month lock %s' % ('off' if LOCKS[li] is None else '+$%d' % LOCKS[li])
    return s


def rank(cands, how):
    """cands: list of dicts with IN / OUT / ALL metrics; how = 'steady' or 'profit'"""
    ok = [c for c in cands if c['IN']['blown'] == 0 and c['IN']['active'] >= 30]
    if how == 'steady':
        return sorted(ok, key=lambda c: (c['IN']['lose'], -c['IN']['total'], -c['IN']['worst']))
    best = min(c['IN']['lose'] for c in ok)
    return sorted([c for c in ok if c['IN']['lose'] <= best + 2], key=lambda c: (-c['IN']['total'], c['IN']['lose']))


def ars():
    Z = np.load(S + '/mcej3/money_ars.npz'); net, bl, n = Z['net'], Z['blown'], Z['n']
    met = metrics(net, bl, n > 0, Z['dd'])
    cands = []
    for i, s in enumerate(M['ars']):
        for j in range(len(RUNS)):
            for li in range(len(LOCKS)):
                c = dict(fam='ARS', set=i, key=s['key'], run=j, lock=li, name='%s | %s' % (s['key'], money_name(j, li)))
                for p in ('IN', 'OUT', 'ALL'): c[p] = {k: float(v[i, j, li]) for k, v in met[p].items()}
                cands.append(c)
    return cands, net


def grid():
    Z = np.load(S + '/mcej3/money_grid.npz'); GN, GB, GT = Z['net'], Z['blown'], Z['n']      # (12 strategies, k, runs, months)
    keep = []
    for k in range(1, 13):
        subs = list(itertools.combinations(range(12), k)); X = np.zeros((len(subs), 12), np.float32)
        for a, sb in enumerate(subs): X[a, list(sb)] = 1.0
        net = np.tensordot(X, GN[:, k - 1], axes=(1, 0))                                     # (subsets, runs, months)
        bl = np.tensordot(X, GB[:, k - 1].astype(np.float32), axes=(1, 0)) > 0
        act = np.tensordot(X, (GT[:, k - 1] > 0).astype(np.float32), axes=(1, 0)) > 0
        met = metrics(net, bl, act)
        # keep the best few per k under each ranking (all candidates would be 2.3 M)
        okm = (met['IN']['blown'] == 0) & (met['IN']['active'] >= 30)
        for how in ('steady', 'profit'):
            if how == 'steady':
                key = np.where(okm, met['IN']['lose'] * 1e7 - met['IN']['total'], np.inf)
            else:
                mn = met['IN']['lose'][okm].min() if okm.any() else 0
                key = np.where(okm & (met['IN']['lose'] <= mn + 2), -met['IN']['total'], np.inf)
            flat = np.argsort(key, axis=None)[:200]
            for f in flat:
                a, j = np.unravel_index(f, key.shape)
                if not np.isfinite(key[a, j]): continue
                c = dict(fam='GRID', subset=subs[a], k=k, run=int(j), name='%s | %s' % ('+'.join('S%d' % (g + 1) for g in subs[a]), money_name(int(j))),
                         monthly=net[a, j].astype(float).tolist())
                for p in ('IN', 'OUT', 'ALL'): c[p] = {kk: float(v[a, j]) for kk, v in met[p].items()}
                keep.append(c)
    uniq = {}
    for c in keep: uniq[c['name']] = c
    return list(uniq.values())


def fmt(c):
    f = lambda p: '%2d loss / %2d profit, %+8.0f, worst %+6.0f' % (c[p]['lose'], c[p]['prof'], c[p]['total'], c[p]['worst'])
    return '%s\n      2021-23: %s | 2024-26: %s | all 70: %s' % (c['name'], f('IN'), f('OUT'), f('ALL'))


if __name__ == '__main__':
    out = {}; L = []
    A, anet = ars()
    G = grid()
    for fam, C in (('ARS', A), ('GRID', G)):
        for how in ('steady', 'profit'):
            R = rank(C, how)
            out[(fam, how)] = R[:50]
            L.append('\n=== %s, %s (chosen on 2021-23) ===' % (fam, 'fewest losing months' if how == 'steady' else 'most profit within 2 losing months of the fewest'))
            for c in R[:15]: L.append(fmt(c))
            top = R[:50]
            L.append('   top 50 in the test period: losing months median %d (min %d, max %d), total median %+.0f; %d of 50 positive' % (
                np.median([c['OUT']['lose'] for c in top]), min(c['OUT']['lose'] for c in top), max(c['OUT']['lose'] for c in top),
                np.median([c['OUT']['total'] for c in top]), sum(1 for c in top if c['OUT']['total'] > 0)))
    pickle.dump(dict(top=out, meta=M), open(S + '/mcej3/choose.pkl', 'wb'))
    open(S + '/mcej3/choose.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
