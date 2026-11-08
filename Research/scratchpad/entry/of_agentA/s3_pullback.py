"""step 3: the pullback from the signal close to the retest fill. (a) diagnostic: pullback stats measured over the 1-minute candles
from the signal close up to (not incl.) the fill minute, by tercile [NOT a rule: state at fill]; (b) CANCEL rules decided at each
1-minute close (or chart-bar close) strictly before the fill minute: a cancelled order removes the trade, kept trades unchanged."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, numpy as np, warnings; warnings.filterwarnings('ignore')
from numba import njit
@njit(cache=True)
def _pbstat(dd, fm, hs, O1, C1, TV1):
    n = len(fm); k = np.zeros(n); v = np.zeros(n); dl = np.zeros(n)
    for s in range(n):
        if fm[s] < 0: continue
        for q in range(hs[s], fm[s]):
            k[s] += 1; v[s] += TV1[q]
            if C1[q] > O1[q]: dl[s] += TV1[q]
            elif C1[q] < O1[q]: dl[s] -= TV1[q]
    return k, v, dl
for tf in sys.argv[1:]:
    df = lib.ds(tf); c = lib.pb_ctx(tf); print('=====', tf)
    k, v, dl = _pbstat(c['d'], c['fm'], c['hs'], c['O1'], c['C1'], c['TV1'])
    vr = np.where(k > 0, (v / np.maximum(k, 1)) / c['sigvpm'], np.nan); dag = np.where(v > 0, -c['d'] * dl / np.maximum(v, 1), np.nan)
    fil = df.filled.to_numpy()
    print('minutes before fill: share 0 = %.2f, median %.0f' % ((k[fil] == 0).mean(), np.median(k[fil])))
    lib.stats(tf, k == 0, df, 'DIAG fill in 1st minute', tag='diag'); lib.stats(tf, (k >= 1) & (k <= 5), df, 'DIAG fill after 1-5 min', tag='diag')
    lib.stats(tf, k > 5, df, 'DIAG fill after >5 min', tag='diag')
    m = k >= 3
    for name, x in (('pb vol rate', vr), ('pb delta against %', dag)):
        q1, q2 = np.nanquantile(x[m & fil & (df.split == 'train').to_numpy()], [1 / 3, 2 / 3])
        lib.stats(tf, m & (x <= q1), df, 'DIAG %s <= %.2f (k>=3)' % (name, q1), tag='diag')
        lib.stats(tf, m & (x > q1) & (x < q2), df, 'DIAG %s mid (k>=3)' % name, tag='diag')
        lib.stats(tf, m & (x >= q2), df, 'DIAG %s >= %.2f (k>=3)' % (name, q2), tag='diag')
    print('--- cancel rules (keep = not cancelled)')
    for chart in (False, True):
        lab = 'chart-close' if chart else '1m-close'
        for thr in (1.0, 0.7, 0.5): lib.stats(tf, ~lib.cancel(tf, 0, thr, 2, chart), df, 'CXL %s pb vol rate > %.1f' % (lab, thr), tag='cxl')
        for thr in (0.3, 0.5): lib.stats(tf, ~lib.cancel(tf, 1, thr, 3, chart), df, 'CXL %s pb delta against > %.1f' % (lab, thr), tag='cxl')
        lib.stats(tf, ~lib.cancel(tf, 2, 0.3, 3, chart), df, 'CXL %s pb quiet vol rate < 0.3' % lab, tag='cxl')
        for thr in (0.3, 0.5): lib.stats(tf, ~lib.cancel(tf, 3, thr, 3, chart), df, 'CXL %s pb delta in favour > %.1f' % (lab, thr), tag='cxl')
