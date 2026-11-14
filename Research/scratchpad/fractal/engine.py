"""Fractal breakout grid: exact reference engine (numba). Rules: SPEC.md.
Bars of any chart timeframe (M1 for the research, M5 / M15 for the TradingView-chart twin), each processed along the path
open -> (high or low, whichever is nearer the open; a tie goes to the low first) -> the other -> close."""
import numpy as np, numba as nb

TF_SEC = {'M1': 60, 'M5': 300, 'M15': 900, 'H1': 3600, 'H4': 14400, 'D1': 86400}
REASON = {1: 'TP', 2: 'SL', 3: 'BE', 4: 'SALV'}


@nb.njit(cache=True)
def pivots(Hh, left, right):
    """ph[k] = high of the swing-high candle p = k - 1 - right (strictly above the `left` candles before it and the `right` candles
    after it), active from fractal-timeframe candle k (it is confirmed when candle p + right closes); NaN where none."""
    n = len(Hh); ph = np.full(n, np.nan)
    for p in range(left, n - right - 1):
        v = Hh[p]; ok = True
        for i in range(1, left + 1):
            if Hh[p - i] >= v:
                ok = False; break
        if ok:
            for j in range(1, right + 1):
                if Hh[p + j] >= v:
                    ok = False; break
        if ok:
            ph[p + right + 1] = v
    return ph


@nb.njit(cache=True)
def sim(O, H, L, C, kk, ph, off, sl, tp, be, sv, out, pm=0):
    """One strategy over the chart bars. kk[i] = fractal-timeframe candle of chart bar i. Writes trades into out (rows:
    entry bar, entry price, exit bar, exit price, reason 1 TP / 2 SL / 3 BE / 4 SALV, BE moved, salvage moved, entry kind 0 path / 1 gap,
    level (the swing high)) and returns the number of trades. A trade still open at the end is not written."""
    n = len(O)
    lvlOn = False; E = 0.0; lvlH = 0.0
    pos = False; F = 0.0; SLp = 0.0; TPp = 0.0; BEl = 0.0; SVl = 0.0; beOn = False; svOn = False
    beAct = be > 0.0; svAct = sv > 0.0
    prevC = np.nan; nt = 0; ei = -1; ek = 0; eH = 0.0
    for i in range(n):
        lvlNew = False
        if i == 0 or kk[i] != kk[i - 1]:
            v = ph[kk[i]]
            if not np.isnan(v):
                lvlOn = True; lvlH = v; E = v * (1.0 + off / 100.0); lvlNew = True
        o = O[i]; h = H[i]; l = L[i]; c = C[i]
        # 1. the open (a jump from the previous close): exits first, then an entry
        if pos:
            xr = 0
            if o >= TPp:
                xr = 4 if svOn else 1
            elif o <= SLp:
                xr = 3 if beOn else 2
            if xr > 0:
                out[nt, 0] = ei; out[nt, 1] = F; out[nt, 2] = i; out[nt, 3] = o; out[nt, 4] = xr
                out[nt, 5] = 1.0 if beOn else 0.0; out[nt, 6] = 1.0 if svOn else 0.0; out[nt, 7] = ek; out[nt, 8] = eH
                nt += 1; pos = False
            else:
                if beAct and not beOn and not svOn and o >= BEl:
                    beOn = True; SLp = F
                elif svAct and not svOn and not beOn and o <= SVl:
                    svOn = True; TPp = F
        if lvlOn and prevC < E and o >= E:
            if not pos:
                pos = True; F = o; SLp = F * (1.0 - sl / 100.0); TPp = F * (1.0 + tp / 100.0)
                BEl = F * (1.0 + be / 100.0); SVl = F * (1.0 - sv / 100.0); beOn = False; svOn = False; ei = i; ek = 1; eH = lvlH
            lvlOn = False
        # 2. the path inside the bar
        if (pm == 0 and (h - o) < (o - l)) or pm == 2:
            a = h; b = l
        else:
            a = l; b = h
        for sg in range(3):
            if sg == 0:
                x = o; y = a
            elif sg == 1:
                x = a; y = b
            else:
                x = b; y = c
            if y > x:
                while True:
                    best = np.inf; ev = 0
                    if pos:
                        if x < TPp and TPp <= y:
                            best = TPp; ev = 1
                        if beAct and not beOn and not svOn and x < BEl and BEl <= y and BEl < best:
                            best = BEl; ev = 2
                    if lvlOn and x < E and E <= y and E < best:
                        best = E; ev = 3
                    if ev == 0:
                        break
                    if ev == 1:
                        out[nt, 0] = ei; out[nt, 1] = F; out[nt, 2] = i; out[nt, 3] = TPp; out[nt, 4] = 4 if svOn else 1
                        out[nt, 5] = 1.0 if beOn else 0.0; out[nt, 6] = 1.0 if svOn else 0.0; out[nt, 7] = ek; out[nt, 8] = eH
                        nt += 1; pos = False
                    elif ev == 2:
                        beOn = True; SLp = F
                    else:
                        if not pos:
                            pos = True; F = E; SLp = F * (1.0 - sl / 100.0); TPp = F * (1.0 + tp / 100.0)
                            BEl = F * (1.0 + be / 100.0); SVl = F * (1.0 - sv / 100.0); beOn = False; svOn = False; ei = i; ek = 0; eH = lvlH
                        lvlOn = False
            elif y < x:
                while True:
                    best = -np.inf; ev = 0
                    if pos:
                        if y <= SLp and SLp < x:
                            best = SLp; ev = 1
                        if svAct and not svOn and not beOn and y <= SVl and SVl < x and SVl > best:
                            best = SVl; ev = 2
                    if ev == 0:
                        break
                    if ev == 1:
                        out[nt, 0] = ei; out[nt, 1] = F; out[nt, 2] = i; out[nt, 3] = SLp; out[nt, 4] = 3 if beOn else 2
                        out[nt, 5] = 1.0 if beOn else 0.0; out[nt, 6] = 1.0 if svOn else 0.0; out[nt, 7] = ek; out[nt, 8] = eH
                        nt += 1; pos = False
                    else:
                        svOn = True; TPp = F
        prevC = c
    return nt


def load():
    S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
    return dict(np.load(S + '/fractal/bars.npz'))


def chart(B, ctf):
    """chart bars of timeframe ctf (M1 or an aggregate) as arrays t, O, H, L, C"""
    if ctf == 'M1':
        return B['t'], B['O'], B['H'], B['L'], B['C']
    return B[ctf + '_t'], B[ctf + '_O'], B[ctf + '_H'], B[ctf + '_L'], B[ctf + '_C']


def run(B, ctf, ftf, right, left, off, sl, tp, be, sv, pm=0):
    """trades (n x 9 array) of one strategy: chart timeframe ctf, fractal timeframe ftf"""
    t, O, H, L, C = chart(B, ctf)
    assert TF_SEC[ctf] <= TF_SEC[ftf], 'the fractal timeframe must not be below the chart timeframe'
    kk = (np.searchsorted(B[ftf + '_t'], t, side='right') - 1).astype(np.int64)
    ph = pivots(B[ftf + '_H'], int(left), int(right))
    out = np.zeros((len(O) // 2 + 10, 9))
    nt = sim(O, H, L, C, kk, ph, float(off), float(sl), float(tp), float(be), float(sv), out, int(pm))
    return out[:nt]


def stats(tr, slpct, cost=0.23, t=None, y0=None, y1=None):
    """per-trade % and R after a round-trip cost in price units; optional year window by the entry time (t = chart bar times)"""
    if len(tr) and t is not None and (y0 or y1):
        import datetime as dt
        yr = np.array([dt.datetime.fromtimestamp(int(t[int(i)]), dt.timezone.utc).year for i in tr[:, 0]])
        m = np.ones(len(tr), bool)
        if y0: m &= yr >= y0
        if y1: m &= yr <= y1
        tr = tr[m]
    n = len(tr)
    if n == 0:
        return dict(n=0, win=0.0, pct=0.0, R=0.0, pf=0.0, ddR=0.0, streak=0, avgR=0.0)
    F = tr[:, 1]; X = tr[:, 3]; pnl = X - F - cost
    pct = pnl / F * 100.0; R = pnl / (F * slpct / 100.0)
    cum = np.cumsum(R); dd = np.max(np.maximum.accumulate(np.r_[0.0, cum])[1:] - cum)
    gw = R[R > 0].sum(); gl = -R[R < 0].sum()
    st = mx = 0
    for r in R:
        st = st + 1 if r < 0 else 0; mx = max(mx, st)
    return dict(n=n, win=100.0 * np.mean(pnl > 0), pct=pct.sum(), R=R.sum(), pf=gw / gl if gl > 0 else np.inf, ddR=max(dd, 0.0), streak=mx, avgR=R.mean())
