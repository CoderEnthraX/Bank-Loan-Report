"""family 4: 08:30 / 10:00 NY data bars (continuation / fade / break), intraday momentum (first 30 / 60 min), late-session drift"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, pandas as pd
FAM = 'time'
for tf in sys.argv[1].split(','):
    b = lib.ctx(tf); H, L, C, O, A = b['H'], b['L'], b['C'], b['O'], b['atr']; nm = b['ny_min']; wd = b['ny_wd'] < 5; ok = b['ok'] & wd
    Ap = np.r_[np.nan, A[:-1]]
    for t0, tn in ((8 * 60 + 30, '0830'), (10 * 60, '1000')):
        first = ok & (nm == t0)
        rng = (H - L) / Ap
        for k in (1.5, 2.5):
            i = np.flatnonzero(first & (rng > k)); sgn = np.sign(C[i] - O[i]).astype(int); m = sgn != 0; i = i[m]; sgn = sgn[m]
            c = C[i]; a = A[i]
            lib.run(tf, i, sgn, c, c - sgn * 1.8 * a, 1, name='%s bar >%.1fATR continue 1.8ATR' % (tn, k), family=FAM)
            st = np.where(sgn == 1, np.minimum((H[i] + L[i]) / 2, c - 0.5 * a), np.maximum((H[i] + L[i]) / 2, c + 0.5 * a))
            lib.run(tf, i, sgn, c, st, 1, name='%s bar >%.1fATR continue stop=mid' % (tn, k), family=FAM)
            lib.run(tf, i, -sgn, c, c + sgn * 1.8 * a, 1, name='%s bar >%.1fATR fade 1.8ATR' % (tn, k), family=FAM)
            ext = np.where(sgn == 1, H[i], L[i])
            st = np.where(-sgn == 1, np.minimum(ext - 0.1 * a, c - 0.5 * a) * 0 + np.minimum(L[i] - 0.1 * a, c - 0.5 * a), np.maximum(H[i] + 0.1 * a, c + 0.5 * a))
            lib.run(tf, i, -sgn, c, st, 1, name='%s bar >%.1fATR fade stop=ext' % (tn, k), family=FAM)
        # break of the data bar's high / low (both stop orders, 2 hours)
        i = np.flatnonzero(first & (rng > 1.5)); a = A[i]
        i2 = np.r_[i, i]; d2 = np.r_[np.ones(len(i)), -np.ones(len(i))].astype(int); a2 = np.r_[a, a]
        e = np.r_[H[i] + 0.05 * a, L[i] - 0.05 * a]
        lib.run(tf, i2, d2, e, e - d2 * 1.8 * a2, 2, window=120 // b['tfmin'], name='%s bar>1.5 break hi/lo stopentry 1.8ATR' % tn, family=FAM)
    # intraday momentum: return over a window -> trade in its sign at the window's end
    for (a0, a1, lab) in ((9 * 60 + 30, 10 * 60, 'NY 09:30-10:00'), (8 * 60 + 20, 9 * 60 + 20, 'COMEX 08:20-09:20'), (3 * 60, 4 * 60, 'London 1st hour'),
                         (18 * 60, 15 * 60, 'session to 15:00'), (18 * 60, 12 * 60, 'session to 12:00')):
        o_i = lib.first_per_day(b, ok & (nm == a0))
        e_i = lib.first_per_day(b, ok & (nm == a1 - b['tfmin'] if a1 > a0 else ok & (nm == a1 - b['tfmin'])))
        so = pd.Series(O[o_i], index=b['tday'][o_i]); se = pd.Series(e_i, index=b['tday'][e_i])
        j = pd.concat([so.rename('o'), se.rename('e')], axis=1).dropna()
        ei = j['e'].to_numpy().astype(int); r = (C[ei] - j['o'].to_numpy()) / A[ei]
        for th in (0.0, 2.0):
            m = np.abs(r) > th; i = ei[m]; d = np.sign(r[m]).astype(int); c = C[i]; a = A[i]
            lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name='mom %s |r|>%.0fATR with 1.8ATR' % (lab, th), family=FAM)
            lib.run(tf, i, d, c, c - d * 4 * a, 1, name='mom %s |r|>%.0fATR with 4ATR' % (lab, th), family=FAM)
    # late-session drift (reference: time-of-day only)
    for t, d0, lab in ((14 * 60, 1, 'long 14:00 NY'), (15 * 60, 1, 'long 15:00 NY'), (7 * 60, -1, 'short 07:00 NY')):
        i = lib.first_per_day(b, ok & (nm == t)); d = np.full(len(i), d0); c = C[i]; a = A[i]
        lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name='TOD %s 1.8ATR' % lab, family=FAM)
