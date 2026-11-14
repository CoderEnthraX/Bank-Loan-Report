"""How often the TradingView-execution edge cases happen (engine v1 logic, chart M5 and M1), per strategy:
 A  entries on the activation bar (the buy stop must already be in place at the previous close)
 G  activation bars with previous close < E <= open (a gap through a buy stop placed at the previous close; the model does not enter)
 U  levels whose activation-bar previous close was >= E (TradingView cannot hold that buy stop)
 B  trades whose BE / salvage trigger and exit happen on the same bar after the trigger (the model exits inside the candle)
 E  trades that open and close on the same bar"""
import sys, numpy as np, numba as nb
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
from final11 import ALL


@nb.njit(cache=True)
def act_stats(O, C, kk, ph, off):
    n = len(O); nl = 0; gap = 0; unarmed = 0; actbar = np.full(n, -1, np.int64)
    for i in range(1, n):
        if kk[i] != kk[i - 1]:
            v = ph[kk[i]]
            if not np.isnan(v):
                E = v * (1.0 + off / 100.0); nl += 1; actbar[i] = 1
                if C[i - 1] < E and O[i] >= E: gap += 1
                if C[i - 1] >= E: unarmed += 1
    return nl, gap, unarmed, actbar


B = EN.load()
for ctf in sys.argv[1:] or ['M5']:
    t, O, H, L, C = EN.chart(B, ctf)
    print('chart', ctf)
    for s, p in enumerate(ALL, 1):
        if EN.TF_SEC[p[0]] < EN.TF_SEC[ctf]: continue
        kk = (np.searchsorted(B[p[0] + '_t'], t, side='right') - 1).astype(np.int64); ph = EN.pivots(B[p[0] + '_H'], p[2], p[1])
        nl, gap, unarmed, actbar = act_stats(O, C, kk, ph, p[3])
        tr = EN.run(B, ctf, *p); ei = tr[:, 0].astype(int); xi = tr[:, 2].astype(int)
        A = int(np.sum((actbar[ei] == 1) & (tr[:, 7] == 0)))
        same = int(np.sum(ei == xi)); bes = int(np.sum((ei != xi) & ((tr[:, 4] == 3) | (tr[:, 4] == 4))))
        print('  S%-2d %-3s levels %6d | A activation-bar entries %4d (%.1f%% of %d trades) | G gaps at activation %3d | U unarmed at activation %5d (%.0f%%) | same-bar trades %4d | BE/SALV exits %4d' % (
            s, p[0], nl, A, 100.0 * A / max(1, len(tr)), len(tr), gap, unarmed, 100.0 * unarmed / max(1, nl), same, bes))
