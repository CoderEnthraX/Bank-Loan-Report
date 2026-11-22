"""Refinement: hill-climb the best random-search configurations (selection score at target X = min edge of A 2021-22 and B 2023, enough
trades), changing 1 - 2 settings or one filter at a time; the test period (2024-26) is only reported. Run: python3 -I refine.py TF X SEED
-> refine_<tf>_<X>.pkl"""
import sys, pickle, numpy as np
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import engine as E, evalx as V, search as S, analyze as A, features as F

FKEYS = ['f1col', 'f1mode', 'f1a', 'f1b', 'f2col', 'f2mode', 'f2a', 'f2b']


def evalc(tf, kw, lv, post, X, filt):
    si, sd, se, ss, sf = E.run(tf, E.params(**kw), X, lv=lv)
    if len(si) == 0:
        return None
    o = V.outc(tf, si, sd, se, ss, int(kw.get('entry', 0)), False)
    return S.mets(o, filt[si] if post == 'filt' else None)


def mutate(rng, tf, kw, lv, fl, post):
    kw = dict(kw); fl = list(fl)
    r2, lv2, fl2, post2 = S.sample(rng, tf)
    u = rng.random()
    if u < 0.7:
        keys = [k for k in r2 if k not in FKEYS and not k.startswith('f')]
        for k in rng.choice(keys, int(rng.integers(1, 3)), replace=False):
            kw[k] = r2[k]
            if k == 'ctx':
                lv = lv2
                kw['vside'] = r2['vside']
    elif u < 0.9:
        # replace / add / drop one filter
        j = int(rng.integers(0, 3))
        if j == 0 and fl:
            fl.pop(int(rng.integers(len(fl))))
        elif len(fl) < 2:
            fl.append(S.FILT[int(rng.integers(len(S.FILT)))])
        else:
            fl[int(rng.integers(2))] = S.FILT[int(rng.integers(len(S.FILT)))]
    else:
        post = None if post else 'filt'
    for k in FKEYS:
        kw.pop(k, None)
    for j, (k, m, a, b) in enumerate(fl):
        kw['f%dcol' % (j + 1)] = F.CI[k]; kw['f%dmode' % (j + 1)] = m; kw['f%da' % (j + 1)] = a; kw['f%db' % (j + 1)] = b
    return kw, lv, fl, post


def main():
    tf, X, seed = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
    res = A.load(tf)
    sc = np.array([A.score(r[4], X, tf) for r in res])
    order = np.argsort(-np.where(np.isfinite(sc), sc, -9))[:40]
    Xf = V.feat(tf); filt = E.load(tf)['filt']
    rng = np.random.default_rng(seed)
    out = []
    for q in order:
        kw, lv, fl, post, m = res[q]
        best = (A.score(m, X, tf), kw, lv, fl, post, m)
        start = best
        for it in range(60):
            c = mutate(rng, tf, best[1], best[2], best[3], best[4])
            mm = evalc(tf, c[0], c[1], c[3], X=Xf, filt=filt) if False else evalc(tf, c[0], c[1], c[3], Xf, filt)
            if mm is None:
                continue
            s = A.score(mm, X, tf)
            if s > best[0]:
                best = (s, c[0], c[1], c[2], c[3], mm)
        out.append(dict(start=start, best=best))
        b = best[5]; s0 = start[5]
        print('start sel %+5.1f test %+5.1f (%d) -> refined sel %+5.1f test %+5.1f (%d)' % (
            100 * start[0], 100 * (s0['T_acc_%g' % X] - 1 / (1 + X)), s0['T_n_%g' % X], 100 * best[0], 100 * (b['T_acc_%g' % X] - 1 / (1 + X)), b['T_n_%g' % X]), flush=True)
        pickle.dump(out, open(HERE + '/refine_%d_%g.pkl' % (tf, X), 'wb'))


if __name__ == '__main__':
    main()
