"""Robustness of candidate settings (exact engine): M1 execution with the indicator's path rule, always-low-first and always-high-first
candles, costs 0.23 / 0.40, M5 / M15 chart execution, every year, and random entries with the same exits (same number of entries,
uniform over the M1 bars, 20 seeds). Usage: cand.py 'TF,R,L,off,tp,sl,be,sv' ..."""
import sys, numpy as np, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN, fast as FA
B = EN.load(); t, O, H, L, C = EN.chart(B, 'M1'); BH1, BL1, BH2, BL2 = FA.blocks(H, L)
YR = np.array([dt.datetime.fromtimestamp(int(x), dt.timezone.utc).year for x in t[::1440]])


def yearly(tr, sl, cost, tt):
    out = []
    for y in range(2021, 2027):
        out.append(EN.stats(tr, sl, cost, t=tt, y0=y, y1=y)['R'])
    return out


def rand_base(n_ev, tp, sl, be, sv, cost, seeds=20):
    ups = np.array([tp, be if be > 0 else tp]); dns = np.array([sl, sv if sv > 0 else sl]); bes = np.array([1]); svs = np.array([1])
    Rs = []; Ys = []
    for sd in range(seeds):
        rng = np.random.default_rng(1000 + sd)
        ej = np.sort(rng.choice(len(O) - 2, size=n_ev, replace=False)).astype(np.int64); es = np.zeros(n_ev, np.int64); eF = O[ej].copy()
        KU, XU, KD, XD, KB, XB, KS, XS = FA.passages(O, H, L, C, BH1, BL1, BH2, BL2, ej, es, eF, ups, dns, bes, svs)
        out = np.zeros((n_ev + 1, 4))
        nt = FA.trades_one(ej, es, eF, 0, 0, 0 if be > 0 else -1, 0 if sv > 0 else -1, KU, XU, KD, XD, KB, XB, KS, XS, bes, svs, out)
        e = out[:nt, 0].astype(int); X = out[:nt, 2]; F = eF[e]; R = (X - F - cost) / (F * sl / 100.0)
        Rs.append(R.sum()); yr = YR[ej[e] // 1440]
        Ys.append([R[yr == y].sum() for y in range(2021, 2027)])
    return np.mean(Rs), np.mean(Ys, axis=0), nt


for arg in sys.argv[1:]:
    a = arg.split(','); tf = a[0]; r, l = int(a[1]), int(a[2]); off, tp, sl, be, sv = map(float, a[3:8])
    print('=== %s right %d left %d offset %+.3f | TP %.2f SL %.2f BE %.2f SALV %.2f' % (tf, r, l, off, tp, sl, be, sv))
    for tag, ctf, pm, cost in (('M1 path rule', 'M1', 0, 0.23), ('M1 low first', 'M1', 1, 0.23), ('M1 high first', 'M1', 2, 0.23), ('M1 costs 0.40', 'M1', 0, 0.40),
                               ('chart M5', 'M5', 0, 0.23), ('chart M15', 'M15', 0, 0.23)):
        if EN.TF_SEC[ctf] > EN.TF_SEC[tf]: continue
        tr = EN.run(B, ctf, tf, r, l, off, sl, tp, be, sv, pm); st = EN.stats(tr, sl, cost); tt = EN.chart(B, ctf)[0]
        rs = np.bincount(tr[:, 4].astype(int), minlength=5)
        print('  %-14s trades %4d win %5.1f%% PF %5.2f | %+7.1fR (%+7.2f%%) avg %+.3fR | DD %5.1fR streak %3d | TP %d SL %d BE %d SALV %d | years %s' % (
            tag, st['n'], st['win'], st['pf'], st['R'], st['pct'], st['avgR'], st['ddR'], st['streak'], rs[1], rs[2], rs[3], rs[4], ' '.join('%+.1f' % x for x in yearly(tr, sl, cost, tt))))
    kk = (np.searchsorted(B[tf + '_t'], t, side='right') - 1).astype(np.int64); ph = EN.pivots(B[tf + '_H'], l, r)
    ej, es, eF, eH = FA.events(O, H, L, C, kk, ph, off)
    mR, mY, nt = rand_base(len(ej), tp, sl, be, sv, 0.23)
    print('  random entries (%d entries, 20 seeds, same exits): mean %+7.1fR | years %s' % (len(ej), mR, ' '.join('%+.1f' % x for x in mY)))
