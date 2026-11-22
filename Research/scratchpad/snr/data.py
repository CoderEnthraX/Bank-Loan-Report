"""Sniper research data: chart bars of each timeframe built from the FxPro gold M1 bars (server-time buckets, like the EA / simulator), the
intrabar buy / sell volume (M1 candles for charts up to H1, M5 candles for H2 / H3, like the Pine auto lower timeframe), the strategy's VWAP
(server-day session, typical price, tick-volume weights: the EA's ProcessBar) and the user's filters (kill zones, 06:00-23:00 IST, news).
Run: python3 -I data.py  -> cache_<tf>.npz (tf = 5, 15, 60, 120, 180 minutes) + m1.npz"""
import os, sys, datetime as dt, numpy as np, numba as nb
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
HERE = S + '/snr'
TFS = (5, 15, 60, 120, 180)


def nth_sunday(y, m, n):
    d = dt.date(y, m, 1); first = d + dt.timedelta(days=(6 - d.weekday()) % 7)
    return (first + dt.timedelta(days=7 * (n - 1))).day


def last_sunday(y, m):
    x = (dt.date(y, m + 1, 1) - dt.timedelta(days=1)) if m < 12 else dt.date(y, 12, 31)
    return x - dt.timedelta(days=(x.weekday() + 1) % 7)


def dst_flags(utc):
    """uk summer, ny summer for each UTC second (vectorised through the year boundaries)"""
    years = range(2020, 2028)
    uk = np.zeros(len(utc), bool); ny = np.zeros(len(utc), bool)
    for y in years:
        a = int(dt.datetime.combine(last_sunday(y, 3), dt.time(1)).replace(tzinfo=dt.timezone.utc).timestamp())
        b = int(dt.datetime.combine(last_sunday(y, 10), dt.time(1)).replace(tzinfo=dt.timezone.utc).timestamp())
        uk |= (utc >= a) & (utc < b)
        a = int(dt.datetime(y, 3, nth_sunday(y, 3, 2), 7, tzinfo=dt.timezone.utc).timestamp())
        b = int(dt.datetime(y, 11, nth_sunday(y, 11, 1), 6, tzinfo=dt.timezone.utc).timestamp())
        ny |= (utc >= a) & (utc < b)
    return uk, ny


def filt_flags(utc_entry):
    """ob_test.filt_ok for each entry time (UTC seconds): hours 06:00-23:00 IST, in a kill zone, not in the news block"""
    uk, ny = dst_flags(utc_entry)
    m = ((utc_entry + 19800) % 86400) // 60
    hours = (m >= 360) & (m < 1380)
    lon = np.where(uk, 0, 60); nys = np.where(ny, 0, 60)
    kz = ((m >= 330) & (m < 570)) | ((m >= 690 + lon) & (m < 870 + lon)) | ((m >= 990 + nys) & (m < 1170 + nys))
    s0 = (17 * 60 + 45 + nys) % 1440; diff = (s0 - m) % 1440
    news = ((m >= s0) & (m < s0 + 30)) | ((diff > 0) & (diff <= 30))
    return hours & kz & ~news, hours, kz, news


def group(key):
    """start index of each run of equal keys"""
    st = np.r_[0, np.nonzero(np.diff(key))[0] + 1]
    return st


def bars_from(srv, O, H, L, C, V, tf):
    key = srv // (tf * 60); st = group(key); en = np.r_[st[1:], len(srv)] - 1
    return dict(t=key[st] * tf * 60, o=O[st], h=np.maximum.reduceat(H, st), l=np.minimum.reduceat(L, st), c=C[en], v=np.add.reduceat(V, st), j0=st, j1=en)


def split(O, C, V):
    """up candle = buying volume, down = selling, unchanged = by the previous close (half each when equal too)"""
    pc = np.r_[C[0], C[:-1]]
    dr = np.where(C > O, 1.0, np.where(C < O, -1.0, np.sign(C - pc)))
    bv = np.where(dr > 0, V, np.where(dr < 0, 0.0, V * 0.5)); sv = np.where(dr < 0, V, np.where(dr > 0, 0.0, V * 0.5))
    return bv, sv


@nb.njit(cache=True)
def vwap_k(t, o, h, l, c, v):
    n = len(c); vw = np.empty(n); sd = np.empty(n); na = np.zeros(n, np.bool_)
    cumPV = 0.0; cumPV2 = 0.0; cumW = 0.0; cumP = 0.0; cumP2 = 0.0; cumN = 0; last = -1
    for i in range(n):
        w = v[i] if v[i] > 0 else 1.0
        src = (h[i] + l[i] + c[i]) / 3.0
        key = t[i] // 86400
        if last == -1 or key != last:
            na[i] = True; cumPV = 0.0; cumPV2 = 0.0; cumW = 0.0; cumP = 0.0; cumP2 = 0.0; cumN = 0
        last = key
        cumPV += src * w; cumPV2 += src * src * w; cumW += w; cumP += src; cumP2 += src * src; cumN += 1
        vwap = cumPV / cumW if cumW > 0 else cumP / cumN
        var = cumPV2 / cumW - vwap * vwap if cumW > 0 else cumP2 / cumN - vwap * vwap
        vw[i] = vwap; sd[i] = np.sqrt(max(var, 0.0))
    return vw, sd, na


def main():
    d = dict(np.load(S + '/entry/cache_M1.npz'))
    srv, utc, O, H, L, C, V = d['srv'], d['utc'], d['O'], d['H'], d['L'], d['C'], d['TV'].astype(float)
    np.savez(HERE + '/m1.npz', srv=srv, utc=utc, o=O, h=H, l=L, c=C, v=V)
    bv1, sv1 = split(O, C, V)
    m5 = bars_from(srv, O, H, L, C, V, 5)
    bv5, sv5 = split(m5['o'], m5['c'], m5['v'])
    for tf in TFS:
        b = bars_from(srv, O, H, L, C, V, tf)
        if tf <= 60:
            ib, isv = np.add.reduceat(bv1, b['j0']), np.add.reduceat(sv1, b['j0']); cnt = b['j1'] - b['j0'] + 1
        else:
            k5 = m5['t'] // (tf * 60); st5 = group(k5)
            assert np.array_equal(k5[st5] * tf * 60, b['t'])
            ib, isv = np.add.reduceat(bv5, st5), np.add.reduceat(sv5, st5); cnt = np.diff(np.r_[st5, len(k5)])
        vw, sd, na = vwap_k(b['t'], b['o'], b['h'], b['l'], b['c'], b['v'])
        ue = utc[b['j1']] + 60                     # the entry time: the bar's close (UTC)
        f, hours, kz, news = filt_flags(ue)
        np.savez(HERE + '/cache_%d.npz' % tf, ibv=ib, isv=isv, icnt=cnt, vwap=vw, vwsd=sd, newa=na, utc0=utc[b['j0']], ue=ue,
                 filt=f, hours=hours, kz=kz, news=news, **b)
        print('tf %3d: %7d bars, intrabars %s, filters pass %.1f%%' % (tf, len(b['t']), 'M1' if tf <= 60 else 'M5', 100 * f.mean()), flush=True)


if __name__ == '__main__':
    main()
