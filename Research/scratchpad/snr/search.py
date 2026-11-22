"""Random search over the Sniper settings + research extensions + up to 2 context filters, per timeframe.
Periods: A = 2021-2022, B = 2023 (selection), T = 2024 - 2 Oct 2026 (test, never used for selection).
Score at target X: min(edge A, edge B) with enough trades in A and B (edge = accuracy - 1 / (1 + X)).
Run: python3 -I search.py TF N SEED -> search_<tf>_<seed>.pkl (checkpoint every 250 configs; resumes)"""
import sys, os, pickle, time, numpy as np, datetime as dt
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import engine as E, evalx as V, outcome as O, features as F

T23 = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp())
XS = (0.2, 0.5, 1.0, 1.5, 2.0)
MINN = {5: (200, 100), 15: (80, 40), 60: (40, 20), 120: (30, 15), 180: (20, 10)}
C = F.CI
DIRF = ['h1_ema50', 'h4_ema50', 'd1_ema20', 'h1_slope', 'ema50_tf', 'ema200_tf', 'wvwap_side', 'vwap_slope20', 'cvd_s20', 'pdc_side', 'poc_dist', 'ppoc_dist']


def filters():
    out = []
    for k in DIRF:
        out.append((k, 1, 0.0, 0.0)); out.append((k, 5, 0.0, 0.0))
    for lo, hi in ((0, 0.7), (0.6, 1.0), (0.8, 1.3), (1.0, 9.0)):
        out.append(('atr_reg', 2, lo, hi))
    for a, b in ((5, 8), (9, 12), (12, 15), (13, 16), (16, 19), (17, 20), (6, 11), (11, 16), (15, 22), (12, 22)):
        out.append(('hour_ist', 2, a, b))
    for a, b in ((0, 0), (1, 3), (4, 4), (0, 3), (1, 4)):
        out.append(('dow', 2, a, b))
    for k in (3, 4, 5):
        out.append(('stack_up', 3, k, 0.0))
    for q in (0.8, 0.9):
        out.append(('upfrac', 3, q, 0.0))
    out.append(('sweep_lo', 3, 1.0, 0.0))
    for a, b in ((1, 1), (0, 0), (-1, -1), (0, 1), (-1, 0)):
        out.append(('va_pos', 4, a, b))
    for a, b in ((-9, 0), (0, 1), (1, 9), (-1, 1)):
        out.append(('poc_dist', 4, a, b))
    for a, b in ((-99, 0), (0, 2), (2, 99)):
        out.append(('pdc_side', 4, a, b))
    out.append(('rn_dist', 2, 0.0, 1.0)); out.append(('rn_dist', 2, 1.0, 99.0))
    return out


FILT = filters()


def pick(rng, vals, w=None):
    return vals[rng.choice(len(vals), p=w)] if w is not None else vals[rng.integers(len(vals))]


def sample(rng, tf):
    hi = tf >= 60
    kw = dict(aggRatio=pick(rng, [1.1, 1.2, 1.3, 1.5, 1.8, 2.2] if hi else [1.3, 1.5, 1.8, 2.2, 2.6, 3.0, 4.0]),
              absSens=pick(rng, [0.8, 1.0, 1.2, 1.5, 2.0]), deltaSrc=pick(rng, [0, 1]), volLen=pick(rng, [20, 40, 80]), absLen=pick(rng, [3, 5, 8]),
              divMin=pick(rng, [10, 15, 25]), wickPct=pick(rng, [30, 40, 50, 60]), aggRelV=pick(rng, [0, 0.8, 1.0, 1.3]), aggBody=pick(rng, [30, 50, 60, 70]),
              mode=pick(rng, [0, 0, 0, 1, 2]), expiry=pick(rng, [3, 5, 10, 20]), zone=pick(rng, [0, 1, 2]), bandMult=pick(rng, [1.0, 1.5, 2.0, 2.5]),
              zoneAtr=pick(rng, [0.25, 0.5, 0.75, 1.0, 1.5]), maxDist=pick(rng, [0, 1.5, 2.5, 4.0]), cvd=pick(rng, [0, 1, 2]), cvdLen=pick(rng, [2, 3, 5, 10]),
              slopeOn=pick(rng, [0, 1]), slopeLen=pick(rng, [3, 5, 10, 20]), cool=pick(rng, [0, 3, 6, 12]), entry=pick(rng, [0, 0, 0, 1]),
              absMask=pick(rng, [15, 15, 9, 1, 3, 8, 12]), minAbsN=pick(rng, [1, 1, 2]), aggDeltaPct=pick(rng, [0, 0, 40, 60]), confirm=pick(rng, [0, 0, 1]),
              minZoneN=pick(rng, [1, 1, 2, 3]), minBarsArm=pick(rng, [0, 1, 2]), maxRelVAgg=pick(rng, [0, 0, 2.0, 3.0]), sideReq=pick(rng, [0] * 8 + [1, -1]))
    if rng.random() < 0.6:
        kw.update(slMode=0, slBuf=pick(rng, [0.15, 0.3, 0.5, 1.0]), minRisk=pick(rng, [0.3, 1.0]), maxRisk=pick(rng, [2.0, 4.0, 6.0]))
    else:
        kw.update(slMode=1, slAtr=pick(rng, [1.0, 1.5, 2.0, 3.0]))
    u = rng.random()
    lv = 'pd'
    if u < 0.5:
        kw.update(ctx=0, vside=pick(rng, [1, 1, 0]))
    elif u < 0.7:
        kw.update(ctx=1, vside=pick(rng, [0, -1]))
    else:
        kw.update(ctx=2, vside=pick(rng, [0, 1, -1])); lv = pick(rng, ['pd', 'sx', 'pw'])
    nf = pick(rng, [0, 1, 1, 2])
    fl = [FILT[q] for q in rng.choice(len(FILT), nf, replace=False)] if nf else []
    for j, (k, m, a, b) in enumerate(fl):
        kw['f%dcol' % (j + 1)] = C[k]; kw['f%dmode' % (j + 1)] = m; kw['f%da' % (j + 1)] = a; kw['f%db' % (j + 1)] = b
    post = 'filt' if rng.random() < 0.3 else None
    return kw, lv, fl, post


def mets(o, mask):
    ok = o['filled'] & (o['end'] >= 0)
    if mask is not None:
        ok = ok & mask
    t = o['t']
    sp = dict(A=ok & (t < T23), B=ok & (t >= T23) & (t < O.TEST0), T=ok & (t >= O.TEST0))
    res = {}
    for X in XS:
        net, hit = O.net_at(o, X); g = ~np.isnan(net)
        for nm, m in sp.items():
            mm = m & g; n = int(mm.sum())
            res['%s_n_%g' % (nm, X)] = n
            res['%s_acc_%g' % (nm, X)] = hit[mm].mean() if n else np.nan
            res['%s_net_%g' % (nm, X)] = net[mm].mean() if n else np.nan
    return res


def main():
    tf, N, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    path = HERE + '/search_%d_%d.pkl' % (tf, seed)
    res = pickle.load(open(path, 'rb')) if os.path.exists(path) else []
    rng = np.random.default_rng(seed)
    for _ in range(len(res)):
        sample(rng, tf)                                   # the same configurations after a resume
    X = V.feat(tf)
    filt = E.load(tf)['filt']
    t0 = time.time()
    while len(res) < N:
        kw, lv, fl, post = sample(rng, tf)
        P = E.params(**kw)
        si, sd, se, ss, sf = E.run(tf, P, X, lv=lv)
        if len(si) == 0:
            res.append((kw, lv, fl, post, None)); continue
        o = V.outc(tf, si, sd, se, ss, int(kw.get('entry', 0)), False)
        m = mets(o, filt[si] if post == 'filt' else None)
        res.append((kw, lv, fl, post, m))
        if len(res) % 250 == 0:
            pickle.dump(res, open(path, 'wb'))
            print('tf %d seed %d: %d configs, %.0fs' % (tf, seed, len(res), time.time() - t0), flush=True)
    pickle.dump(res, open(path, 'wb'))
    print('done', tf, seed, len(res))


if __name__ == '__main__':
    main()
