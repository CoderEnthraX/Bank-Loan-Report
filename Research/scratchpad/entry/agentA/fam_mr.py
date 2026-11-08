"""family 5: mean reversion after runs / big z, inside bar & NR7 breakouts, daily / weekly reopen gaps, round numbers"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, pandas as pd
FAM = 'mr'
def runlen(x):
    out = np.zeros(len(x), np.int64); c = 0
    for k in range(len(x)):
        c = c + 1 if x[k] else 0; out[k] = c
    return out
for tf in sys.argv[1].split(','):
    b = lib.ctx(tf); H, L, C, O, A, V, SD = b['H'], b['L'], b['C'], b['O'], b['atr'], b['V'], b['SD']; nm = b['ny_min']
    ok = b['ok'] & (b['ny_wd'] < 5); per_h = 60 // b['tfmin']
    up = runlen(C > O); dn = runlen(C < O)
    for N in ((5, 7) if tf == 'M5' else (4, 6)):
        il = np.flatnonzero(ok & (dn == N)); is_ = np.flatnonzero(ok & (up == N))
        i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
        lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name='%d bars one way -> fade 1.8ATR' % N, family=FAM)
        lib.run(tf, i, -d, c, c + d * 1.8 * a, 1, name='%d bars one way -> continue 1.8ATR' % N, family=FAM)
    z = (C - V) / np.where(SD > 0, SD, np.nan); sd_ok = (SD > 0.5 * A) & (b['vb'] >= 2 * per_h)
    zz = z * SD / A  # distance from VWAP in ATR
    for k in (4.0, 6.0):
        dist = (C - V) / A; pd_ = np.r_[0, dist[:-1]]
        il = lib.decluster(np.flatnonzero(ok & (dist < -k) & (pd_ >= -k)), per_h); is_ = lib.decluster(np.flatnonzero(ok & (dist > k) & (pd_ <= k)), per_h)
        i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
        lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name='|C-VWAP|>%.0fATR fade 1.8ATR' % k, family=FAM)
        lib.run(tf, i, d, c, c - d * 3 * a, 1, name='|C-VWAP|>%.0fATR fade 3ATR' % k, family=FAM)
    for k in (3.0,):
        pz = np.r_[0, z[:-1]]
        il = lib.decluster(np.flatnonzero(ok & sd_ok & (z < -k) & (pz >= -k)), per_h); is_ = lib.decluster(np.flatnonzero(ok & sd_ok & (z > k) & (pz <= k)), per_h)
        i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
        lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name='z>3sig fade 1.8ATR', family=FAM)
    # inside bar / NR7 breakout (both stop orders, 3 bars)
    rng = H - L
    nr7 = rng <= pd.Series(rng).rolling(7).min().to_numpy()
    ins = (H < np.r_[np.inf, H[:-1]]) & (L > np.r_[-np.inf, L[:-1]])
    for lab, cond in (('NR7', nr7), ('inside bar', ins), ('NR7+inside', nr7 & ins)):
        i = np.flatnonzero(ok & cond); a = A[i]
        i2 = np.r_[i, i]; d2 = np.r_[np.ones(len(i)), -np.ones(len(i))].astype(int); a2 = np.r_[a, a]
        e = np.r_[H[i] + 0.05 * a, L[i] - 0.05 * a]; oth = np.r_[L[i] - 0.05 * a, H[i] + 0.05 * a]
        st = np.where(d2 == 1, np.minimum(oth, e - 0.5 * a2), np.maximum(oth, e + 0.5 * a2))
        lib.run(tf, i2, d2, e, st, 2, window=3, name='%s breakout stop=other side' % lab, family=FAM)
        lib.run(tf, i2, d2, e, e - d2 * 1.8 * a2, 2, window=3, name='%s breakout 1.8ATR' % lab, family=FAM)
    # reopen gaps: first bar of the server session (after the daily break) vs previous close
    first = b['ds'] & b['ok']
    i0 = np.flatnonzero(first); gap = (O[i0] - C[i0 - 1]) / A[i0]
    for wk, lab in ((False, 'daily'), (True, 'weekly')):
        isw = (b['utc'][i0] - b['utc'][i0 - 1]) > 86400
        sel = (isw if wk else ~isw) & (np.abs(gap) > 0.5)
        i = i0[sel]; g = np.sign(gap[sel]).astype(int); c = C[i]; a = A[i]
        lib.run(tf, i, -g, c, c + g * 1.8 * a, 1, name='%s reopen gap>0.5ATR fade 1.8ATR' % lab, family=FAM)
        lib.run(tf, i, g, c, c - g * 1.8 * a, 1, name='%s reopen gap>0.5ATR continue 1.8ATR' % lab, family=FAM)
    # round numbers: bar trades through a $10/$50 level and closes back on its original side (reject) / beyond (break)
    for step in (10.0, 50.0):
        pc = np.r_[C[0], C[:-1]]
        lev_up = (np.floor(pc / step) + 1) * step; lev_dn = np.floor(pc / step) * step
        rejS = ok & (H >= lev_up) & (C < lev_up); rejL = ok & (L <= lev_dn) & (C > lev_dn)
        brkL = ok & (C > lev_up); brkS = ok & (C < lev_dn)
        for lab, Lm, Sm in (('reject', rejL, rejS), ('break', brkL, brkS)):
            il = lib.decluster(np.flatnonzero(Lm), per_h); is_ = lib.decluster(np.flatnonzero(Sm), per_h)
            i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
            lib.run(tf, i, d, c, c - d * 1.8 * a, 1, name='round $%d %s 1.8ATR' % (step, lab), family=FAM)
