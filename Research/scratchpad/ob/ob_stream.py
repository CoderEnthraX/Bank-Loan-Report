"""Bar-by-bar order block engine (the algorithm the Pine strategy and the EA run), checked against ob_test.py's signals.
Per chart bar: (1) a new bucket opened while the previous HTF candle was not closed -> close it (its order blocks count from this bar);
(2) the zones act on this bar (age, death, touch, episode: break, aggression, absorption); (3) this bar ends its HTF candle -> close it
(its order blocks count from the next bar). HTF candles are built from the chart bars in server time.
Run: python3 -I ob_stream.py  -> compares with ob_results.pkl"""
import sys, os, pickle, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ob_test as T


class OB:
    def __init__(self, ltf_min, htfs, fvgN=3, epi=30, maxDays=20, volN=20, volMult=1.0, absBody=40, absWick=50, aggBody=55, buf=0.01, minRisk=0.05):
        self.ltf = ltf_min; self.htfs = list(htfs); self.N = fvgN; self.epi = epi; self.maxMs = maxDays * 86400
        self.volN = volN; self.volMult = volMult; self.absBody = absBody / 100.0; self.absWick = absWick / 100.0; self.aggBody = aggBody / 100.0
        self.buf = buf; self.minRisk = minRisk
        self.cur = [None] * len(self.htfs)          # [key, o, h, l, c]
        self.done = [[] for _ in self.htfs]        # completed HTF candles (o, h, l, c), last N + 1
        self.zones = []                            # dict(dir, lo, hi, t0 (usable from, seconds), st, tb, ab)
        self.vols = []; self.lows = []; self.highs = []; self.pl = []; self.ph = []; self.n = 0

    def key(self, t, m):  # t = server time (datetime), bucket of m minutes
        return (t.date(), (t.hour * 60 + t.minute) // m)

    def close_htf(self, q, tnow):
        c = self.cur[q]; d = self.done[q]
        d.append(c[1:]); del d[:-(self.N + 1)]
        k = len(d) - 1
        for dirn in (1, -1):
            for i in range(k - self.N, k - 1):          # i = k-N .. k-2: the FVG (k-2, k) and the close beyond the block, at the first k
                if i < 0: continue
                o, h, l, cc = d[i]
                if (dirn == 1 and not cc < o) or (dirn == -1 and not cc > o): continue
                def ok(kk):
                    if dirn == 1: return d[kk][2] > d[kk - 2][1] and d[kk][3] > h
                    return d[kk][1] < d[kk - 2][2] and d[kk][3] < l
                if not ok(k): continue
                if any(ok(kk) for kk in range(i + 2, k)): continue   # found at an earlier k: already a zone
                if len(self.zones) >= 100: self.zones.pop(0)
                self.zones.append(dict(dir=dirn, lo=l, hi=h, t0=tnow, st=0, tb=-1, ab=False))
        self.cur[q] = None

    def bar(self, t, o, h, l, c, v):
        """t = the bar's open (server time). Returns (dir, entry, stop_candle, stop_swing or None) or None"""
        m = self.ltf
        for q, hm in enumerate(self.htfs):
            kq = self.key(t, hm)
            if self.cur[q] is not None and self.cur[q][0] != kq: self.close_htf(q, t)
            if self.cur[q] is None: self.cur[q] = [kq, o, h, l, c]
            else:
                cq = self.cur[q]; cq[2] = max(cq[2], h); cq[3] = min(cq[3], l); cq[4] = c
        # pivots (2, 2) confirmed on this bar: the bar 2 back
        self.lows.append(l); self.highs.append(h); self.vols.append(v); self.n += 1
        j = self.n - 1
        if j >= 4:
            p = j - 2
            if self.lows[p] <= min(self.lows[p - 2:p + 3]): self.pl.append(self.lows[p]); del self.pl[:-200]
            if self.highs[p] >= max(self.highs[p - 2:p + 3]): self.ph.append(self.highs[p]); del self.ph[:-200]
        vavg = sum(self.vols[-self.volN - 1:-1]) / self.volN if self.n > self.volN else None
        rng = h - l; body = abs(c - o); sig = 0; keep = []
        for z in self.zones:
            if z['t0'] > t: keep.append(z); continue          # not usable yet (closed on this bar: from the next)
            d, lo, hi = z['dir'], z['lo'], z['hi']
            dead = (d == 1 and c < lo) or (d == -1 and c > hi)
            if z['st'] == 0:
                if (t - z['t0']).total_seconds() > self.maxMs: continue
                if dead: continue
                if l <= hi and h >= lo: z['st'] = 1; z['tb'] = j
                else: keep.append(z); continue
            if j - z['tb'] >= self.epi or dead: continue
            if rng <= 0: keep.append(z); continue
            if z['ab'] and ((d == 1 and c > o) or (d == -1 and c < o)) and body >= self.aggBody * rng:
                sig = d; continue                              # traded: the zone is used
            if vavg is not None and l <= hi and h >= lo:
                wick = (min(o, c) - l) if d == 1 else (h - max(o, c))
                if v > self.volMult * vavg and body < self.absBody * rng and wick >= self.absWick * rng: z['ab'] = True
            keep.append(z)
        self.zones = keep
        tc = t + dt.timedelta(minutes=m)
        for q, hm in enumerate(self.htfs):
            if self.cur[q] is not None and self.key(tc, hm) != self.cur[q][0]: self.close_htf(q, tc)
        if not sig: return None
        sc = l - self.buf if sig == 1 else h + self.buf
        sw = None
        for pv in reversed(self.pl if sig == 1 else self.ph):
            if (sig == 1 and pv < c) or (sig == -1 and pv > c): sw = pv - self.buf if sig == 1 else pv + self.buf; break
        return sig, c, sc, sw


def check():
    B = {tf: T.bars(tf) for tf in set(T.MIN)}
    R = pickle.load(open(HERE + '/ob_results.pkl', 'rb'))
    tot_bad = 0
    for ltf, htf in T.PAIRS:
        L = B[ltf]; eng = OB(T.MIN[ltf], [T.MIN[htf]])
        mine = set()
        srv = [T.SRV[j] for j in L['j0']]
        for i in range(len(L['o'])):
            r = eng.bar(srv[i], L['o'][i], L['h'][i], L['l'][i], L['c'][i], L['v'][i])
            if r is None: continue
            sig, e, sc, sw = r; tE = L['t1'][i]
            if tE < T.TEST0: continue
            for sn, stp in (('candle', sc), ('swing', sw)):
                if stp is None or abs(e - stp) < 0.05: continue
                mine.add((sn, sig, tE, round(e, 6), round(abs(e - stp), 6)))
        ref = set((x['stop'], x['dir'], x['t'], round(x['entry'], 6), round(x['risk'], 6)) for x in R if x['ltf'] == ltf and x['htf'] == htf)
        miss = ref - mine; extra = mine - ref
        # extras are allowed only where ob_test dropped a trade for an unknown outcome (the end of the data)
        ext_bad = [x for x in extra if x[2] < T.IST[-1] - dt.timedelta(days=1)]
        print('%s/%s: reference trades %d, stream %d, missing %d, extra %d (before the last day: %d)' % (ltf, htf, len(ref), len(mine), len(miss), len(extra), len(ext_bad)))
        for x in sorted(miss)[:3]: print('   missing', x)
        for x in sorted(ext_bad)[:3]: print('   extra', x)
        tot_bad += len(miss) + len(ext_bad)
    print('OB STREAM vs ob_test:', 'IDENTICAL' if tot_bad == 0 else 'DIFFERENCES %d' % tot_bad)


if __name__ == '__main__':
    check()
