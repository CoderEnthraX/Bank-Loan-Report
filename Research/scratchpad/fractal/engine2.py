"""Fractal breakout grid v2: the exact engine with the optional settings (all off = engine.sim exactly). Rules: SPEC2.md.
sim2(O, H, L, C, T, kk, ph, off, sl, tp, be, sv, allow, wk, dayid, kexp, trA, trD, tExit, emode, maxDay, pm, out)
  allow[i]  a breakout on chart bar i may open a trade (hours, days, trend, weekend filters); a breakout that is not allowed is skipped and
            uses up the buy stop
  wk[i]     an open trade closes at the open of bar i (weekend close)
  dayid[i]  day number of bar i (in the filters' time zone) for maxDay (most entries per day; 0 = no limit)
  kexp      a waiting buy stop expires after this many fractal-TF candles (0 = never): at the first chart bar of TF candle kAct + kexp
  trA, trD  trailing stop: once the highest price since the fill is >= F (1 + trA %), SL = max(SL, highest x (1 - trD %)); trD 0 = off
  tExit     close at the open of the first bar that opens >= entry bar's open time + tExit seconds (0 = off)
  emode     0 buy stop (path), 1 candle close at / above E after a close below E since the buy stop was set (fill at the close)
Exit reasons: 1 TP, 2 SL, 3 BE, 4 SALV, 5 TRAIL, 6 TIME, 7 WEEKEND."""
import numpy as np, numba as nb
import engine as EN


@nb.njit(cache=True)
def sim2(O, H, L, C, T, kk, ph, off, sl, tp, be, sv, allow, wk, dayid, kexp, trA, trD, tExit, emode, maxDay, pm, out):
    n = len(O)
    lvlOn = False; E = 0.0; lvlH = 0.0; kAct = 0; armed = False
    pos = False; F = 0.0; SLp = 0.0; TPp = 0.0; BEl = 0.0; SVl = 0.0; beOn = False; svOn = False; trOn = False; hi = 0.0; eT = 0
    beAct = be > 0.0; svAct = sv > 0.0; trAct = trD > 0.0
    prevC = np.nan; nt = 0; ei = -1; ek = 0; eH = 0.0; dCnt = 0; dPrev = -1
    for i in range(n):
        if dayid[i] != dPrev:
            dCnt = 0; dPrev = dayid[i]
        lvlNew = False
        if i == 0 or kk[i] != kk[i - 1]:
            v = ph[kk[i]]
            if not np.isnan(v):
                lvlOn = True; lvlH = v; E = v * (1.0 + off / 100.0); lvlNew = True; kAct = kk[i]; armed = False
        if lvlOn and kexp > 0 and kk[i] - kAct >= kexp:
            lvlOn = False
        o = O[i]; h = H[i]; l = L[i]; c = C[i]
        # 1. the open: trailing update, TP / SL gaps, time / weekend exit, BE / salvage at the open, then a gap entry
        if pos:
            if trAct and hi >= F * (1.0 + trA / 100.0):
                tl = hi * (1.0 - trD / 100.0)
                if tl > SLp:
                    SLp = tl; trOn = True
            xr = 0
            if o >= TPp:
                xr = 4 if svOn else 1
            elif o <= SLp:
                xr = 5 if trOn else (3 if beOn else 2)
            elif tExit > 0 and T[i] >= eT + tExit:
                xr = 6
            elif wk[i]:
                xr = 7
            if xr > 0:
                out[nt, 0] = ei; out[nt, 1] = F; out[nt, 2] = i; out[nt, 3] = o; out[nt, 4] = xr
                out[nt, 5] = 1.0 if beOn else 0.0; out[nt, 6] = 1.0 if svOn else 0.0; out[nt, 7] = ek; out[nt, 8] = eH
                nt += 1; pos = False
            else:
                if beAct and not beOn and not svOn and o >= BEl:
                    beOn = True
                    if F > SLp:
                        SLp = F
                elif svAct and not svOn and not beOn and o <= SVl:
                    svOn = True; TPp = F
                if o > hi:
                    hi = o
        if emode == 0 and lvlOn and prevC < E and o >= E:
            if not pos and allow[i] and (maxDay <= 0 or dCnt < maxDay):
                pos = True; F = o; SLp = F * (1.0 - sl / 100.0); TPp = F * (1.0 + tp / 100.0)
                BEl = F * (1.0 + be / 100.0); SVl = F * (1.0 - sv / 100.0); beOn = False; svOn = False; trOn = False; hi = o
                ei = i; ek = 1; eH = lvlH; eT = T[i]; dCnt += 1
            lvlOn = False
        # 2. the path
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
                    if emode == 0 and lvlOn and x < E and E <= y and E < best:
                        best = E; ev = 3
                    if ev == 0:
                        break
                    if ev == 1:
                        out[nt, 0] = ei; out[nt, 1] = F; out[nt, 2] = i; out[nt, 3] = TPp; out[nt, 4] = 4 if svOn else 1
                        out[nt, 5] = 1.0 if beOn else 0.0; out[nt, 6] = 1.0 if svOn else 0.0; out[nt, 7] = ek; out[nt, 8] = eH
                        nt += 1; pos = False
                    elif ev == 2:
                        beOn = True
                        if F > SLp:
                            SLp = F
                    else:
                        if not pos and allow[i] and (maxDay <= 0 or dCnt < maxDay):
                            pos = True; F = E; SLp = F * (1.0 - sl / 100.0); TPp = F * (1.0 + tp / 100.0)
                            BEl = F * (1.0 + be / 100.0); SVl = F * (1.0 - sv / 100.0); beOn = False; svOn = False; trOn = False; hi = E
                            ei = i; ek = 0; eH = lvlH; eT = T[i]; dCnt += 1
                        lvlOn = False
                if pos and y > hi:
                    hi = y
            elif y < x:
                if pos and trAct and hi >= F * (1.0 + trA / 100.0):
                    tl = hi * (1.0 - trD / 100.0)
                    if tl > SLp:
                        SLp = tl; trOn = True
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
                        out[nt, 0] = ei; out[nt, 1] = F; out[nt, 2] = i; out[nt, 3] = SLp; out[nt, 4] = 5 if trOn else (3 if beOn else 2)
                        out[nt, 5] = 1.0 if beOn else 0.0; out[nt, 6] = 1.0 if svOn else 0.0; out[nt, 7] = ek; out[nt, 8] = eH
                        nt += 1; pos = False
                    else:
                        svOn = True; TPp = F
        # 3. candle-close entry (emode 1): armed by a close below E since the buy stop was set
        if emode == 1 and lvlOn:
            if armed and c >= E:
                if not pos and allow[i] and (maxDay <= 0 or dCnt < maxDay):
                    pos = True; F = c; SLp = F * (1.0 - sl / 100.0); TPp = F * (1.0 + tp / 100.0)
                    BEl = F * (1.0 + be / 100.0); SVl = F * (1.0 - sv / 100.0); beOn = False; svOn = False; trOn = False; hi = c
                    ei = i; ek = 2; eH = lvlH; eT = T[i]; dCnt += 1
                lvlOn = False
            elif c < E:
                armed = True
        prevC = c
    return nt


def masks_default(n):
    return np.ones(n, np.bool_), np.zeros(n, np.bool_), np.zeros(n, np.int64)


def run2(B, ctf, ftf, right, left, off, sl, tp, be, sv, allow=None, wk=None, dayid=None, kexp=0, trA=0.0, trD=0.0, tExit=0, emode=0, maxDay=0, pm=0, T=None):
    t, O, H, L, C = EN.chart(B, ctf)
    kk = (np.searchsorted(B[ftf + '_t'], t, side='right') - 1).astype(np.int64)
    ph = EN.pivots(B[ftf + '_H'], int(left), int(right))
    a0, w0, d0 = masks_default(len(O))
    out = np.zeros((len(O) // 2 + 10, 9))
    nt = sim2(O, H, L, C, (t if T is None else T).astype(np.int64), kk, ph, float(off), float(sl), float(tp), float(be), float(sv), a0 if allow is None else allow, w0 if wk is None else wk,
              d0 if dayid is None else dayid, int(kexp), float(trA), float(trD), int(tExit), int(emode), int(maxDay), int(pm), out)
    return out[:nt]
