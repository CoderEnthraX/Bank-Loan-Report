"""The user's 9 strategies (table, 2026-11-14) on gold 2021-01 .. 2026-10, M1 execution; costs $0.23 per ounce (spread 0.16 + $7 per lot)."""
import sys, time, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
T9 = [  # (fractal TF, right, left, offset %, SL %, TP %, BE %, salvage %)
    ('D1', 3, 25, -0.14, 3.00, 0.75, 0.45, 0.80), ('D1', 3, 15, -0.085, 0.50, 2.00, 0.25, 0.80), ('D1', 2, 7, -0.065, 0.30, 1.65, 0.20, 0.50),
    ('H4', 8, 12, -0.025, 0.44, 3.10, 0.33, 0.90), ('H1', 19, 30, -0.045, 2.00, 0.35, 0.10, 0.70), ('H1', 25, 25, -0.060, 4.20, 0.33, 0.15, 0.80),
    ('H1', 23, 25, -0.055, 0.87, 0.56, 0.13, 1.10), ('H1', 20, 25, -0.060, 0.68, 0.43, 0.10, 0.70), ('H1', 5, 5, -0.080, 2.00, 0.70, 0.10, 1.00)]
if __name__ == '__main__':
    B = EN.load(); ctf = sys.argv[1] if len(sys.argv) > 1 else 'M1'
    t = EN.chart(B, ctf)[0]
    for s, (ftf, r, l, off, sl, tp, be, sv) in enumerate(T9, 1):
        t0 = time.time(); tr = EN.run(B, ctf, ftf, r, l, off, sl, tp, be, sv); st = EN.stats(tr, sl)
        rs = np.bincount(tr[:, 4].astype(int), minlength=5)
        yrs = ' '.join('%d:%+.1f' % (y, EN.stats(tr, sl, t=t, y0=y, y1=y)['R']) for y in range(2021, 2027))
        print('S%d %-3s R%-2d L%-2d | trades %4d win %5.1f%% | sum %+7.2f%% | %+7.1fR avg %+.3fR PF %5.2f | maxDD %5.1fR streak %2d | TP %d SL %d BE %d SALV %d | gaps %d | %s | %.1fs' % (
            s, ftf, r, l, st['n'], st['win'], st['pct'], st['R'], st['avgR'], st['pf'], st['ddR'], st['streak'], rs[1], rs[2], rs[3], rs[4], int(tr[:, 7].sum()) if len(tr) else 0, yrs, time.time() - t0))
