"""Sniper research engine (numba): the EA's SnBar step by step (= the Pine ENGINE, verified 149 / 149 on the simulator) on every bar of a
timeframe cache, plus optional research parameters (absorption types, minimum absorption count, aggression delta %, generic per-bar filter
slots on an extra feature matrix X, confirmation bar). Returns the signals with their entry / stop and diagnostic features.
P layout: see PNAMES / DEF."""
import numpy as np, numba as nb

PNAMES = ['aggRatio', 'absSens', 'deltaSrc', 'volLen', 'atrLen', 'absLen', 'divMin', 'wickPct', 'aggRelV', 'aggBody', 'mode', 'expiry',
          'zone', 'bandMode', 'bandMult', 'zoneAtr', 'maxDist', 'cvd', 'cvdLen', 'slopeOn', 'slopeLen', 'cool', 'entry', 'offset', 'slMode',
          'slAtr', 'slPts', 'slPct', 'slBuf', 'swingLen', 'minRisk', 'maxRisk',
          # research extensions (defaults = the original behaviour)
          'absMask', 'minAbsN', 'aggDeltaPct', 'confirm', 'maxRelVAgg', 'minZoneN', 'minBarsArm', 'maxAggRatio',
          'f1col', 'f1mode', 'f1a', 'f1b', 'f2col', 'f2mode', 'f2a', 'f2b', 'f3col', 'f3mode', 'f3a', 'f3b', 'sideReq', 'ctx', 'vside']
DEF = dict(aggRatio=2.2, absSens=1.2, deltaSrc=0, volLen=20, atrLen=14, absLen=5, divMin=15.0, wickPct=40.0, aggRelV=1.0, aggBody=50.0, mode=0,
           expiry=10, zone=1, bandMode=0, bandMult=1.0, zoneAtr=0.75, maxDist=2.5, cvd=1, cvdLen=3, slopeOn=0, slopeLen=5, cool=3, entry=0,
           offset=0.0, slMode=0, slAtr=1.5, slPts=5.0, slPct=0.25, slBuf=0.15, swingLen=5, minRisk=0.3, maxRisk=4.0,
           absMask=15, minAbsN=1, aggDeltaPct=0.0, confirm=0, maxRelVAgg=0.0, minZoneN=1, minBarsArm=0, maxAggRatio=0.0,
           f1col=-1, f1mode=0, f1a=0.0, f1b=0.0, f2col=-1, f2mode=0, f2a=0.0, f2b=0.0, f3col=-1, f3mode=0, f3a=0.0, f3b=0.0, sideReq=0, ctx=0, vside=1)
PI = {k: i for i, k in enumerate(PNAMES)}
FEAT = ['aggR', 'relV', 'bodyP', 'deltaPct', 'zoneWAtr', 'distAtr', 'riskAtr', 'absTypes', 'nAbs', 'barsArm', 'hasZ', 'atr', 'cvdDir', 'rollDir',
        'intra', 'bandPos', 'clPos']


def params(**kw):
    p = dict(DEF); p.update(kw)
    bad = set(kw) - set(DEF)
    assert not bad, bad
    return np.array([float(p[k]) for k in PNAMES])


@nb.njit(cache=True)
def _fslot(X, i, col, mode, a, b, d):
    """generic filter slot: mode 1 sign (long X > a, short X < -a), 2 band (a <= X <= b for both), 3 pair (long X[col] >= a, short X[col+1] >= a),
    4 direction-signed band (a <= d * X <= b)"""
    if mode == 0 or col < 0:
        return True
    x = X[i, col]
    if x != x:
        return False
    if mode == 1:
        return x > a if d > 0 else x < -a
    if mode == 2:
        return x >= a and x <= b
    if mode == 3:
        y = x if d > 0 else X[i, col + 1]
        return y >= a
    if mode == 4:
        return d * x >= a and d * x <= b
    if mode == 5:
        return x < -a if d > 0 else x > a
    return True


@nb.njit(cache=True)
def kernel(o, h, l, c, v, ibv, isv, icnt, vw, vsd, newa, X, P, mintick, LS, LR):
    n = len(c)
    aggRatio = P[0]; absSens = P[1]; deltaSrc = int(P[2]); volLen = int(P[3]); atrLen = int(P[4]); absLen = int(P[5]); divMin = P[6]
    wickPct = P[7]; aggRelV = P[8]; aggBody = P[9]; mode = int(P[10]); expiry = int(P[11]); zone = int(P[12]); bandMode = int(P[13])
    bandMult = P[14]; zoneAtr = P[15]; maxDist = P[16]; cvd = int(P[17]); cvdLen = int(P[18]); slopeOn = int(P[19]); slopeLen = int(P[20])
    cool = int(P[21]); entry = int(P[22]); offset = P[23]; slMode = int(P[24]); slAtr = P[25]; slPts = P[26]; slPct = P[27]; slBuf = P[28]
    swingLen = int(P[29]); minRisk = P[30]; maxRisk = P[31]
    absMask = int(P[32]); minAbsN = int(P[33]); aggDeltaPct = P[34]; confirm = int(P[35]); maxRelVAgg = P[36]; minZoneN = int(P[37])
    minBarsArm = int(P[38]); maxAggRatio = P[39]
    f1c = int(P[40]); f1m = int(P[41]); f1a = P[42]; f1b = P[43]; f2c = int(P[44]); f2m = int(P[45]); f2a = P[46]; f2b = P[47]
    f3c = int(P[48]); f3m = int(P[49]); f3a = P[50]; f3b = P[51]; sideReq = int(P[52]); ctx = int(P[53]); vside = int(P[54])
    dl = np.zeros(n); tv = np.zeros(n)
    out_i = np.empty(n, np.int64); out_d = np.empty(n, np.int64); out_e = np.empty(n); out_s = np.empty(n)
    nf = 17
    out_f = np.empty((n, nf))
    ns = 0
    trSum = 0.0; atrV = 0.0; trN = 0; cvdS = 0.0
    bullArm = -1; bearArm = -1; lastSig = -1
    bullLo = 0.0; bullHi = 0.0; bearLo = 0.0; bearHi = 0.0
    bullTypes = 0; bearTypes = 0; bullN = 0; bearN = 0; bullFirst = -1; bearFirst = -1
    pend = 0; pendE = 0.0; pendS = 0.0; pendBar = -1
    pendF = np.zeros(nf)
    for i in range(n):
        nb_ = i + 1
        vv = v[i]
        if i == 0:
            tr = h[i] - l[i]
        else:
            tr = max(max(h[i] - l[i], abs(h[i] - c[i - 1])), abs(l[i] - c[i - 1]))
        if trN < atrLen:
            trSum += tr; trN += 1
            if trN == atrLen:
                atrV = trSum / atrLen
        else:
            atrV = (1.0 / atrLen) * tr + (1.0 - 1.0 / atrLen) * atrV
        atrOk = trN >= atrLen
        sAtr = atrV if atrOk else 0.0
        avgOk = nb_ >= volLen
        avg = 0.0
        if avgOk:
            for j in range(volLen - 1, -1, -1):
                avg += v[i - j]
            avg /= volLen
        relV = vv / avg if (avgOk and avg > 0) else 0.0
        rng = h[i] - l[i]
        bodyP = abs(c[i] - o[i]) / rng if rng > 0 else 0.0
        clPos = (c[i] - l[i]) / rng if rng > 0 else 0.5
        loW = min(o[i], c[i]) - l[i]; upW = h[i] - max(o[i], c[i])
        intra = deltaSrc == 0 and icnt[i] >= 2
        if intra:
            buyV = ibv[i]; sellV = isv[i]
        else:
            buyV = vv * (c[i] - l[i]) / rng if rng > 0 else vv * 0.5
            sellV = vv - buyV
        totV = buyV + sellV; delta = buyV - sellV
        bullR = buyV / max(max(sellV, totV * 0.01), 0.000001); bearR = sellV / max(max(buyV, totV * 0.01), 0.000001)
        dl[i] = delta; tv[i] = totV
        cvdS = delta if newa[i] else cvdS + delta
        rollOk = nb_ >= cvdLen
        roll = 0.0
        if rollOk:
            for j in range(cvdLen - 1, -1, -1):
                roll += dl[i - j]
        bullAg = c[i] > o[i] and bullR >= aggRatio and relV >= aggRelV and bodyP * 100.0 >= aggBody
        bearAg = c[i] < o[i] and bearR >= aggRatio and relV >= aggRelV and bodyP * 100.0 >= aggBody
        winOk = nb_ >= absLen
        loL = 0.0; hiH = 0.0; winD = 0.0; winV = 0.0; winRV = 0.0
        if winOk:
            loL = l[i]; hiH = h[i]
            for j in range(1, absLen):
                loL = min(loL, l[i - j]); hiH = max(hiH, h[i - j])
            for j in range(absLen - 1, -1, -1):
                winD += dl[i - j]
            for j in range(absLen - 1, -1, -1):
                winV += tv[i - j]
            for j in range(absLen - 1, -1, -1):
                winRV += v[i - j]
        winDP = 100.0 * winD / winV if (winOk and winV > 0) else 0.0
        winRel = winRV / (avg * absLen) if (avgOk and avg > 0 and winOk) else 0.0
        backOk = nb_ > absLen
        back = c[i - absLen] if backOk else 0.0
        effort = relV >= absSens
        bt = 0; st_ = 0
        if effort and loW >= rng * wickPct / 100.0 and clPos >= 0.5:
            bt |= 1
        if intra and effort and delta < 0 and c[i] >= o[i]:
            bt |= 2
        if relV >= absSens * 1.5 and atrOk and rng <= sAtr * 0.7 and winOk and l[i] <= loL:
            bt |= 4
        if winDP <= -divMin and backOk and c[i] >= back and winRel >= 1.0:
            bt |= 8
        if effort and upW >= rng * wickPct / 100.0 and clPos <= 0.5:
            st_ |= 1
        if intra and effort and delta > 0 and c[i] <= o[i]:
            st_ |= 2
        if relV >= absSens * 1.5 and atrOk and rng <= sAtr * 0.7 and winOk and h[i] >= hiH:
            st_ |= 4
        if winDP >= divMin and backOk and c[i] <= back and winRel >= 1.0:
            st_ |= 8
        bt &= absMask; st_ &= absMask
        nbt = (bt & 1) + ((bt >> 1) & 1) + ((bt >> 2) & 1) + ((bt >> 3) & 1)
        nst = (st_ & 1) + ((st_ >> 1) & 1) + ((st_ >> 2) & 1) + ((st_ >> 3) & 1)
        bullAb = nbt >= minAbsN and nbt > 0
        bearAb = nst >= minAbsN and nst > 0
        vwap = vw[i]
        basis = vsd[i] if bandMode == 0 else vwap * 0.01
        up1 = vwap + basis * bandMult; lo1 = vwap - basis * bandMult
        zw = zoneAtr * sAtr
        tV = atrOk and l[i] <= vwap + zw and h[i] >= vwap - zw
        tU = atrOk and l[i] <= up1 + zw and h[i] >= up1 - zw
        tL = atrOk and l[i] <= lo1 + zw and h[i] >= lo1 - zw
        if ctx == 0:      # the original: longs at the VWAP / upper band #1, shorts at the VWAP / lower band #1
            bullCtx = atrOk and c[i] >= vwap - zw and (zone == 2 or tV or (zone == 1 and tU))
            bearCtx = atrOk and c[i] <= vwap + zw and (zone == 2 or tV or (zone == 1 and tL))
        elif ctx == 1:    # research: reversal at the outer band (longs at the lower band, shorts at the upper band)
            bullCtx = atrOk and tL and c[i] >= lo1 - zw
            bearCtx = atrOk and tU and c[i] <= up1 + zw
        else:             # research: absorption at the given support / resistance levels (LS / LR)
            bullCtx = atrOk and LS[i] == LS[i] and l[i] <= LS[i] + zw and h[i] >= LS[i] - zw and c[i] >= LS[i] - zw
            bearCtx = atrOk and LR[i] == LR[i] and l[i] <= LR[i] + zw and h[i] >= LR[i] - zw and c[i] <= LR[i] + zw
        dist = abs(c[i] - vwap) / sAtr if (atrOk and sAtr > 0) else 0.0
        distOk = maxDist <= 0 or dist <= maxDist
        slopeOk = nb_ > slopeLen
        slope = vwap - vw[i - slopeLen] if slopeOk else 0.0
        swOk = nb_ >= swingLen
        swLo = 0.0; swHi = 0.0
        if swOk:
            swLo = l[i]; swHi = h[i]
            for j in range(1, swingLen):
                swLo = min(swLo, l[i - j]); swHi = max(swHi, h[i - j])
        bullArmed = bullArm >= 0 and i - bullArm <= expiry
        bearArmed = bearArm >= 0 and i - bearArm <= expiry
        if bullArmed and ((ctx == 0 and atrOk and c[i] < vwap - zw) or c[i] < bullLo):
            bullArm = -1; bullArmed = False
        if bearArmed and ((ctx == 0 and atrOk and c[i] > vwap + zw) or c[i] > bearHi):
            bearArm = -1; bearArmed = False
        if bullAb and bullCtx:
            if bullArmed:
                bullLo = min(bullLo, l[i]); bullHi = max(bullHi, h[i]); bullTypes |= bt; bullN += 1
            else:
                bullLo = l[i]; bullHi = h[i]; bullTypes = bt; bullN = 1; bullFirst = i
            bullArm = i; bullArmed = True
        if bearAb and bearCtx:
            if bearArmed:
                bearLo = min(bearLo, l[i]); bearHi = max(bearHi, h[i]); bearTypes |= st_; bearN += 1
            else:
                bearLo = l[i]; bearHi = h[i]; bearTypes = st_; bearN = 1; bearFirst = i
            bearArm = i; bearArmed = True
        # a pending confirmation: the bar after the signal must close beyond the signal close
        if pend != 0:
            if (pend == 1 and c[i] > pendE) or (pend == -1 and c[i] < pendE):
                out_i[ns] = i; out_d[ns] = pend; out_e[ns] = c[i]; out_s[ns] = pendS - (pendE - c[i]) * 0.0
                for q in range(nf):
                    out_f[ns, q] = pendF[q]
                ns += 1
            pend = 0
        coolOk = lastSig < 0 or i - lastSig >= cool
        bullF = (vside == 0 or (vside == 1 and c[i] > vwap) or (vside == -1 and c[i] < vwap)) and distOk and (slopeOn == 0 or (slopeOk and slope > 0)) and (cvd == 0 or ((rollOk and roll > 0) if cvd == 1 else cvdS > 0)) and coolOk
        bearF = (vside == 0 or (vside == 1 and c[i] < vwap) or (vside == -1 and c[i] > vwap)) and distOk and (slopeOn == 0 or (slopeOk and slope < 0)) and (cvd == 0 or ((rollOk and roll < 0) if cvd == 1 else cvdS < 0)) and coolOk
        if bullF:
            bullF = _fslot(X, i, f1c, f1m, f1a, f1b, 1) and _fslot(X, i, f2c, f2m, f2a, f2b, 1) and _fslot(X, i, f3c, f3m, f3a, f3b, 1)
        if bearF:
            bearF = _fslot(X, i, f1c, f1m, f1a, f1b, -1) and _fslot(X, i, f2c, f2m, f2a, f2b, -1) and _fslot(X, i, f3c, f3m, f3a, f3b, -1)
        dpB = 100.0 * delta / totV if totV > 0 else 0.0
        if aggDeltaPct > 0:
            bullAg = bullAg and dpB >= aggDeltaPct
            bearAg = bearAg and -dpB >= aggDeltaPct
        if maxRelVAgg > 0:
            bullAg = bullAg and relV <= maxRelVAgg
            bearAg = bearAg and relV <= maxRelVAgg
        if maxAggRatio > 0:
            bullAg = bullAg and bullR <= maxAggRatio
            bearAg = bearAg and bearR <= maxAggRatio
        bullZ = bullArmed and bullN >= minZoneN and (i - bullFirst) >= minBarsArm
        bearZ = bearArmed and bearN >= minZoneN and (i - bearFirst) >= minBarsArm
        if mode == 1:
            buy = bullF and bullAg
        elif mode == 2:
            buy = bullF and bullZ and c[i] > bullHi and c[i] > o[i]
        else:
            buy = bullF and bullZ and bullAg
        if mode == 1:
            sell = bearF and (not buy) and bearAg
        elif mode == 2:
            sell = bearF and (not buy) and bearZ and c[i] < bearLo and c[i] < o[i]
        else:
            sell = bearF and (not buy) and bearZ and bearAg
        if sideReq != 0:      # research: only one direction (1 long, -1 short)
            if sideReq == 1:
                sell = False
            else:
                buy = False
        if not buy and not sell:
            continue
        sd = 1 if buy else -1
        hasZ = bullArmed if sd == 1 else bearArmed
        zExt = bullLo if sd == 1 else bearHi
        if entry == 1:
            base = (h[i] + l[i]) / 2.0
        elif entry == 2:
            base = min(c[i], vwap) if sd == 1 else max(c[i], vwap)
        else:
            base = c[i]
        ent = base - sd * offset
        strOk = hasZ or swOk
        if sd == 1:
            sStr = (min(zExt, l[i]) if hasZ else swLo) - slBuf * sAtr
        else:
            sStr = (max(zExt, h[i]) if hasZ else swHi) + slBuf * sAtr
        if slMode == 1:
            risk = sAtr * slAtr
        elif slMode == 2:
            risk = slPts
        elif slMode == 3:
            risk = ent * slPct / 100.0
        else:
            risk = sd * (ent - sStr)
        if slMode == 0:
            risk = max(minRisk * sAtr, min(maxRisk * sAtr, risk if strOk else minRisk * sAtr))
        if not (risk > 0):
            risk = max(sAtr * 0.5, mintick * 10)
        stp = ent - sd * risk
        lastSig = i
        if sd == 1:
            ztyp = bullTypes; zn = bullN; zfirst = bullFirst
            bullArm = -1
        else:
            ztyp = bearTypes; zn = bearN; zfirst = bearFirst
            bearArm = -1
        fv = np.empty(nf)
        fv[0] = bullR if sd == 1 else bearR
        fv[1] = relV; fv[2] = bodyP; fv[3] = sd * dpB
        fv[4] = ((bullHi - bullLo) if sd == 1 else (bearHi - bearLo)) / sAtr if (hasZ and sAtr > 0) else np.nan
        fv[5] = sd * (c[i] - vwap) / sAtr if sAtr > 0 else np.nan
        fv[6] = risk / sAtr if sAtr > 0 else np.nan
        fv[7] = ztyp if hasZ else 0; fv[8] = zn if hasZ else 0; fv[9] = (i - zfirst) if hasZ else -1
        fv[10] = 1.0 if hasZ else 0.0; fv[11] = sAtr; fv[12] = sd * cvdS; fv[13] = sd * roll
        fv[14] = 1.0 if intra else 0.0
        fv[15] = sd * (c[i] - vwap) / vsd[i] if vsd[i] > 0 else np.nan
        fv[16] = clPos if sd == 1 else 1.0 - clPos
        if confirm > 0:
            pend = sd; pendE = c[i]; pendS = stp; pendBar = i
            for q in range(nf):
                pendF[q] = fv[q]
            continue
        out_i[ns] = i; out_d[ns] = sd; out_e[ns] = ent; out_s[ns] = stp
        for q in range(nf):
            out_f[ns, q] = fv[q]
        ns += 1
    return out_i[:ns], out_d[:ns], out_e[:ns], out_s[:ns], out_f[:ns]


_CACHE = {}


def load(tf):
    if tf not in _CACHE:
        _CACHE[tf] = dict(np.load('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr/cache_%d.npz' % tf))
    return _CACHE[tf]


_LV = {}


def levels(tf, kind):
    """support / resistance arrays known at each bar: pd = the previous server day's low / high, sx = the session's low / high before this
    bar, pw = the previous week's low / high"""
    key = (tf, kind)
    if key not in _LV:
        b = load(tf); n = len(b['c']); l, h, t = b['l'], b['h'], b['t']
        LS = np.full(n, np.nan); LR = np.full(n, np.nan)
        if kind in ('pd', 'pw'):
            k = t // 86400 if kind == 'pd' else (t + 3 * 86400) // (7 * 86400)
            st = np.r_[0, np.nonzero(np.diff(k))[0] + 1]; en = np.r_[st[1:], n]
            lo = np.minimum.reduceat(l, st); hi = np.maximum.reduceat(h, st)
            for g in range(1, len(st)):
                LS[st[g]:en[g]] = lo[g - 1]; LR[st[g]:en[g]] = hi[g - 1]
        elif kind == 'sx':
            k = t // 86400
            st = np.r_[0, np.nonzero(np.diff(k))[0] + 1]; en = np.r_[st[1:], n]
            for a, z in zip(st, en):
                if z - a > 1:
                    LS[a + 1:z] = np.minimum.accumulate(l[a:z])[:-1]; LR[a + 1:z] = np.maximum.accumulate(h[a:z])[:-1]
        _LV[key] = (LS, LR)
    return _LV[key]


def run(tf, P, X=None, lv='pd'):
    b = load(tf)
    if X is None:
        X = np.zeros((len(b['c']), 1))
    LS, LR = levels(tf, lv) if int(P[PI['ctx']]) == 2 else (np.full(1, np.nan), np.full(1, np.nan))
    if len(LS) == 1:
        LS = np.full(len(b['c']), np.nan); LR = LS
    return kernel(b['o'], b['h'], b['l'], b['c'], b['v'], b['ibv'], b['isv'], b['icnt'], b['vwap'], b['vwsd'], b['newa'], X, P, 0.01, LS, LR)
