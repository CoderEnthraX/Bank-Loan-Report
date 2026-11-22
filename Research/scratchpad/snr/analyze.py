"""Search analysis: rank the configurations by the selection score at target X (min of the edges in A = 2021-22 and B = 2023, with enough
trades), then show their test (2024 - 2026) results. Also the selection-bias check: the test edge of the top-k vs all configurations.
Run: python3 -I analyze.py TF [X ...]"""
import sys, glob, pickle, numpy as np
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import search as S, features as F

INV = {v: k for k, v in F.CI.items()}


def load(tf):
    res = []
    for f in sorted(glob.glob(HERE + '/search_%d_*.pkl' % tf)):
        res += [r for r in pickle.load(open(f, 'rb')) if r[4] is not None]
    return res


def score(m, X, tf):
    a, b = S.MINN[tf]
    if m['A_n_%g' % X] < a or m['B_n_%g' % X] < b:
        return -np.inf
    r = 1.0 / (1.0 + X)
    return min(m['A_acc_%g' % X], m['B_acc_%g' % X]) - r


def desc(kw, lv, fl, post):
    d = dict(E_DEFAULTS)
    s = ['%s=%g' % (k, v) for k, v in kw.items() if not k.startswith('f') and v != d.get(k)]
    if kw.get('ctx') == 2:
        s.append('levels=' + lv)
    for f in fl:
        s.append('F[%s %s %g %g]' % (f[0], {1: 'with', 5: 'against', 2: 'in', 3: 'min', 4: 'dirin'}[f[1]], f[2], f[3]))
    if post:
        s.append('userfilters')
    return ' '.join(s)


import engine as E
E_DEFAULTS = E.DEF


def main():
    tf = int(sys.argv[1]); xs = [float(x) for x in sys.argv[2:]] or [0.5, 1.0, 1.5]
    res = load(tf)
    print('TF %d: %d configurations' % (tf, len(res)))
    for X in xs:
        sc = np.array([score(r[4], X, tf) for r in res])
        ok = np.isfinite(sc)
        te = np.array([r[4]['T_acc_%g' % X] - 1 / (1 + X) if r[4]['T_n_%g' % X] >= S.MINN[tf][1] else np.nan for r in res])
        order = np.argsort(-np.where(ok, sc, -9))
        print('\n=== X = %g R: %d eligible; all eligible configs: mean test edge %+.2f pts (sd %.2f)' % (X, ok.sum(), 100 * np.nanmean(te[ok]), 100 * np.nanstd(te[ok])))
        for k in (10, 50, 200):
            top = order[:k]
            print('  top %3d by selection score: mean test edge %+.2f pts, %.0f%% positive' % (k, 100 * np.nanmean(te[top]), 100 * np.nanmean(te[top] > 0)))
        for q in order[:15]:
            kw, lv, fl, post, m = res[q]
            print('  sel %+5.1f | A %4.1f%% (%d) B %4.1f%% (%d) | TEST %4.1f%% (%d) edge %+5.1f net %+.3f | %s' % (
                100 * sc[q], 100 * m['A_acc_%g' % X], m['A_n_%g' % X], 100 * m['B_acc_%g' % X], m['B_n_%g' % X],
                100 * m['T_acc_%g' % X], m['T_n_%g' % X], 100 * te[q] if te[q] == te[q] else np.nan, m['T_net_%g' % X], desc(kw, lv, fl, post)))


if __name__ == '__main__':
    main()
