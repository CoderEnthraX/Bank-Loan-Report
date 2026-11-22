"""Per-bar context features for the Sniper research (no look-ahead: every value is known at the chart bar's close).
X columns (one matrix per timeframe, cache feat_<tf>.npz):
  ema50_tf     close vs EMA50 of the chart (sign x distance in ATR)        ema200_tf    the same with EMA200
  h1_ema50     last closed H1 bar: close vs its EMA50 (sign: +1 / -1)    h4_ema50     the same on H4        d1_ema20  D1 close vs EMA20
  h1_slope     slope of the H1 EMA50 over 5 H1 bars (ATR units, signed)
  pdc_side     close vs the previous server day's close (ATR)             pdhl_pos     position in the previous day's range (0 = low, 1 = high)
  wvwap_side   close vs the weekly VWAP (ATR)                             atr_reg      ATR14 / its 200-bar average
  vwap_slope20 VWAP change over 20 bars (ATR)                             cvd_s20      sum of the delta of the last 20 bars / their volume
  poc_dist     close - developing session POC (ATR)                       va_pos       position vs the developing value area (-1 below VAL, 0 inside, +1 above VAH)
  ppoc_dist    close - the previous session's POC (ATR)                   sweep_lo / sweep_hi   a bar of the last 10 took out the prior 20-bar low / high (1 / 0)
  stack_up / stack_dn  longest run of up / down intrabars in the bar      upfrac / dnfrac  share of the bar's intrabar volume that is buying / selling
  hour_ist     IST hour of the bar's close                                dow          day of the week (0 Monday)
  spread       mean M1 spread of the bar (price)                          rn_dist      distance to the nearest $10 level (ATR)
Run: python3 -I features.py"""
import sys, numpy as np, numba as nb
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/snr')
import data as D

COLS = ['ema50_tf', 'ema200_tf', 'h1_ema50', 'h4_ema50', 'd1_ema20', 'h1_slope', 'pdc_side', 'pdhl_pos', 'wvwap_side', 'atr_reg', 'vwap_slope20',
        'cvd_s20', 'poc_dist', 'va_pos', 'ppoc_dist', 'sweep_lo', 'sweep_hi', 'stack_up', 'stack_dn', 'upfrac', 'dnfrac', 'hour_ist', 'dow', 'spread', 'rn_dist']
CI = {k: i for i, k in enumerate(COLS)}


def ema(x, n):
    a = 2.0 / (n + 1); out = np.empty(len(x)); e = x[0]
    for i in range(len(x)):
        e = a * x[i] + (1 - a) * e if i else x[0]; out[i] = e
    return out


ema = nb.njit(cache=True)(ema)


@nb.njit(cache=True)
def atr14(h, l, c):
    n = len(c); out = np.full(n, np.nan); s = 0.0; a = 0.0
    for i in range(n):
        tr = h[i] - l[i] if i == 0 else max(max(h[i] - l[i], abs(h[i] - c[i - 1])), abs(l[i] - c[i - 1]))
        if i < 14:
            s += tr
            if i == 13:
                a = s / 14; out[i] = a
        else:
            a = tr / 14 + (1 - 1.0 / 14) * a; out[i] = a
    return out


@nb.njit(cache=True)
def profile(srv1, h1, l1, v1, bar_end_j, binw):
    """developing session POC / VAH / VAL at each chart bar end (M1 index bar_end_j), and the previous session's final POC;
    a minute's volume is spread evenly over the $binw bins of its range"""
    nbar = len(bar_end_j); poc = np.full(nbar, np.nan); vah = np.full(nbar, np.nan); val = np.full(nbar, np.nan); ppoc = np.full(nbar, np.nan)
    NB = 4000
    hist = np.zeros(NB); base = 0.0; day = -1; prev_poc = np.nan; cur_poc = np.nan
    j = 0; tot = 0.0
    for b in range(nbar):
        jend = bar_end_j[b]
        while j <= jend:
            dk = srv1[j] // 86400
            if dk != day:
                if day != -1:
                    prev_poc = cur_poc
                day = dk; hist[:] = 0.0; base = l1[j] - (NB // 2) * binw; tot = 0.0
            lo = int((l1[j] - base) / binw); hi = int((h1[j] - base) / binw)
            if lo < 0:
                lo = 0
            if hi >= NB:
                hi = NB - 1
            if hi < lo:
                hi = lo
            w = v1[j] / (hi - lo + 1)
            for q in range(lo, hi + 1):
                hist[q] += w
            tot += v1[j]
            j += 1
        # POC and the 70% value area
        k = 0; mx = -1.0
        for q in range(NB):
            if hist[q] > mx:
                mx = hist[q]; k = q
        cur_poc = base + (k + 0.5) * binw
        a = k; z = k; acc = hist[k]
        while acc < 0.7 * tot and (a > 0 or z < NB - 1):
            up = hist[z + 1] if z < NB - 1 else -1.0
            dn = hist[a - 1] if a > 0 else -1.0
            if up >= dn:
                z += 1; acc += up
            else:
                a -= 1; acc += dn
        poc[b] = cur_poc; vah[b] = base + (z + 1) * binw; val[b] = base + a * binw; ppoc[b] = prev_poc
    return poc, vah, val, ppoc


@nb.njit(cache=True)
def stacks(o1, c1, j0, j1, bv, sv):
    n = len(j0); su = np.zeros(n); sd = np.zeros(n); uf = np.full(n, np.nan); df = np.full(n, np.nan)
    for b in range(n):
        ru = 0; rd = 0; mu = 0; md = 0; tb = 0.0; ts = 0.0
        for j in range(j0[b], j1[b] + 1):
            if c1[j] > o1[j]:
                ru += 1; rd = 0
            elif c1[j] < o1[j]:
                rd += 1; ru = 0
            else:
                ru = 0; rd = 0
            mu = max(mu, ru); md = max(md, rd); tb += bv[j]; ts += sv[j]
        su[b] = mu; sd[b] = md
        if tb + ts > 0:
            uf[b] = tb / (tb + ts); df[b] = ts / (tb + ts)
    return su, sd, uf, df


def htf_side(b, M, htf, n_ema, srv1, o1, h1, l1, c1, v1):
    """close vs EMA(n) of the last CLOSED htf bar at each chart bar's close; and the EMA slope over 5 htf bars (ATR of htf)"""
    hb = D.bars_from(srv1, o1, h1, l1, c1, v1, htf)
    e = ema(hb['c'], n_ema); at = atr14(hb['h'], hb['l'], hb['c'])
    close_t = b['t'] + (b['t'][1] - b['t'][0] if False else 0)
    tclose = b['t'] + TFMIN[0] * 60
    hend = hb['t'] + htf * 60
    k = np.searchsorted(hend, tclose, side='right') - 1    # last htf bar ended by the chart bar's close
    side = np.where(k >= 0, np.sign(hb['c'][np.maximum(k, 0)] - e[np.maximum(k, 0)]), np.nan)
    k5 = np.maximum(k - 5, 0)
    slope = np.where(k >= 5, (e[np.maximum(k, 0)] - e[k5]) / at[np.maximum(k, 0)], np.nan)
    return side, slope


TFMIN = [5]


def build(tf):
    TFMIN[0] = tf
    b = dict(np.load(S + '/snr/cache_%d.npz' % tf)); M = dict(np.load(S + '/snr/m1.npz'))
    srv1, o1, h1, l1, c1, v1 = M['srv'], M['o'], M['h'], M['l'], M['c'], M['v']
    n = len(b['c']); X = np.full((n, len(COLS)), np.nan)
    c, h, l = b['c'], b['h'], b['l']
    at = atr14(h, l, c)
    X[:, CI['ema50_tf']] = (c - ema(c, 50)) / at
    X[:, CI['ema200_tf']] = (c - ema(c, 200)) / at
    X[:, CI['h1_ema50']], X[:, CI['h1_slope']] = htf_side(b, M, 60, 50, srv1, o1, h1, l1, c1, v1)
    X[:, CI['h4_ema50']], _ = htf_side(b, M, 240, 50, srv1, o1, h1, l1, c1, v1)
    X[:, CI['d1_ema20']], _ = htf_side(b, M, 1440, 20, srv1, o1, h1, l1, c1, v1)
    # previous server day
    day = b['t'] // 86400
    ud, first = np.unique(day, return_index=True)
    last = np.r_[first[1:], n] - 1
    dclose = c[last]; dhigh = np.maximum.reduceat(h, first); dlow = np.minimum.reduceat(l, first)
    di = np.searchsorted(ud, day)
    pc = np.where(di > 0, dclose[np.maximum(di - 1, 0)], np.nan); ph = np.where(di > 0, dhigh[np.maximum(di - 1, 0)], np.nan); pl = np.where(di > 0, dlow[np.maximum(di - 1, 0)], np.nan)
    X[:, CI['pdc_side']] = (c - pc) / at
    X[:, CI['pdhl_pos']] = (c - pl) / np.where(ph - pl > 0, ph - pl, np.nan)
    # weekly VWAP (weeks from Monday 00:00 server)
    wk = (b['t'] + 3 * 86400) // (7 * 86400)
    src = (h + l + c) / 3.0; w = np.where(b['v'] > 0, b['v'], 1.0)
    pv = np.zeros(n); ww = np.zeros(n)
    st = D.group(wk)
    for a, z in zip(st, np.r_[st[1:], n]):
        pv[a:z] = np.cumsum(src[a:z] * w[a:z]); ww[a:z] = np.cumsum(w[a:z])
    X[:, CI['wvwap_side']] = (c - pv / ww) / at
    atm = np.convolve(at, np.ones(200) / 200, mode='full')[:n]
    atm[:199] = np.nan
    X[:, CI['atr_reg']] = at / atm
    vw = b['vwap']
    X[20:, CI['vwap_slope20']] = (vw[20:] - vw[:-20]) / at[20:]
    # delta (intrabar, else the candle estimate), 20-bar sum / volume
    rng = h - l
    est_b = np.where(rng > 0, b['v'] * (c - l) / np.where(rng > 0, rng, 1), b['v'] * 0.5)
    intra = b['icnt'] >= 2
    bv = np.where(intra, b['ibv'], est_b); sv = np.where(intra, b['isv'], b['v'] - est_b)
    dl = bv - sv; tv = bv + sv
    cd = np.cumsum(dl); ct = np.cumsum(tv)
    s20 = np.full(n, np.nan); s20[20:] = (cd[20:] - cd[:-20]) / np.maximum(ct[20:] - ct[:-20], 1e-9)
    X[:, CI['cvd_s20']] = s20
    poc, vah, val, ppoc = profile(srv1, h1, l1, v1, b['j1'], 0.5)
    X[:, CI['poc_dist']] = (c - poc) / at
    X[:, CI['va_pos']] = np.where(c > vah, 1.0, np.where(c < val, -1.0, 0.0))
    X[:, CI['ppoc_dist']] = (c - ppoc) / at
    lo20 = np.full(n, np.nan); hi20 = np.full(n, np.nan)
    for i in range(21, n):
        pass
    from numpy.lib.stride_tricks import sliding_window_view as swv
    mn = swv(l, 20).min(axis=1); mx = swv(h, 20).max(axis=1)      # window ending at i (incl.)
    prevmin = np.full(n, np.nan); prevmax = np.full(n, np.nan)
    prevmin[20:] = mn[:-1]; prevmax[20:] = mx[:-1]                    # the 20 bars before i
    swl = (l < prevmin).astype(float); swh = (h > prevmax).astype(float)
    X[:, CI['sweep_lo']] = np.r_[np.zeros(9), swv(swl, 10).max(axis=1)]
    X[:, CI['sweep_hi']] = np.r_[np.zeros(9), swv(swh, 10).max(axis=1)]
    # intrabar stacks (M1 candles inside the bar; H2 / H3 also from M1 here)
    pc1 = np.r_[c1[0], c1[:-1]]
    dr = np.where(c1 > o1, 1.0, np.where(c1 < o1, -1.0, np.sign(c1 - pc1)))
    bv1 = np.where(dr > 0, v1, np.where(dr < 0, 0.0, v1 * 0.5)); sv1 = np.where(dr < 0, v1, np.where(dr > 0, 0.0, v1 * 0.5))
    su, sdn, uf, df = stacks(o1, c1, b['j0'], b['j1'], bv1, sv1)
    X[:, CI['stack_up']] = su; X[:, CI['stack_dn']] = sdn; X[:, CI['upfrac']] = uf; X[:, CI['dnfrac']] = df
    ist = b['ue'] + 19800
    X[:, CI['hour_ist']] = (ist % 86400) // 3600
    X[:, CI['dow']] = ((b['ue'] // 86400) + 3) % 7          # 1970-01-01 was a Thursday -> Monday = 0
    sp = dict(np.load(S + '/entry/cache_M1.npz'))['SP']
    X[:, CI['spread']] = np.add.reduceat(sp, b['j0']) / (b['j1'] - b['j0'] + 1)
    X[:, CI['rn_dist']] = np.abs(c - np.round(c / 10.0) * 10.0) / at
    np.savez(S + '/snr/feat_%d.npz' % tf, X=X, cols=np.array(COLS))
    print('tf %d: %d bars x %d features, nan share %.3f' % (tf, n, len(COLS), np.isnan(X).mean()), flush=True)


if __name__ == '__main__':
    for tf in (5, 15, 60, 120, 180):
        build(tf)
