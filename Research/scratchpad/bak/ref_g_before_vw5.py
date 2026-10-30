"""Python reference of the SHARED ENGINE block of Auction_Retest_Model.pine / Auction_Retest_Strategy.pine (v3).
Every engine input of the Pine scripts is an option here (same names, same defaults). Bar times in the CSVs are IST, so the
day/hours filters use IST like the scripts' default time zone (Asia/Kolkata). run(sym, opts) -> trades of the engine
(dict dir, arm, fill, exit, entry, stop, res, half, ghost); ghost (no-chase) trades are returned with ghost=True."""
import sys, math, datetime
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit'); sys.path.insert(0, S + '/hunt3/data')
from engine import prepare as eprep, rma, rtick

IN = dict(
    # SIGNAL MODEL
    structLen=10, brkLen=6, entryLen=6, retestBars=5, dispAtr=0.8, dispBodyPct=55.0, dispClosePct=25.0, momLen=10, momAtr=0.85,
    cmoMin=20.0, rearmKeep=True, stopMode='atr', stopAtr=1.8, stopLen=6, stopBufAtr=0.22,
    halfStopOn=True, halfStopAtr=0.9, biasNet=3, impBodyPct=50.0, halfOpenOut=True, halfStrict=False, halfCap=False,
    cooldownBars=1, maxFills=5, dayStopR=0.0, fillBarStopR=False, legReset=True, atrLen=14, vwapFilter=True, slopeBars=3,
    slopeCross=True, minOpenBars=0, skipSunday=True, deepOn=False, deepFar=2.0, allowLong=True, allowShort=True,
    # ENTRY PRICE
    entryMode='model', entryPct=50.0,
    # TARGETS AND EXIT
    tp1R=0.6, tp2R=1.0, tp3R=1.5, tp4R=2.0, exitAt=4, mv1On=False, mv1R=0.0, mv2On=False, mv2R=0.6, mv3On=False, mv3R=1.0,
    # ACCURACY FILTERS
    noChase=False, noChaseSig=2.4, lossBlock=False, chopOn=False, chopMax=12.0, emaOn=False, emaMax=1.65, minVwOn=False, minVwAtr=1.0, maxVwOn=False, maxVwDist=3.0, maxVwUnit='atr',
    # DAYS AND HOURS (IST)
    dayOn=False, days=(True, True, True, True, True, True, True), hoursOn=False, hoursSess=(600, 2300),
    # KILL ZONES (IST minutes; Asia, London, New York, London close) and the shift in hours
    kzOn=False, kz=(True, True, True, True), kzShift=0)
_W = {}
def weights(sym):
    """per-bar volume weights backed out of the CSV VWAP (TradingView uses the real volume; the CSVs have none)."""
    if sym not in _W:
        sys.path.insert(0, S + '/research/orderflow'); import of
        _W[sym] = of.weights(sym)[1]
    return _W[sym]

def run(sym, opts=None):
    p = dict(IN); p.update(opts or {})
    P = eprep(sym); mt = P['mt']
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; n = len(O)
    T = P['T']   # IST datetimes of the bar opens
    atr = rma(P['tr'], p['atrLen'])
    w = P['W'] if (p['noChase'] or p.get('needW')) else None
    exitR = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R'])[p['exitAt'] - 1]
    E = 1e-7
    # VWAP period state (the CSV VWAP is the session VWAP; only bars-since-reset and the sigma sums are tracked here)
    vwBars = 0; sw = s1 = s2 = 0.0; nSess = 0
    # day / counter state
    dayFills = 0; dayRiskR = 0.0; lossDirBlk = 0
    bullN = bearN = 0; prevNet = None; sesO = sesH = sesL = pdH = pdL = None
    # trade state
    st = 0; armBar = fillBar = lastExit = lastFill = None; lastDir = 0
    lim = stp = stp0 = trRisk = None; t = [None] * 4; tF = None; tpHit = 0; trHalf = False; trGhost = False; trVwd = trVwdA = None
    trades = []; cur = None; bestPx = None
    # optional filters: VWAP crosses this VWAP period; 1-hour (UTC) candles built from the bars and their EMA20 (hE[0..3] = last 4 completed hours)
    vxSide = vxN = 0; hK = hC = None; hNum = 0; hSum = 0.0; hE = [None] * 4; hA = 2.0 / 21.0
    EP = datetime.datetime(1970, 1, 1)
    for i in range(n):
        newAnchor = P['daystart'][i]; newDay = newAnchor
        if newAnchor: vwBars = 0; sw = s1 = s2 = 0.0; nSess = nSess + 1 if i > 0 else 0
        else: vwBars += 1
        if w is not None:
            tp_ = (H[i] + L[i] + C[i]) / 3; sw += w[i]; s1 += w[i] * tp_; s2 += w[i] * tp_ * tp_
        vwSd = math.sqrt(max(s2 / sw - (s1 / sw) ** 2, 0.0)) if w is not None and sw > 0 else None
        if newDay:
            dayFills = 0; dayRiskR = 0.0; lossDirBlk = 0
            if i > 0: prevNet = bullN - bearN
            bullN = bearN = 0
            pdH, pdL = sesH, sesL; sesH, sesL, sesO = H[i], L[i], O[i]
        else:
            sesH = H[i] if sesH is None else max(sesH, H[i]); sesL = L[i] if sesL is None else min(sesL, L[i])
        A_ = atr[i]
        if newAnchor: vxSide = 0; vxN = 0
        vxDev = (C[i] - V[i]) / A_ if (A_ is not None and A_ > 0) else 0.0
        vxZ = 1 if vxDev > 0.2 else -1 if vxDev < -0.2 else 0
        if vxZ != 0:
            if vxSide != 0 and vxZ != vxSide: vxN += 1
            vxSide = vxZ
        vxRate = 100.0 * vxN / (vwBars + 1)
        hKey = int((T[i] - datetime.timedelta(hours=5, minutes=30) - EP).total_seconds() // 3600)
        if hK is not None and hKey != hK:
            hNum += 1
            if hNum <= 20:
                hSum += hC; e_ = hSum / 20.0 if hNum == 20 else None
            else:
                e_ = hA * hC + (1.0 - hA) * hE[0]
            hE = [e_, hE[0], hE[1], hE[2]]
        hK = hKey; hC = C[i]
        emaSpd = abs(hE[0] - hE[3]) / A_ if (hE[0] is not None and hE[3] is not None and A_ is not None and A_ > 0) else None
        warm = i >= max(p['structLen'], p['brkLen'], p['entryLen'], p['momLen'], p['slopeBars'], p['stopLen']) + 1 and atr[i] is not None
        A = atr[i] if atr[i] is not None else 0.0
        # ── 1. live trade (bars after the fill): stop first, then the final target, else stop moves ──
        if abs(st) == 2 and i > fillBar:
            isL = st == 2; d = 1 if isL else -1
            stopHit = L[i] <= stp + mt * 0.001 if isL else H[i] >= stp - mt * 0.001
            tgtHit = H[i] >= tF - mt * 0.001 if isL else L[i] <= tF + mt * 0.001
            reached = 3 if (H[i] >= t[2] if isL else L[i] <= t[2]) else 2 if (H[i] >= t[1] if isL else L[i] <= t[1]) else 1 if (H[i] >= t[0] if isL else L[i] <= t[0]) else 0
            prevHit = tpHit; tpHit = max(tpHit, reached)
            if not stopHit: bestPx = max(bestPx, H[i]) if isL else min(bestPx, L[i])
            if stopHit or tgtHit:
                win = not stopHit
                res = exitR if win else (-1.0 if stp == stp0 else d * (stp - lim) / trRisk)
                if not trGhost:
                    dayRiskR += res
                    if res < 0: lossDirBlk = d
                    elif res > 0: lossDirBlk = 0
                lastExit = i; st = 0; cur.update(exit=i, res=res, best=bestPx, stpX=stp)
            elif reached > prevHit:
                ns = stp
                if p['mv1On'] and reached >= 1: ns = max(ns, lim + p['mv1R'] * trRisk) if isL else min(ns, lim - p['mv1R'] * trRisk)
                if p['mv2On'] and reached >= 2: ns = max(ns, lim + p['mv2R'] * trRisk) if isL else min(ns, lim - p['mv2R'] * trRisk)
                if p['mv3On'] and reached >= 3: ns = max(ns, lim + p['mv3R'] * trRisk) if isL else min(ns, lim - p['mv3R'] * trRisk)
                stp = ns
        # ── 2. armed setup: fill (limit touch, or the next bar for market entries) or expiry ──
        if abs(st) == 1 and i > armBar:
            isL = st == 1; d = 1 if isL else -1
            touched = True if p['entryMode'] == 'market' else (L[i] <= lim + mt * 0.001 if isL else H[i] >= lim - mt * 0.001)
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; lastFill = i; lastDir = d; tpHit = 0; dayFills += 1
                cur = dict(dir=d, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, half=trHalf, ghost=trGhost, vwd=trVwd, vwdA=trVwdA); trades.append(cur)
                bestPx = lim
                if (L[i] <= stp + mt * 0.001 if isL else H[i] >= stp - mt * 0.001):
                    if not trGhost:
                        dayRiskR += -1.0 if p['fillBarStopR'] else 0.0
                        lossDirBlk = d
                    lastExit = i; st = 0; cur.update(exit=i, res=-1.0, best=lim, stpX=stp)
            elif i - armBar >= p['retestBars']:
                st = 0
        if not warm:
            continue
        # ── signal conditions ──
        priorHigh = max(H[i - p['structLen']:i]); priorLow = min(L[i - p['structLen']:i])
        sigHigh = max(H[i - p['brkLen']:i]); sigLow = min(L[i - p['brkLen']:i])
        el = min(p['entryLen'], p['structLen']); entHigh = max(H[i - el:i]); entLow = min(L[i - el:i])
        swingLow = min(L[i - p['stopLen'] + 1:i + 1]); swingHigh = max(H[i - p['stopLen'] + 1:i + 1])
        rng = H[i] - L[i]; body = abs(C[i] - O[i]); bodyMid = (O[i] + C[i]) / 2
        momMove = C[i] - C[i - p['momLen']]
        erDen = sum(abs(C[j] - C[j - 1]) for j in range(i - p['momLen'] + 1, i + 1))
        erUp = p['cmoMin'] <= 0 or (erDen > 0 and momMove / erDen >= p['cmoMin'] / 100.0)
        erDn = p['cmoMin'] <= 0 or (erDen > 0 and -momMove / erDen >= p['cmoMin'] / 100.0)
        vwSlope = V[i] - V[i - p['slopeBars']] if p['slopeBars'] > 0 and vwBars >= p['slopeBars'] else None
        slopeUp = vwSlope is None or vwSlope > 0; slopeDn = vwSlope is None or vwSlope < 0
        sgSlope = None if p['slopeBars'] <= 0 else (V[i] - V[i - p['slopeBars']] if p['slopeCross'] else vwSlope)
        sigUp = sgSlope is None or sgSlope > 0; sigDn = sgSlope is None or sgSlope < 0
        bigCandle = rng > 0 and rng >= p['dispAtr'] * A and body / rng * 100 >= p['dispBodyPct'] - E
        bigImp = rng > 0 and rng >= p['dispAtr'] * A and body / rng * 100 >= p['impBodyPct'] - E
        closeHi = rng > 0 and (H[i] - C[i]) / rng * 100 <= p['dispClosePct'] + E
        closeLo = rng > 0 and (C[i] - L[i]) / rng * 100 <= p['dispClosePct'] + E
        bullImp = C[i] > O[i] and H[i] > priorHigh and bigImp and closeHi and slopeUp
        bearImp = C[i] < O[i] and L[i] < priorLow and bigImp and closeLo and slopeDn
        utc = T[i] - datetime.timedelta(hours=5, minutes=30)
        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and utc.weekday() == 6)
        bullBase = p['allowLong'] and setupOk and C[i] > O[i] and bigCandle and closeHi and sigUp and (not p['vwapFilter'] or C[i] > V[i]) and (p['momAtr'] <= 0 or momMove >= p['momAtr'] * A) and erUp
        bearBase = p['allowShort'] and setupOk and C[i] < O[i] and bigCandle and closeLo and sigDn and (not p['vwapFilter'] or C[i] < V[i]) and (p['momAtr'] <= 0 or -momMove >= p['momAtr'] * A) and erDn
        deepL = deepS = False
        if p['deepOn']:
            momB = C[i] - C[i - p['brkLen']]; erDenB = sum(abs(C[j] - C[j - 1]) for j in range(i - p['brkLen'] + 1, i + 1))
            deepL = p['allowLong'] and setupOk and C[i] > O[i] and bigCandle and closeHi and sigUp and C[i] > V[i] and C[i] > sigHigh and momB >= p['momAtr'] * A and erDenB > 0 and momB / erDenB >= p['cmoMin'] / 100.0 and priorHigh - C[i] >= p['deepFar'] * A
            deepS = p['allowShort'] and setupOk and C[i] < O[i] and bigCandle and closeLo and sigDn and C[i] < V[i] and C[i] < sigLow and -momB >= p['momAtr'] * A and erDenB > 0 and -momB / erDenB >= p['cmoMin'] / 100.0 and C[i] - priorLow >= p['deepFar'] * A
        # half stop: first impulse of the session against a strongly opposite previous session (or a gap outside its range)
        halfL = p['halfStopOn'] and bullN == 0 and prevNet is not None and prevNet <= -p['biasNet']
        halfS = p['halfStopOn'] and bearN == 0 and prevNet is not None and prevNet >= p['biasNet']
        if p['halfStrict'] and prevNet is not None:
            halfL = halfL and (prevNet <= -5 or (prevNet + bullN - bearN <= -1 and bearN >= 1))
            halfS = halfS and (prevNet >= 5 or (prevNet + bullN - bearN >= 1 and bullN >= 1))
        if p['halfOpenOut'] and pdH is not None:
            halfL = halfL or (p['halfStopOn'] and bullN == 0 and sesO < pdL)
            halfS = halfS or (p['halfStopOn'] and bearN == 0 and sesO > pdH)
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        # ── 3. arm ──
        cooled = lastExit is None or i - lastExit >= max(p['cooldownBars'], 1)
        dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']
        legN = 0 if lastFill is None else i - lastFill
        legOn = p['legReset'] and abs(st) != 2 and 0 < legN < p['structLen']
        brkHigh, brkLow = sigHigh, sigLow
        if legOn:
            if lastDir == 1: brkHigh = max(H[i - legN:i])
            else: brkLow = min(L[i - legN:i])
        bullDisp = (bullBase and C[i] > brkHigh) or deepL
        bearDisp = (bearBase and C[i] < brkLow) or deepS
        if p['lossBlock'] and lossDirBlk == 1: bullDisp = False
        if p['lossBlock'] and lossDirBlk == -1: bearDisp = False
        tod = T[i].hour * 100 + T[i].minute; a0, b0 = p['hoursSess']
        dayOk = not p['dayOn'] or p['days'][T[i].weekday()]
        hourOk = not p['hoursOn'] or ((a0 <= tod < b0) if a0 < b0 else (tod >= a0 or tod < b0))
        km = T[i].hour * 60 + T[i].minute; sh = p['kzShift'] * 60
        def inkz(a, b):
            ks, ke = (a + sh + 1440) % 1440, (b + sh + 1440) % 1440
            return (ks <= km < ke) if ks < ke else (km >= ks or km < ke)
        kzOk = not p['kzOn'] or any(on and inkz(a, b) for on, (a, b) in zip(p['kz'], ((330, 570), (690, 870), (990, 1170), (1170, 1290))))
        canArm = dayOk and hourOk and kzOk and abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and A > 0
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bullDisp; d = 1 if isL else -1
            entry = (max(bodyMid, entHigh) if isL else min(bodyMid, entLow)) if p['entryMode'] == 'model' else \
                    (C[i] - d * p['entryPct'] / 100.0 * rng) if p['entryMode'] == 'pct' else C[i]
            half = p['stopMode'] == 'atr' and (halfL if isL else halfS)
            cStop = entry - d * p['stopAtr'] * A
            hStop = min(entry - p['halfStopAtr'] * A, L[i]) if isL else max(entry + p['halfStopAtr'] * A, H[i])
            if p['halfCap']: hStop = max(hStop, cStop) if isL else min(hStop, cStop)
            sStop = swingLow - p['stopBufAtr'] * A if isL else swingHigh + p['stopBufAtr'] * A
            stop = (hStop if half else cStop) if p['stopMode'] == 'atr' else (max(sStop, cStop) if isL else min(sStop, cStop))
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                z = d * (C[i] - V[i]) / vwSd if (p['noChase'] and vwSd and vwBars >= 3 and nSess >= 1) else None   # like Pine / the EA: not in the first (partial) VWAP period
                ghost = p['noChase'] and z is not None and z > p['noChaseSig']
                chopNo = p['chopOn'] and vxRate > p['chopMax']
                emaNo = p['emaOn'] and emaSpd is not None and emaSpd > p['emaMax']
                nearNo = p['minVwOn'] and d * (C[i] - V[i]) < p['minVwAtr'] * A
                # signal close too far from the VWAP (either side), in ATR or in price
                vwd = abs(C[i] - V[i])
                farNo = p['maxVwOn'] and vwd > (p['maxVwDist'] if p['maxVwUnit'] == 'price' else p['maxVwDist'] * A)
                ghost = ghost or chopNo or emaNo or nearNo or farNo
                st = d; armBar = i; lim = entry; stp = stop; stp0 = stop; trRisk = risk; trHalf = half; trGhost = ghost; trVwd = vwd; trVwdA = vwd / A
                t = [lim + d * p['tp1R'] * risk, lim + d * p['tp2R'] * risk, lim + d * p['tp3R'] * risk, lim + d * p['tp4R'] * risk]
                tF = t[p['exitAt'] - 1]
    return trades

def shown(sym, opts=None):
    return [x for x in run(sym, opts) if not x['ghost']]

