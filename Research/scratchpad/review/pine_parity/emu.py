"""Literal emulation of shared_engine.pine (Pine series/na semantics) on the CSV bars, compared with ref.run().
vwap = CSV VWAP, newAnchor = newDay = ref's daystart, atr = ref's rma (same inputs the reference uses)."""
import sys, math, datetime
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/build'); import ref
from ref import eprep, rma, rtick

na = None
def isna(x): return x is None
def gt(a, b): return a is not None and b is not None and a > b
def ge(a, b): return a is not None and b is not None and a >= b
def lt(a, b): return a is not None and b is not None and a < b
def le(a, b): return a is not None and b is not None and a <= b
def sub(a, b): return None if a is None or b is None else a - b
def mul(a, b): return None if a is None or b is None else a * b
def pmax(a, b): return None if a is None or b is None else max(a, b)
def pmin(a, b): return None if a is None or b is None else min(a, b)

def emu(sym, opts=None):
    p = dict(ref.IN); p.update(opts or {})
    P = eprep(sym); R = P['rows']; n = len(R); mt = P['mt']
    O = [r['o'] for r in R]; H = [r['h'] for r in R]; L = [r['l'] for r in R]; C = [r['c'] for r in R]; V = [r['vwap'] for r in R]
    T = [datetime.datetime.strptime(r['t'], '%Y-%m-%d %H:%M') for r in R]
    ATR = rma(P['tr'], p['atrLen'])
    w = ref.weights(sym) if p['noChase'] else None
    exitK = p['exitAt']; exitR = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R'])[exitK - 1]
    def hist(arr, i, k): return arr[i - k] if i - k >= 0 else None
    def highest(arr, i, ln, off):
        j0 = i - off - ln + 1; j1 = i - off
        if j0 < 0: return None
        return max(arr[j0:j1 + 1])
    def lowest(arr, i, ln, off):
        j0 = i - off - ln + 1; j1 = i - off
        if j0 < 0: return None
        return min(arr[j0:j1 + 1])
    absd = [None] + [abs(C[j] - C[j - 1]) for j in range(1, n)]
    def msum(i, ln):
        j0 = i - ln + 1
        if j0 < 0 or any(absd[j] is None for j in range(j0, i + 1)): return None
        return sum(absd[j0:i + 1])
    vwBars = 0; sessN = 0; sw = s1 = s2 = 0.0
    dayFills = 0; dayRiskR = 0.0; lossDirBlk = 0; bullN = bearN = 0; prevNet = na; sesO = sesH = sesL = pdH = pdL = na
    st = 0; armBar = fillBar = lastExit = lastFill = na; lastDir = 0
    lim = stp = stp0 = trRisk = t1 = t2 = t3 = t4 = tF = na; tpHit = 0; trHalf = False; trGhost = False
    trades = []; cur = None
    for i in range(n):
        newAnchor = P['daystart'][i]; newDay = newAnchor
        if newAnchor:
            sw = s1 = s2 = 0.0; vwBars = 0
            if i > 0: sessN += 1
        else: vwBars += 1
        if w is not None:
            tp_ = (H[i] + L[i] + C[i]) / 3; sw += w[i]; s1 += w[i] * tp_; s2 += w[i] * tp_ * tp_
        vwap = V[i]
        vwSd = math.sqrt(max(s2 / sw - (s1 / sw) ** 2, 0.0)) if (w is not None and sw > 0) else 0.0
        atr = ATR[i]
        sL = p['structLen']; bL = p['brkLen']
        priorHigh = highest(H, i, sL, 1); priorLow = lowest(L, i, sL, 1)
        sigHigh = highest(H, i, bL, 1); sigLow = lowest(L, i, bL, 1)
        el = min(p['entryLen'], sL); entHigh = highest(H, i, el, 1); entLow = lowest(L, i, el, 1)
        swingLow = lowest(L, i, p['stopLen'], 0); swingHigh = highest(H, i, p['stopLen'], 0)
        high, low, close, open_ = H[i], L[i], C[i], O[i]
        rng = high - low; body = abs(close - open_); bodyMid = (open_ + close) / 2.0
        momMove = sub(close, hist(C, i, p['momLen']))
        erDen = msum(i, p['momLen'])
        cmoMin = p['cmoMin']
        erUp = cmoMin <= 0 or (gt(erDen, 0) and ge(momMove / erDen if erDen else None, cmoMin / 100.0))
        erDn = cmoMin <= 0 or (gt(erDen, 0) and ge(-momMove / erDen if erDen and momMove is not None else None, cmoMin / 100.0))
        sb = p['slopeBars']
        vwSlope = sub(vwap, hist(V, i, sb)) if (sb > 0 and vwBars >= sb) else na
        slopeUp = isna(vwSlope) or vwSlope > 0; slopeDn = isna(vwSlope) or vwSlope < 0
        sgSlope = na if sb <= 0 else (sub(vwap, hist(V, i, sb)) if p['slopeCross'] else vwSlope)
        sigUp = isna(sgSlope) or sgSlope > 0; sigDn = isna(sgSlope) or sgSlope < 0
        bigCandle = rng > 0 and ge(rng, mul(p['dispAtr'], atr)) and body / rng * 100.0 >= p['dispBodyPct'] - 1e-7
        bigImp = rng > 0 and ge(rng, mul(p['dispAtr'], atr)) and body / rng * 100.0 >= p['impBodyPct'] - 1e-7
        closeHi = rng > 0 and (high - close) / rng * 100.0 <= p['dispClosePct'] + 1e-7
        closeLo = rng > 0 and (close - low) / rng * 100.0 <= p['dispClosePct'] + 1e-7
        bullImp = close > open_ and gt(high, priorHigh) and bigImp and closeHi and slopeUp
        bearImp = close < open_ and lt(low, priorLow) and bigImp and closeLo and slopeDn
        utc = T[i] - datetime.timedelta(hours=5, minutes=30)
        setupOk = vwBars >= p['minOpenBars'] and not (p['skipSunday'] and utc.weekday() == 6)
        mA = p['momAtr']
        bullBase = p['allowLong'] and setupOk and close > open_ and bigCandle and closeHi and sigUp and (not p['vwapFilter'] or gt(close, vwap)) and (mA <= 0 or ge(momMove, mul(mA, atr))) and erUp
        bearBase = p['allowShort'] and setupOk and close < open_ and bigCandle and closeLo and sigDn and (not p['vwapFilter'] or lt(close, vwap)) and (mA <= 0 or ge(None if momMove is None else -momMove, mul(mA, atr))) and erDn
        momB = sub(close, hist(C, i, bL)); erDenB = msum(i, bL)
        deepL = p['deepOn'] and p['allowLong'] and setupOk and close > open_ and bigCandle and closeHi and sigUp and gt(close, vwap) and gt(close, sigHigh) and ge(momB, mul(mA, atr)) and gt(erDenB, 0) and momB / erDenB >= cmoMin / 100.0 and ge(sub(priorHigh, close), mul(p['deepFar'], atr))
        deepS = p['deepOn'] and p['allowShort'] and setupOk and close < open_ and bigCandle and closeLo and sigDn and lt(close, vwap) and lt(close, sigLow) and ge(None if momB is None else -momB, mul(mA, atr)) and gt(erDenB, 0) and -momB / erDenB >= cmoMin / 100.0 and ge(sub(close, priorLow), mul(p['deepFar'], atr))
        if newDay:
            dayFills = 0; dayRiskR = 0.0; lossDirBlk = 0
            if i > 0: prevNet = bullN - bearN
            bullN = bearN = 0; pdH = sesH; pdL = sesL; sesH = high; sesL = low; sesO = open_
        else:
            sesH = high if isna(sesH) else max(sesH, high); sesL = low if isna(sesL) else min(sesL, low)
        bn = p['biasNet']; hs = p['halfStopOn']
        halfL = hs and bullN == 0 and not isna(prevNet) and prevNet <= -bn
        halfS = hs and bearN == 0 and not isna(prevNet) and prevNet >= bn
        if p['halfStrict'] and not isna(prevNet):
            halfL = halfL and (prevNet <= -5 or (prevNet + bullN - bearN <= -1 and bearN >= 1))
            halfS = halfS and (prevNet >= 5 or (prevNet + bullN - bearN >= 1 and bullN >= 1))
        if p['halfOpenOut'] and not isna(pdH):
            halfL = halfL or (hs and bullN == 0 and sesO < pdL)
            halfS = halfS or (hs and bearN == 0 and sesO > pdH)
        if bullImp: bullN += 1
        if bearImp: bearN += 1
        # step 1
        if abs(st) == 2 and gt(i, fillBar):
            isL = st == 2; d = 1.0 if isL else -1.0
            stopHit = low <= stp + mt * 0.001 if isL else high >= stp - mt * 0.001
            tgtHit = high >= tF - mt * 0.001 if isL else low <= tF + mt * 0.001
            reached = 3 if (high >= t3 if isL else low <= t3) else 2 if (high >= t2 if isL else low <= t2) else 1 if (high >= t1 if isL else low <= t1) else 0
            prevHit = tpHit; tpHit = max(tpHit, reached)
            if stopHit or tgtHit:
                win = not stopHit
                res = exitR if win else (-1.0 if stp == stp0 else d * (stp - lim) / trRisk)
                if not trGhost:
                    dayRiskR += res
                    lossDirBlk = (1 if isL else -1) if res < 0 else 0 if res > 0 else lossDirBlk
                lastExit = i; st = 0; cur.update(exit=i, res=res)
            elif tpHit > prevHit:
                ns = stp
                if p['mv1On'] and tpHit >= 1: ns = max(ns, lim + p['mv1R'] * trRisk) if isL else min(ns, lim - p['mv1R'] * trRisk)
                if p['mv2On'] and tpHit >= 2: ns = max(ns, lim + p['mv2R'] * trRisk) if isL else min(ns, lim - p['mv2R'] * trRisk)
                if p['mv3On'] and tpHit >= 3: ns = max(ns, lim + p['mv3R'] * trRisk) if isL else min(ns, lim - p['mv3R'] * trRisk)
                if ns != stp: stp = ns
        # step 2
        if abs(st) == 1 and gt(i, armBar):
            isL = st == 1
            touched = True if p['entryMode'] == 'market' else (low <= lim + mt * 0.001 if isL else high >= lim - mt * 0.001)
            if touched and dayFills < p['maxFills']:
                st = 2 if isL else -2; fillBar = i; lastFill = i; lastDir = 1 if isL else -1; tpHit = 0; dayFills += 1
                cur = dict(dir=lastDir, arm=armBar, fill=i, entry=lim, stop=stp, exit=None, res=None, half=trHalf, ghost=trGhost); trades.append(cur)
                if (low <= stp + mt * 0.001 if isL else high >= stp - mt * 0.001):
                    if not trGhost:
                        dayRiskR += -1.0 if p['fillBarStopR'] else 0.0
                        lossDirBlk = 1 if isL else -1
                    lastExit = i; st = 0; cur.update(exit=i, res=-1.0)
            elif i - armBar >= p['retestBars']:
                st = 0
        # step 3
        cooled = isna(lastExit) or i - lastExit >= max(p['cooldownBars'], 1)
        dayOpen = p['dayStopR'] <= 0 or dayRiskR > -p['dayStopR']
        legN = 0 if isna(lastFill) else i - lastFill
        legOn = p['legReset'] and abs(st) != 2 and legN > 0 and legN < sL
        brkHigh = sigHigh; brkLow = sigLow
        if legOn:
            legHigh = hist(H, i, 1); legLow = hist(L, i, 1)
            for j in range(1, legN + 1):
                legHigh = pmax(legHigh, hist(H, i, j)); legLow = pmin(legLow, hist(L, i, j))
            if lastDir == 1: brkHigh = legHigh
            else: brkLow = legLow
        bullDisp = (bullBase and gt(close, brkHigh)) or deepL
        bearDisp = (bearBase and lt(close, brkLow)) or deepS
        if p['lossBlock'] and lossDirBlk == 1: bullDisp = False
        if p['lossBlock'] and lossDirBlk == -1: bearDisp = False
        tod = T[i].hour * 100 + T[i].minute; a0, b0 = p['hoursSess']
        dayOk = not p['dayOn'] or p['days'][T[i].weekday()]
        hourOk = not p['hoursOn'] or ((a0 <= tod < b0) if a0 < b0 else (tod >= a0 or tod < b0))
        canArm = dayOk and hourOk and abs(st) != 2 and cooled and dayFills < p['maxFills'] and dayOpen and gt(atr, 0)
        keepArm = p['rearmKeep'] and ((st == 1 and bullDisp) or (st == -1 and bearDisp))
        if canArm and (bullDisp or bearDisp) and not keepArm:
            isL = bool(bullDisp); d = 1.0 if isL else -1.0
            em = p['entryMode']
            entry = (max(bodyMid, entHigh) if isL else min(bodyMid, entLow)) if em == 'model' else (close - d * p['entryPct'] / 100.0 * rng) if em == 'pct' else close
            half = p['stopMode'] == 'atr' and (halfL if isL else halfS)
            cStop = entry - d * p['stopAtr'] * atr
            hStop = min(entry - p['halfStopAtr'] * atr, low) if isL else max(entry + p['halfStopAtr'] * atr, high)
            sStop = swingLow - p['stopBufAtr'] * atr if isL else swingHigh + p['stopBufAtr'] * atr
            stop = (hStop if half else cStop) if p['stopMode'] == 'atr' else (max(sStop, cStop) if isL else min(sStop, cStop))
            risk = d * (entry - stop)
            if risk >= mt and rtick(stop, mt) != rtick(entry, mt):
                z = d * (close - vwap) / vwSd if (p['noChase'] and vwSd > 0 and vwBars >= 3 and sessN >= 1) else na
                ghost = p['noChase'] and not isna(z) and z > p['noChaseSig']
                st = 1 if isL else -1; armBar = i; lim = entry; stp = stop; stp0 = stop; trRisk = risk; trHalf = half; trGhost = ghost
                t1 = lim + d * p['tp1R'] * risk; t2 = lim + d * p['tp2R'] * risk; t3 = lim + d * p['tp3R'] * risk; t4 = lim + d * p['tp4R'] * risk
                tF = (t1, t2, t3, t4)[exitK - 1]
    return trades

if __name__ == '__main__':
    SY = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
    key = lambda x: (x['dir'], x['arm'], x['fill'], x['exit'], round(x['entry'], 9), round(x['stop'], 9), None if x['res'] is None else round(x['res'], 9), x['half'], x['ghost'])
    CASES = [('defaults', {}),
             ('deepOn', dict(deepOn=True)), ('halfStrict', dict(halfStrict=True)), ('lossBlock', dict(lossBlock=True)),
             ('moves', dict(mv1On=True, mv1R=0.0, mv2On=True, mv2R=0.6, mv3On=True, mv3R=1.0)), ('exitTP2', dict(exitAt=2)),
             ('market', dict(entryMode='market')), ('pct30', dict(entryMode='pct', entryPct=30.0)), ('swing', dict(stopMode='swing')),
             ('days MTW', dict(dayOn=True, days=(True, True, True, False, False, False, False))),
             ('hours 1330-2100', dict(hoursOn=True, hoursSess=(1330, 2100))), ('hours 2200-0300', dict(hoursOn=True, hoursSess=(2200, 300))),
             ('noChase(skip first sess)', dict(noChase=True, _skipFirstSess=True)), ('rearm new', dict(rearmKeep=False)),
             ('dayStop2 fillbar', dict(dayStopR=2.0, fillBarStopR=True)), ('slopeCross off', dict(slopeCross=False)),
             ('minOpen3 cool3', dict(minOpenBars=3, cooldownBars=3)), ('legReset off', dict(legReset=False)),
             ('fast warmup', dict(atrLen=3, structLen=4, brkLen=2, momLen=2, stopLen=2, entryLen=2, slopeBars=1))]
    only = sys.argv[1:]
    for name, o in CASES:
        if only and name not in only: continue
        bad = 0; tot = 0
        for s in SY:
            a = [key(x) for x in ref.run(s, o)]; b = [key(x) for x in emu(s, o)]
            tot += len(a)
            if a != b:
                bad += 1
                for k, (u, v) in enumerate(zip(a, b)):
                    if u != v: print('   ', s, 'first diff', k, 'ref', u, 'pine', v); break
                else: print('   ', s, 'len', len(a), len(b))
        print(f'{name:26s} ref trades {tot:5d}  instruments differing: {bad}', flush=True)
