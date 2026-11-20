"""Order block + absorption + aggression test on gold, 2026 (asked 2026-11-20). All bars are built from the M1 bars (server-time buckets).
Order block (HTF, bullish; bearish is the mirror): a down candle i (C < O) followed by a bullish fair value gap made by candles (k-2, k) with
i <= k-2 and k <= i+3 (L[k] > H[k-2]) and C[k] > H[i]; usable from the CLOSE of candle k; zone = [L[i], H[i]]; dead when an LTF candle closes
below L[i]; traded once (its first episode: from the first LTF touch, at most 30 LTF candles).
LTF absorption: a candle that overlaps the zone, volume > mean of the 20 previous candles, body < 40% of its range, the wick into the zone
>= 50% of its range (bullish: lower wick). Aggression: a LATER candle in the episode, C > O and body >= 55% of its range -> buy at its close.
Stops: 'candle' = aggression low - 0.01; 'swing' = the latest confirmed swing low (pivot, 2 bars each side, confirmed before the aggression
candle) below the entry - 0.01. Outcome on M1 from the next minute: the best price reached before the stop (a minute touching the stop
counts as the stop) -> reached 0.1 ... 3R; net R if exiting there, costs 0.23 per oz (spread 0.16 + $7 a lot): win (X r - 0.23) / (r + 0.23),
loss -1. Filters: kill zones Asia 05:30-09:30, London 11:30-14:30 (UK winter +1h), New York 16:30-19:30 (US winter +1h) IST, hours 06:00-
23:00 IST, news 17:45 IST (New York time) + 30 min and 30 min before: no entry. Run: python3 -I ob_test.py -> ob_results.pkl"""
import sys, pickle, datetime as dt, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/bese')
from ref_gbe import ny_summer
LEVELS = (0.1, 0.2, 0.3, 0.5, 0.6, 1.0, 1.5, 2.0, 3.0)
COST = 0.23
PAIRS = [('M1', 'M3'), ('M1', 'M5'), ('M5', 'M15'), ('M5', 'M30'), ('M5', 'H1'), ('M15', 'H1'), ('M15', 'H4')]
MIN = {'M1': 1, 'M3': 3, 'M5': 5, 'M15': 15, 'M30': 30, 'H1': 60, 'H4': 240}
START = dt.datetime(2025, 11, 15); TEST0 = dt.datetime(2026, 1, 1)

d = pickle.load(open(S + '/gold/data/M1.pkl', 'rb'))
i0 = next(i for i, t in enumerate(d['srv']) if t >= START)
SRV = d['srv'][i0:]; UTC = d['utc'][i0:]; O1, H1, L1, C1, V1 = (d[k][i0:] for k in ('O', 'H', 'L', 'C', 'TV'))
IST = [u + dt.timedelta(hours=5, minutes=30) for u in UTC]; N1 = len(O1)


def bars(tf):
    m = MIN[tf]; out = dict(o=[], h=[], l=[], c=[], v=[], t0=[], t1=[], j0=[], j1=[])
    key = None; g0 = 0
    def flush(a, b):
        out['o'].append(O1[a]); out['h'].append(max(H1[a:b + 1])); out['l'].append(min(L1[a:b + 1])); out['c'].append(C1[b]); out['v'].append(sum(V1[a:b + 1]))
        out['t0'].append(IST[a]); out['t1'].append(IST[b] + dt.timedelta(minutes=1)); out['j0'].append(a); out['j1'].append(b)
    for j, t in enumerate(SRV):
        k = (t.date(), (t.hour * 60 + t.minute) // m)
        if key is None: key = k; g0 = j
        elif k != key: flush(g0, j - 1); key = k; g0 = j
    flush(g0, N1 - 1)
    return out


def uk_summer(u):
    def last_sun(y, mo):
        x = dt.datetime(y, mo + 1, 1) - dt.timedelta(days=1) if mo < 12 else dt.datetime(y, 12, 31)
        return x - dt.timedelta(days=(x.weekday() + 1) % 7)
    return last_sun(u.year, 3).replace(hour=1) <= u < last_sun(u.year, 10).replace(hour=1)


def mins(t): return t.hour * 60 + t.minute


def filt_ok(t):
    """t = the entry time (IST): in a kill zone, 06:00-23:00 IST, not in the news block"""
    u = t - dt.timedelta(hours=5, minutes=30); m = mins(t)
    if not (360 <= m < 1380): return False
    lon = 0 if uk_summer(u) else 60; ny = 0 if ny_summer(u) else 60
    kz = (330 <= m < 570) or (690 + lon <= m < 870 + lon) or (990 + ny <= m < 1170 + ny)
    if not kz: return False
    s0 = (17 * 60 + 45 + ny) % 1440; diff = (s0 - m) % 1440
    return not ((s0 <= m < s0 + 30) or (0 < diff <= 30))


def obs(H):
    """order blocks of an HTF bar series: (direction, zone lo, zone hi, usable from (IST))"""
    o, h, l, c = H['o'], H['h'], H['l'], H['c']; out = []
    for i in range(len(o) - 3):
        if c[i] < o[i]:
            for k in range(i + 2, i + 4):
                if k < len(o) and l[k] > h[k - 2] and c[k] > h[i]: out.append((1, l[i], h[i], H['t1'][k])); break
        if c[i] > o[i]:
            for k in range(i + 2, i + 4):
                if k < len(o) and h[k] < l[k - 2] and c[k] < l[i]: out.append((-1, l[i], h[i], H['t1'][k])); break
    return out


def outcome(dirn, entry, stop, jstart):
    """best excursion (price) before the stop on M1 from bar jstart; None if neither stop nor 3R within the data"""
    r = abs(entry - stop); best = 0.0; top = 3.0 * r
    for j in range(jstart, N1):
        if dirn == 1:
            if L1[j] <= stop: return best / r, True
            best = max(best, H1[j] - entry)
        else:
            if H1[j] >= stop: return best / r, True
            best = max(best, entry - L1[j])
        if best >= top: return best / r, False
    return best / r, None


def run():
    B = {tf: bars(tf) for tf in set(MIN)}
    res = []
    for ltf, htf in PAIRS:
        L = B[ltf]; ob = obs(B[htf]); n = len(L['o'])
        # LTF index by time
        import bisect
        t0s = L['t0']
        piv_lo = [i for i in range(2, n - 2) if L['l'][i] <= min(L['l'][i - 2:i + 3])]
        piv_hi = [i for i in range(2, n - 2) if L['h'][i] >= max(L['h'][i - 2:i + 3])]
        seen = set()
        for dirn, lo, hi, tu in ob:
            a = bisect.bisect_left(t0s, tu)                      # the first LTF candle that opens after the OB is usable
            touch = None
            for i in range(a, n):
                if L['t0'][i] - tu > dt.timedelta(days=20): break
                if (dirn == 1 and L['c'][i] < lo) or (dirn == -1 and L['c'][i] > hi): break   # dead before a touch
                if L['l'][i] <= hi and L['h'][i] >= lo: touch = i; break
            if touch is None: continue
            absorbed = False; sig = None
            for i in range(touch, min(n, touch + 30)):
                if (dirn == 1 and L['c'][i] < lo) or (dirn == -1 and L['c'][i] > hi): break     # the OB is broken
                rng = L['h'][i] - L['l'][i]
                if rng <= 0: continue
                body = abs(L['c'][i] - L['o'][i])
                if absorbed and ((dirn == 1 and L['c'][i] > L['o'][i]) or (dirn == -1 and L['c'][i] < L['o'][i])) and body >= 0.55 * rng:
                    sig = i; break
                if i >= 20 and L['l'][i] <= hi and L['h'][i] >= lo:
                    vavg = sum(L['v'][i - 20:i]) / 20.0
                    wick = (min(L['o'][i], L['c'][i]) - L['l'][i]) if dirn == 1 else (L['h'][i] - max(L['o'][i], L['c'][i]))
                    if L['v'][i] > vavg and body < 0.40 * rng and wick >= 0.50 * rng: absorbed = True
            if sig is None or L['t1'][sig] < TEST0: continue
            if (sig, dirn) in seen: continue
            seen.add((sig, dirn))
            entry = L['c'][sig]; tE = L['t1'][sig]; jn = L['j1'][sig] + 1
            if jn >= N1: continue
            stops = {'candle': (L['l'][sig] - 0.01) if dirn == 1 else (L['h'][sig] + 0.01)}
            pv = [p for p in (piv_lo if dirn == 1 else piv_hi) if p <= sig - 2]
            sw = None
            for p in reversed(pv[-200:]):
                v = L['l'][p] if dirn == 1 else L['h'][p]
                if (dirn == 1 and v < entry) or (dirn == -1 and v > entry): sw = v; break
            if sw is not None: stops['swing'] = (sw - 0.01) if dirn == 1 else (sw + 0.01)
            for sn, stp in stops.items():
                r = abs(entry - stp)
                if r < 0.05: continue
                mfe, stopped = outcome(dirn, entry, stp, jn)
                if stopped is None and mfe < 3.0: continue
                res.append(dict(ltf=ltf, htf=htf, stop=sn, dir=dirn, t=tE, entry=entry, risk=r, mfe=mfe, stopped=stopped, filt=filt_ok(tE)))
        print(ltf, htf, 'order blocks', len(ob), 'trades', sum(1 for x in res if x['ltf'] == ltf and x['htf'] == htf), flush=True)
    return res


if __name__ == '__main__':
    R = run()
    pickle.dump(R, open(S + '/ob/ob_results.pkl', 'wb'))
    print('saved', len(R))
